"""Unit tests for orchestration planning, execution, hybrid routing, synthesis.

All tests are offline and deterministic: handlers are fakes, no network,
no models, no sleeps beyond sub-second timeout checks.
"""

from __future__ import annotations

import time

import pytest

from orchestration.execution.cancellation import (
    CancellationToken,
    CancelledError,
)
from orchestration.execution.execution_engine import ExecutionEngine
from orchestration.execution.sandbox import Sandbox, SandboxPolicy, SandboxViolation
from orchestration.execution.sequential_executor import SequentialExecutor
from orchestration.execution.parallel_executor import ParallelExecutor
from orchestration.execution.timeout_manager import run_with_timeout
from orchestration.hybrid.fallback_manager import FallbackExhausted, FallbackManager
from orchestration.hybrid.route_policy import Route, RoutePolicy
from orchestration.hybrid.route_selector import RouteSelector
from orchestration.planning.dag_builder import DAGBuilder, DAGBuildError
from orchestration.planning.dependency_resolver import (
    critical_path_length,
    execution_waves,
    resolve_order,
    validate,
)
from orchestration.planning.planner import Planner, PlanningError
from orchestration.planning.task_graph import CycleError, TaskGraph, TaskNode
from orchestration.synthesis.conflict_resolver import ConflictResolver
from orchestration.synthesis.output_validator import OutputValidator


# ── TaskGraph ────────────────────────────────────────────────────────────────
class TestTaskGraph:
    def test_topological_order_respects_dependencies(self):
        graph = TaskGraph()
        graph.add_task(TaskNode(id="a", description="fetch"))
        graph.add_task(TaskNode(id="b", description="clean", depends_on=["a"]))
        graph.add_task(TaskNode(id="c", description="analyze", depends_on=["b"]))
        assert resolve_order(graph) == ["a", "b", "c"]

    def test_duplicate_id_rejected(self):
        graph = TaskGraph()
        graph.add_task(TaskNode(id="x", description="one"))
        with pytest.raises(ValueError):
            graph.add_task(TaskNode(id="x", description="two"))

    def test_unknown_dependency_rejected(self):
        graph = TaskGraph()
        with pytest.raises(Exception):
            graph.add_task(TaskNode(id="a", description="x", depends_on=["ghost"]))

    def test_cycle_detected_via_topological_order(self):
        graph = TaskGraph()
        graph.add_task(TaskNode(id="a", description="a"))
        graph.add_task(TaskNode(id="b", description="b", depends_on=["a"]))
        graph.add_task(TaskNode(id="c", description="c", depends_on=["b", "a"]))
        assert resolve_order(graph) == ["a", "b", "c"]

    def test_cycle_raises_when_edges_close_a_loop(self):
        bad = TaskGraph()
        bad.add_task(TaskNode(id="p", description="p"))
        bad.add_task(TaskNode(id="q", description="q", depends_on=["p"]))
        # Simulate an out-of-band mutation that closes the loop p -> q -> p.
        bad.get("p").depends_on.append("q")
        with pytest.raises(CycleError):
            bad.topological_order()

    def test_ready_tasks_and_leaves(self):
        graph = TaskGraph()
        graph.add_task(TaskNode(id="a", description="a"))
        graph.add_task(TaskNode(id="b", description="b", depends_on=["a"]))
        assert graph.ready_tasks([]) == ["a"]
        assert graph.ready_tasks(["a"]) == ["b"]
        assert graph.leaves() == ["b"]


# ── Dependency resolution ────────────────────────────────────────────────────
class TestDependencyResolver:
    def _diamond(self) -> TaskGraph:
        builder = DAGBuilder()
        return builder.build(
            [
                {"id": "root", "description": "root"},
                {"id": "left", "description": "left", "depends_on": ["root"]},
                {"id": "right", "description": "right", "depends_on": ["root"]},
                {
                    "id": "join",
                    "description": "join",
                    "depends_on": ["left", "right"],
                },
            ]
        )

    def test_waves_parallelize_independent_tasks(self):
        waves = execution_waves(self._diamond())
        assert waves[0] == ["root"]
        assert sorted(waves[1]) == ["left", "right"]
        assert waves[2] == ["join"]

    def test_validate_ok_and_reports_errors(self):
        ok, errors = validate(self._diamond())
        assert ok and errors == []

    def test_critical_path_length(self):
        cost = {"root": 1.0, "left": 2.0, "right": 3.0, "join": 1.0}
        assert critical_path_length(self._diamond(), cost) == 5.0


