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

try:
    from intelligence.liquid.adapters.cfc_adapter import CfCAdapter
except Exception:  # pragma: no cover - optional dependency
    CfCAdapter = None


class LiquidEngine:
    """Coordinates all liquid intelligence components."""

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        cfc_adapter: Optional[Any] = None,
    ) -> None:
        """Initialize the liquid engine.

        Args:
            config: Optional configuration dict.
            cfc_adapter: Optional CfCAdapter instance for study model integration.
                        If provided, enables optional CfC-based predictions.
                        Default engine behavior is unchanged when not provided.
        """
        self.config = config or {}
        self.state = LiquidState()
        self.context = LiquidContext()
        self.controller = LiquidController()
        self.adaptation = AdaptationManager()
        self.confidence = ConfidenceEstimator()
        self.uncertainty = UncertaintyEstimator()

        # Optional CfC study model adapter (lazy-loaded when used)
        self._cfc_adapter = cfc_adapter
        self._cfc_enabled = cfc_adapter is not None

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

        result = {
            "action": action,
            "confidence": confidence,
            "uncertainty": uncertainty,
            "state": self.state.get_snapshot(),
        }

        # Optionally include CfC study model prediction if adapter is configured
        if self._cfc_enabled and self._cfc_adapter is not None:
            try:
                cfc_result = self._cfc_adapter.predict(str(input_data))
                result["cfc_prediction"] = cfc_result
            except Exception:
                # Silently ignore CfC errors to preserve default behavior
                result["cfc_prediction"] = {"error": "cfc_adapter_unavailable"}

        return result

    def cfc_predict(self, text: str) -> Dict[str, Any]:
        """Get prediction from CfC study model adapter.

        Only available when CfCAdapter is explicitly injected at construction.

        Args:
            text: Input text to classify.

        Returns:
            Dict with intent, confidence, logits.

        Raises:
            RuntimeError: If CfC adapter is not configured or checkpoint missing.
        """
        if not self._cfc_enabled or self._cfc_adapter is None:
            raise RuntimeError(
                "CfC adapter not configured. Pass cfc_adapter to LiquidEngine constructor."
            )
        return self._cfc_adapter.predict(text)

    def cfc_update(self, text: str, verified_intent: str) -> Dict[str, Any]:
        """Update CfC study model with a VERIFIED intent label.

        Only available when CfCAdapter is explicitly injected at construction.
        NEVER call with the model's own predicted label - must be externally verified.

        Args:
            text: Input text.
            verified_intent: Ground-truth intent label (verified externally).

        Returns:
            Dict with update info.

        Raises:
            RuntimeError: If CfC adapter is not configured.
            ValueError: If verified_intent is not in known label set.
        """
        if not self._cfc_enabled or self._cfc_adapter is None:
            raise RuntimeError(
                "CfC adapter not configured. Pass cfc_adapter to LiquidEngine constructor."
            )
        return self._cfc_adapter.update(text, verified_intent)

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