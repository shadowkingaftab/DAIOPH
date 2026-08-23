"""Unit tests for the DAIOPH API layer (schemas, REST routes, events, WS).

Offline and deterministic: route collaborators are fakes injected through
the dependency container or constructor seams; gRPC tests assert the honest
unavailable behaviour without requiring grpcio.
"""

from __future__ import annotations

import pytest

from APIs.events.event_handlers import EventHandlerRegistry
from APIs.grpc.server import GrpcServer
from APIs.grpc.services import ChatService, GrpcNotAvailableError, MemoryService
from APIs.rest.dependencies import DependencyContainer, DependencyMissingError
from APIs.rest.routes.agents import AgentsRoute
from APIs.rest.routes.health import HealthRoute
from APIs.rest.routes.models import ModelsRoute
from APIs.schemas.base import Field, Schema, ValidationError
from APIs.schemas.chat import CHAT_SEND_SCHEMA
from APIs.websocket.connection_manager import ConnectionManager
from APIs.websocket.websocket_server import WebSocketServer, WebSocketTransportError


# ── Schemas ──────────────────────────────────────────────────────────────────
class TestSchemas:
    def test_valid_payload_passes(self):
        ok, problems = CHAT_SEND_SCHEMA.validate(
            {"message": "hello", "session_id": "s1", "route": "edge"}
        )
        assert ok and problems == []

    def test_missing_required_field_reported(self):
        ok, problems = CHAT_SEND_SCHEMA.validate({"message": "hi"})
        assert not ok and any("session_id" in p for p in problems)

    def test_wrong_type_reported(self):
        ok, problems = CHAT_SEND_SCHEMA.validate(
            {"message": 42, "session_id": "s1"}
        )
        assert not ok and any("expected str" in p for p in problems)

    def test_max_length_enforced(self):
        schema = Schema("t", [Field(name="x", type=str, max_length=5)])
        ok, problems = schema.validate({"x": "way too long"})
        assert not ok and any("exceeds" in p for p in problems)

    def test_choices_enforced(self):
        ok, problems = CHAT_SEND_SCHEMA.validate(
            {"message": "m", "session_id": "s", "route": "quantum"}
        )
        assert not ok and any("not in" in p for p in problems)

    def test_validate_or_raise_raises(self):
        with pytest.raises(ValidationError):
            CHAT_SEND_SCHEMA.validate_or_raise({})

    def test_non_dict_payload_rejected(self):
        ok, problems = CHAT_SEND_SCHEMA.validate(["not", "a", "dict"])  # type: ignore[arg-type]
        assert not ok and problems


# ── Dependency container ─────────────────────────────────────────────────────
class TestDependencyContainer:
    def test_singleton_cached(self):
        container = DependencyContainer()
        container.register("svc", lambda: {"calls": []})
        first = container.resolve("svc")
        second = container.resolve("svc")
        assert first is second

    def test_factory_not_cached(self):
        container = DependencyContainer()
        container.register("svc", lambda: object(), singleton=False)
        assert container.resolve("svc") is not container.resolve("svc")

    def test_missing_dependency_raises_clear_error(self):
        container = DependencyContainer()
        with pytest.raises(DependencyMissingError):
            container.resolve("ghost")

    def test_try_resolve_returns_default(self):
        container = DependencyContainer()
        assert container.try_resolve("ghost", default="fallback") == "fallback"

    def test_override_forces_value(self):
        container = DependencyContainer()
        container.register("svc", lambda: "real")
        container.override("svc", "fake")
        assert container.resolve("svc") == "fake"


# ── Health routes ────────────────────────────────────────────────────────────
class TestHealthRoute:
    def test_liveness_always_alive(self):
        health = HealthRoute(started_at=0.0)
        report = health.liveness()
        assert report["status"] == "alive" and report["uptime_seconds"] > 0

    def test_readiness_ready_when_checks_pass(self):
        health = HealthRoute(readiness_checks={"db": lambda: True})
        assert health.readiness()["status"] == "ready"

    def test_readiness_not_ready_when_check_fails(self):
        health = HealthRoute(readiness_checks={"db": lambda: False})
        report = health.readiness()
        assert report["status"] == "not_ready" and report["failed"] == ["db"]

    def test_readiness_reports_raising_check_honestly(self):
        def broken():
            raise RuntimeError("connection refused")

        health = HealthRoute(readiness_checks={"db": broken})
        report = health.readiness()
        assert report["status"] == "not_ready"
        assert "connection refused" in report["checks"]["db"]


# ── Agent routes ─────────────────────────────────────────────────────────────
class _FakeRuntime:
    """Duck-typed stand-in for orchestration.agents.AgentRuntime."""

    class _Registry:
        def list_ids(self):
            return ["agent-1"]

        def __len__(self):
            return 1

    def __init__(self):
        self.registry = self._Registry()

    def status(self):
        return {"agents": {"agent-1": {"runs": 0}}}

    def spawn(self, agent_cls, agent_id=None):
        return type("A", (), {"agent_id": agent_id})()

    def run(self, agent_id, task, context=None):
        return {"ok": True, "agent_id": agent_id, "output": task.upper()}


class TestAgentsRoute:
    def _route(self):
        container = DependencyContainer()
        container.register_value("agent_runtime", _FakeRuntime())
        return AgentsRoute(container)

    def test_list_agents_uses_injected_runtime(self):
        report = self._route().list_agents()
        assert report["count"] == 1 and "agent-1" in report["agents"]

    def test_invalid_payload_rejected(self):
        result = self._route().run_agent({"task": "no agent id"})
        assert result["status"] == "invalid"

    def test_unknown_agent_is_not_found(self):
        result = self._route().run_agent(
            {"agent_id": "missing", "task": "work"}
        )
        assert result["status"] == "not_found"

    def test_known_agent_runs(self):
        result = self._route().run_agent({"agent_id": "agent-1", "task": "go"})
        assert result["ok"] and result["output"] == "GO"

    def test_spawn_with_bad_role_rejected(self):
        result = self._route().spawn_agent(
            {"agent_id": "x", "role": "wizard"}
        )
        assert result["status"] == "invalid"


