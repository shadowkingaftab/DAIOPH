"""Reasoning engine - orchestrates the reasoning pipeline."""

from typing import Any, Dict, List, Optional

from intelligence.reasoning.reasoning_engine import ReasoningEngine
from intelligence.reasoning.planner import Planner
from intelligence.reasoning.task_decomposer import TaskDecomposer
from intelligence.reasoning.hypothesis_engine import HypothesisEngine
from intelligence.reasoning.verifier import Verifier
from intelligence.reasoning.critic import Critic
from intelligence.reasoning.reflection import Reflection
from intelligence.reasoning.uncertainty_reasoner import UncertaintyReasoner


class OrchestratedReasoningEngine:
    """Top-level reasoning orchestrator.

    Composes all sub-engines into a coherent reasoning pipeline
    with planning, hypothesis, verification, and critique.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the reasoning engine.

        Args:
            config: Optional configuration dict.
        """
        self.config = config or {}
        self.planner = Planner()
        self.task_decomposer = TaskDecomposer()
        self.hypothesis_engine = HypothesisEngine()
        self.verifier = Verifier()
        self.critic = Critic()
        self.reflection = Reflection()
        self.uncertainty_reasoner = UncertaintyReasoner()

    def reason(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run the full reasoning pipeline.

        Args:
            input_data: Input to reason over.
            context: Optional context dict.

        Returns:
            Dict[str, Any]: Reasoning result with steps and conclusion.
        """
        # Step 1: Decompose into tasks
        tasks = self.task_decomposer.decompose(input_data, context)

        # Step 2: Generate hypotheses
        hypotheses = self.hypothesis_engine.generate(tasks, context)

        # Step 3: Verify hypotheses
        verified = self.verifier.verify(hypotheses, context)

        # Step 4: Critique the results
        critiqued = self.critic.critique(verified, context)

        # Step 5: Reflect on the process
        reflection = self.reflection.reflect(critiqued, context)

        # Step 6: Reason about uncertainty
        uncertainty = self.uncertainty_reasoner.reason(context)

        return {
            "tasks": tasks,
            "hypotheses": hypotheses,
            "verified": verified,
            "critiqued": critiqued,
            "reflection": reflection,
            "uncertainty": uncertainty,
        }

    def reset(self) -> None:
        """Reset all sub-engines."""
        self.planner.reset()
        self.task_decomposer.reset()
        self.hypothesis_engine.reset()
        self.verifier.reset()
        self.critic.reset()
        self.reflection.reset()
        self.uncertainty_reasoner.reset()