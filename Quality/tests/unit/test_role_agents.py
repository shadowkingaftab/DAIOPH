"""Unit tests for DAIOPH role agents and the agent runtime.

Offline and deterministic: LLM seams are exercised with fakes or by
asserting the honest AgentCapabilityError when no model is injected.
"""

from __future__ import annotations

import pytest

from agents.analyst import AnalystAgent
from agents.base.policy import AgentPolicy
from agents.coder import CoderAgent
from agents.executor import ExecutorAgent
from agents.planner import PlannerAgent
from agents.researcher import ResearcherAgent
from agents.supervisor import SupervisorAgent
from agents.verifier import VerifierAgent
from orchestration.agents import (
    AgentMemory,
    AgentRegistry,
    AgentRuntime,
    AgentSupervisor,
    AgentToolbelt,
    ToolBinding,
    ToolPermissionError,
    run_agent_loop,
)


class TestAgentPolicy:
    def test_defaults_are_valid(self):
        policy = AgentPolicy()
        assert policy.max_steps >= 1

    def test_invalid_budgets_rejected(self):
        with pytest.raises(ValueError):
            AgentPolicy(max_steps=0)
        with pytest.raises(ValueError):
            AgentPolicy(max_retries=-1)
        with pytest.raises(ValueError):
            AgentPolicy(timeout_seconds=0)

    def test_approval_requires_membership(self):
        with pytest.raises(ValueError):
            AgentPolicy(allowed_tools=frozenset(), require_approval=frozenset({"x"}))


class TestRoleAgentsLocalBehaviour:
    def test_planner_splits_goal_into_chained_steps(self):
        agent = PlannerAgent()
        result = agent.run("Fetch data; clean it. Then analyze.")
        assert result["ok"] and result["source"] == "local_heuristic"
        steps = result["plan"]["steps"]
        assert len(steps) == 3
        assert steps[1]["depends_on"] == [steps[0]["id"]]
        assert steps[2]["depends_on"] == [steps[1]["id"]]

    def test_analyst_summarizes_records(self):
        agent = AnalystAgent()
        data = [
            {"name": "a", "score": 1},
            {"name": "b", "score": 2},
            {"score": 3},  # 'name' missing entirely -> partial coverage
        ]
        result = agent.run("summarize", context={"data": data})
        assert result["ok"]
        summary = result
        assert summary["record_count"] == 3
        assert summary["field_coverage"]["name"] == 2
        assert summary["anomalies"]["partial_fields"]["name"] == 1

    def test_supervisor_aggregates_results(self):
        agent = SupervisorAgent()
        results = {
            "t1": {"ok": True},
            "t2": {"ok": False},
        }
        verdict = agent.run("goal", context={"results": results})
        assert verdict["goal_met"] is False
        assert verdict["failed_tasks"] == ["t2"]

    def test_verifier_passes_and_fails_on_criteria(self):
        agent = VerifierAgent()
        passing = agent.run(
            "The report includes a summary section",
            context={"criteria": ["summary", "references"]},
        )
        # Only 'summary' is present -> fail is the honest verdict.
        assert passing["verdict"] == "fail"
        full = agent.run(
            "Includes a summary and references",
            context={"criteria": ["summary", "references"]},
        )
        assert full["verdict"] == "pass"

    def test_coder_without_llm_raises_honestly(self):
        agent = CoderAgent()
        with pytest.raises(RuntimeError):
            agent.run("write a function")

    def test_coder_with_fake_llm_returns_output(self):
        agent = CoderAgent(llm=lambda prompt: "CODE:" + prompt[:12])
        result = agent.run("print hi")
        assert result["ok"] and result["source"] == "llm"
        assert result["output"].startswith("CODE:")

    def test_executor_requires_handler_or_llm(self):
        agent = ExecutorAgent()
        with pytest.raises(RuntimeError):
            agent.run("step one")
        handled = agent.run("step one", context={"execute": lambda t, c: "executed"})
        assert handled["output"] == "executed"

    def test_researcher_uses_injected_search_callable(self):
        agent = ResearcherAgent()
        findings = agent.run(
            "what is X", context={"search": lambda q, ctx: [{"doc": "x"}]}
        )
        assert findings["findings"] == [{"doc": "x"}]

    def test_empty_task_rejected(self):
        with pytest.raises(ValueError):
            PlannerAgent().run("   ")

    def test_lifecycle_and_snapshot(self):
        agent = PlannerAgent(agent_id="p1")
        agent.start()
        agent.run("do a; do b")
        snap = agent.snapshot()
        assert snap["running"] is True and snap["runs"] == 1
        agent.stop()
        agent.reset()
        assert agent.snapshot()["runs"] == 0