# ── DAGBuilder / Planner ─────────────────────────────────────────────────────
class TestDAGBuilderAndPlanner:
    def test_auto_ids_from_description(self):
        graph = DAGBuilder().build([{"description": "Fetch the data"}])
        assert list(graph.tasks)[0].id == "fetch-the-data"

    def test_sequential_fallback_chains_tasks(self):
        graph = DAGBuilder(sequential_fallback=True).build(
            [{"description": "one"}, {"description": "two"}, {"description": "three"}]
        )
        assert graph.get("two").depends_on == ["one"]

    def test_invalid_route_hint_rejected(self):
        with pytest.raises(DAGBuildError):
            DAGBuilder().build(
                [{"description": "x", "route_hint": "quantum"}]
            )

    def test_planner_single_strategy(self):
        plan = Planner().plan("Do the thing", strategy="single")
        assert plan.task_count == 1
        assert plan.metadata["strategy"] == "single"

    def test_planner_llm_strategy_with_fake_decomposer(self):
        fake = lambda goal: (  # noqa: E731
            '[{"id": "a", "description": "first"},'
            ' {"id": "b", "description": "second", "depends_on": ["a"]}]'
        )
        plan = Planner(decomposer=fake).plan("goal", strategy="llm")
        assert plan.task_count == 2
        assert plan.waves == [["a"], ["b"]]

    def test_planner_llm_without_decomposer_raises(self):
        with pytest.raises(PlanningError):
            Planner().plan("goal", strategy="llm")

    def test_planner_rejects_invalid_json(self):
        planner = Planner(decomposer=lambda goal: "not json")
        with pytest.raises(PlanningError):
            planner.plan("goal", strategy="llm")


# ── Execution ────────────────────────────────────────────────────────────────
def _echo_handler(task_id: str, description: str, context: dict):
    return f"done:{task_id}"


def _fail_on(task_id: str):
    def handler(task_id_: str, description: str, context: dict):
        if task_id_ == task_id:
            raise RuntimeError(f"boom:{task_id}")
        return f"done:{task_id_}"

    return handler


class TestExecutors:
    def _plan(self):
        return Planner().plan("linear chain", strategy="single")

    def test_sequential_success(self):
        engine = ExecutionEngine(parallel=False)
        report = engine.run(self._plan(), _echo_handler)
        assert report.all_ok and report.succeeded == 1

    def test_failure_skips_downstream(self):
        from orchestration.planning.dag_builder import DAGBuilder

        graph = DAGBuilder().build(
            [
                {"id": "a", "description": "a"},
                {"id": "b", "description": "b", "depends_on": ["a"]},
            ]
        )
        from orchestration.planning.execution_plan import new_plan

        plan = new_plan("chain", graph)
        engine = ExecutionEngine(parallel=False)
        report = engine.run(plan, _fail_on("a"))
        assert report.results["a"].status.value == "failed"
        assert report.results["b"].status.value == "skipped"

    def test_parallel_matches_sequential_results(self):
        from orchestration.planning.dag_builder import DAGBuilder
        from orchestration.planning.execution_plan import new_plan

        graph = DAGBuilder().build(
            [
                {"id": "r", "description": "r"},
                {"id": "l", "description": "l", "depends_on": ["r"]},
                {"id": "rr", "description": "rr", "depends_on": ["r"]},
            ]
        )
        plan = new_plan("fanout", graph)
        par = ExecutionEngine(parallel=True, max_workers=2).run(plan, _echo_handler)
        seq = ExecutionEngine(parallel=False).run(plan, _echo_handler)
        assert par.all_ok and seq.all_ok
        assert {k: v.output for k, v in par.results.items()} == {
            k: v.output for k, v in seq.results.items()
        }

    def test_cancellation_stops_pending_work(self):
        token = CancellationToken()
        token.cancel("user stop")
        executor = SequentialExecutor(token=token)
        results = executor.execute(self._plan(), _echo_handler)
        assert all(r.status.value == "cancelled" for r in results.values())

    def test_cancelled_token_raises(self):
        token = CancellationToken()
        with pytest.raises(CancelledError):
            token.cancel()
            token.raise_if_cancelled()