# ── Model routes ─────────────────────────────────────────────────────────────
class TestModelsRoute:
    def test_no_registry_reports_unavailable(self):
        report = ModelsRoute().list_models()
        assert report["status"] == "unavailable" and report["models"] == []

    def test_registry_listing_and_lookup(self):
        models = [{"model_id": "qwen2-0.5b", "quant": "q4_k_m"}]
        route = ModelsRoute(registry_fn=lambda: models)
        listing = route.list_models()
        assert listing["count"] == 1
        found = route.get_model("qwen2-0.5b")
        assert found["status"] == "ok" and found["model"]["quant"] == "q4_k_m"

    def test_get_model_not_found(self):
        route = ModelsRoute(registry_fn=lambda: [])
        assert route.get_model("nope")["status"] == "not_found"

    def test_registry_failure_surfaced(self):
        def broken():
            raise RuntimeError("registry down")

        report = ModelsRoute(registry_fn=broken).list_models()
        assert report["status"] == "error" and "registry down" in report["error"]


# ── Events ───────────────────────────────────────────────────────────────────
class TestEventHandlerRegistry:
    def test_dispatch_delivers_to_all_handlers(self):
        registry = EventHandlerRegistry()
        seen = []
        registry.subscribe("chat.message", seen.append)
        registry.subscribe("chat.message", lambda p: seen.append("second"))
        result = registry.dispatch("chat.message", {"text": "hi"})
        assert len(result["delivered"]) == 2 and len(seen) == 2

    def test_handler_failure_isolated_and_reported(self):
        registry = EventHandlerRegistry()

        def bad(payload):
            raise RuntimeError("handler exploded")

        received = []
        registry.subscribe("evt", bad)
        registry.subscribe("evt", received.append)
        result = registry.dispatch("evt", {})
        assert len(result["delivered"]) == 1
        assert "handler exploded" in result["failed"]["bad"]

    def test_unsubscribe_removes_handler(self):
        registry = EventHandlerRegistry()
        handler = lambda p: None  # noqa: E731
        registry.subscribe("evt", handler)
        registry.unsubscribe("evt", handler)
        assert registry.event_types() == []


# ── WebSocket ────────────────────────────────────────────────────────────────
class _FakeConnection:
    def __init__(self):
        self.sent = []

    def send(self, payload):
        self.sent.append(payload)


class TestConnectionManager:
    def test_register_broadcast_unregister(self):
        manager = ConnectionManager()
        conn_a, conn_b = _FakeConnection(), _FakeConnection()
        manager.register("a", conn_a)
        manager.register("b", conn_b)
        summary = manager.broadcast({"hello": True})
        assert summary == {"sent": 2, "failed": 0}
        manager.unregister("a")
        assert manager.count() == 1

    def test_duplicate_registration_rejected(self):
        manager = ConnectionManager()
        manager.register("a", _FakeConnection())
        with pytest.raises(ValueError):
            manager.register("a", _FakeConnection())

    def test_dead_connection_dropped_on_send(self):
        manager = ConnectionManager()

        class Dead:
            def send(self, payload):
                raise RuntimeError("socket closed")

        manager.register("dead", Dead())
        assert manager.send_to("dead", {}) is False
        assert not manager.is_connected("dead")


class TestWebSocketServer:
    def test_start_without_transport_raises_honestly(self):
        server = WebSocketServer()
        with pytest.raises(WebSocketTransportError):
            server.start()

    def test_message_routed_to_registered_handler(self):
        server = WebSocketServer()
        server.register_handler(
            "ping", lambda conn_id, data: {"pong": data.get("seq")}
        )
        reply = server.handle_message("c1", {"type": "ping", "data": {"seq": 7}})
        assert reply["type"] == "ping.reply" and reply["data"]["pong"] == 7

    def test_unknown_type_returns_explicit_error(self):
        server = WebSocketServer()
        reply = server.handle_message("c1", {"type": "nope"})
        assert reply["type"] == "error" and "nope" in reply["data"]["error"]

    def test_malformed_payload_rejected(self):
        server = WebSocketServer()
        reply = server.handle_message("c1", "just a string")  # type: ignore[arg-type]
        assert reply["type"] == "error"

    def test_handler_exception_becomes_error_reply(self):
        server = WebSocketServer()

        def boom(conn_id, data):
            raise RuntimeError("kaboom")

        server.register_handler("boom", boom)
        reply = server.handle_message("c1", {"type": "boom"})
        assert reply["type"] == "error" and "kaboom" in reply["data"]["error"]


# ── gRPC honest scaffold ─────────────────────────────────────────────────────
class TestGrpcScaffold:
    def test_service_methods_raise_unavailable(self):
        with pytest.raises(GrpcNotAvailableError):
            ChatService().SendMessage({})
        with pytest.raises(GrpcNotAvailableError):
            MemoryService().QueryMemory({})

    def test_server_serve_raises_when_unwired(self):
        server = GrpcServer(port=50051)
        # grpcio is intentionally absent from project dependencies; whatever
        # the environment, an unwired server must refuse to fake serving.
        with pytest.raises((GrpcNotAvailableError, NotImplementedError)):
            server.serve(wait_forever=False)

    def test_port_validation(self):
        with pytest.raises(ValueError):
            GrpcServer(port=0)