class TestAgentRuntime:
    def _runtime(self) -> AgentRuntime:
        runtime = AgentRuntime(timeout_seconds=5.0)
        runtime.spawn(PlannerAgent, agent_id="planner-1")
        return runtime

    def test_spawn_registers_agent(self):
        runtime = self._runtime()
        assert "planner-1" in runtime.registry.list_ids()

    def test_run_executes_local_behaviour(self):
        runtime = self._runtime()
        result = runtime.run("planner-1", "step one; step two")
        assert result["ok"] and result["agent_id"] == "planner-1"

    def test_duplicate_registration_rejected(self):
        runtime = self._runtime()
        from agents.planner import PlannerAgent as PA

        with pytest.raises(ValueError):
            runtime.spawn(PA, agent_id="planner-1")


class TestSupervisor:
    def test_dispatch_collects_results_and_goal_met(self):
        runtime = AgentRuntime(timeout_seconds=5.0)
        runtime.spawn(SupervisorAgent, agent_id="sup-1")
        supervisor = AgentSupervisor(runtime, max_retries=0)
        report = supervisor.dispatch("assess", ["sup-1"], context={"results": {}})
        assert report.goal_met and report.succeeded == ["sup-1"]

    def test_failure_counts_retries(self):
        runtime = AgentRuntime(timeout_seconds=5.0)
        runtime.spawn(CoderAgent, agent_id="coder-1")  # no llm -> always fails
        supervisor = AgentSupervisor(runtime, max_retries=2)
        report = supervisor.dispatch("write code", ["coder-1"])
        assert not report.goal_met
        assert report.retries["coder-1"] == 2


class TestRegistryMemoryToolsLoop:
    def test_registry_by_role(self):
        registry = AgentRegistry()
        registry.register(PlannerAgent("p"))
        registry.register(AnalystAgent("a"))
        assert len(registry.by_role("planner")) == 1
        assert len(registry.by_role("analyst")) == 1

    def test_memory_bounded_log(self):
        memory = AgentMemory(log_size=3)
        for i in range(5):
            memory.append("agent", {"i": i})
        history = memory.history("agent")
        assert len(history) == 3 and history[-1]["i"] == 4

    def test_toolbelt_denies_unlisted_tools(self):
        belt = AgentToolbelt(AgentPolicy())
        belt.register(ToolBinding(name="fs_read", fn=lambda: "data"))
        with pytest.raises(ToolPermissionError):
            belt.invoke("fs_read")

    def test_toolbelt_allows_listed_and_gates_approval(self):
        policy = AgentPolicy(allowed_tools=frozenset({"read", "delete"}))
        belt = AgentToolbelt(policy)
        belt.register(ToolBinding(name="read", fn=lambda path="": path))
        belt.register(
            ToolBinding(name="delete", fn=lambda path="": "deleted",
                        requires_approval=True)
        )
        assert belt.invoke("read", path="f.txt") == "f.txt"
        with pytest.raises(ToolPermissionError):
            belt.invoke("delete", path="f.txt")  # no approval callback

    def test_loop_completes_on_done_flag(self):
        policy = AgentPolicy(max_steps=5)

        def step(index, state):
            return {"done": index >= 1}

        result = run_agent_loop(step, policy)
        assert result.completed and result.step_count == 2

    def test_loop_respects_step_budget(self):
        policy = AgentPolicy(max_steps=3)
        result = run_agent_loop(lambda i, s: {}, policy)
        assert not result.completed
        assert result.stopped_reason == "step budget exhausted"