class TestSandboxAndTimeout:
    def test_deny_by_default(self):
        sandbox = Sandbox(SandboxPolicy())
        with pytest.raises(SandboxViolation):
            sandbox.guard("fs_read")

    def test_read_only_blocks_mutating_capability(self):
        policy = SandboxPolicy(allowed_capabilities={"fs_write"}, read_only=True)
        sandbox = Sandbox(policy)
        with pytest.raises(SandboxViolation):
            sandbox.guard("fs_write")

    def test_wrapped_function_clamps_output(self):
        policy = SandboxPolicy(allowed_capabilities={"list"}, max_output_items=3)
        sandbox = Sandbox(policy)
        wrapped = sandbox.wrap("list", lambda: [1, 2, 3, 4, 5])
        assert wrapped() == [1, 2, 3]

    def test_timeout_returns_fast_result(self):
        assert run_with_timeout(lambda: 42, timeout=1.0) == 42

    def test_timeout_expires(self):
        start = time.time()
        with pytest.raises(TimeoutError):
            run_with_timeout(time.sleep, args=(0.5,), timeout=0.05)
        assert time.time() - start < 0.4


# ── Hybrid routing ───────────────────────────────────────────────────────────
class TestRouting:
    def test_cloud_unavailable_defaults_to_edge(self):
        selector = RouteSelector(RoutePolicy(), cloud_available=False)
        decision = selector.select("anything", complexity=0.99)
        assert decision.route is Route.EDGE

    def test_high_complexity_routes_to_cloud_when_available(self):
        selector = RouteSelector(RoutePolicy(), cloud_available=True)
        decision = selector.select("heavy task", complexity=0.9)
        assert decision.route is Route.CLOUD

    def test_planner_hint_respected(self):
        selector = RouteSelector(RoutePolicy(), cloud_available=True)
        assert selector.select("t", hint="edge").route is Route.EDGE
        assert selector.select("t", hint="cloud").route is Route.CLOUD

    def test_fallback_first_success_wins(self):
        calls = []

        def edge(tid, desc, ctx):
            calls.append("edge")
            raise RuntimeError("edge down")

        def cloud(tid, desc, ctx):
            calls.append("cloud")
            return "cloud-result"

        manager = FallbackManager({"edge": edge, "cloud": cloud})
        output, route, attempts = manager.run("t1", "desc", {})
        assert output == "cloud-result" and route == "cloud" and attempts == 2
        assert calls == ["edge", "cloud"]

    def test_fallback_exhausted_carries_errors(self):
        def bad(route_name):
            def handler(tid, desc, ctx):
                raise RuntimeError(f"{route_name} failed")

            return handler

        manager = FallbackManager({"edge": bad("edge"), "cloud": bad("cloud")})
        with pytest.raises(FallbackExhausted) as excinfo:
            manager.run("t1", "desc", {})
        assert set(excinfo.value.errors) == {"edge", "cloud"}


# ── Synthesis ────────────────────────────────────────────────────────────────
class TestSynthesis:
    def test_validator_flags_empty_output(self):
        ok, problems = OutputValidator().validate("")
        assert not ok and problems

    def test_conflict_resolver_priority(self):
        winner, strategy = ConflictResolver().resolve(
            {"a": "from-a", "b": "from-b"}, strategy="priority", priorities=["b", "a"]
        )
        assert winner == "from-b" and strategy == "priority"

    def test_conflict_resolver_majority(self):
        winner, _ = ConflictResolver().resolve(
            {"a": "x", "b": "x", "c": "y"}, strategy="majority"
        )
        assert winner == "x"

    def test_conflict_resolver_no_candidates_is_honest_none(self):
        winner, _ = ConflictResolver().resolve({"a": None}, strategy="first")
        assert winner is None