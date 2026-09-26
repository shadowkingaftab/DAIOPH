"""Liquid intelligence engine - composes the liquid subsystem components.

The engine orchestrates the liquid state, controller, and adaptation
mechanisms to provide adaptive, self-tuning intelligence.
"""

from typing import Any, Dict, Optional

from intelligence.liquid.liquid_state import LiquidState
from intelligence.liquid.liquid_context import LiquidContext
from intelligence.liquid.liquid_controller import LiquidController
from intelligence.liquid.adaptation import AdaptationManager
from intelligence.liquid.confidence import ConfidenceEstimator
from intelligence.liquid.uncertainty import UncertaintyEstimator


class LiquidEngine:
    """Coordinates all liquid intelligence components."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the liquid engine.

        Args:
            config: Optional configuration dict.
        """
        self.config = config or {}
        self.state = LiquidState()
        self.context = LiquidContext()
        self.controller = LiquidController()
        self.adaptation = AdaptationManager()
        self.confidence = ConfidenceEstimator()
        self.uncertainty = UncertaintyEstimator()

    def process(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process input through the liquid intelligence pipeline.

        Args:
            input_data: Input to process.
            context: Optional context dict.

        Returns:
            Dict[str, Any]: Processing result with confidence/uncertainty.
        """
        if context:
            self.context.update(context)

        # Update state with the input
        self.state.update(input_data)

        # Controller decides action based on current state
        action = self.controller.decide(self.state.get_snapshot())

        # Estimate confidence and uncertainty
        confidence = self.confidence.estimate(self.state.get_snapshot(), input_data)
        uncertainty = self.uncertainty.estimate(self.state.get_snapshot(), input_data)

        # Adapt based on the outcome
        self.adaptation.adapt(input_data, action)

        return {
            "action": action,
            "confidence": confidence,
            "uncertainty": uncertainty,
            "state": self.state.get_snapshot(),
        }

    def reset(self) -> None:
        """Reset the liquid engine state."""
        self.state.reset()
        self.context.reset()
        self.controller.reset()

    def get_status(self) -> Dict[str, Any]:
        """Get engine status.

        Returns:
            Dict[str, Any]: Status information.
        """
        return {
            "state": self.state.get_snapshot(),
            "context": self.context.get_all(),
            "stability": self.state.stability,
        }