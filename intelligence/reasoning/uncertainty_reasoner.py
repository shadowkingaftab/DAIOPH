"""UncertaintyReasoner - reasons about uncertainty in results."""

from typing import Any, Dict, List, Optional


class UncertaintyReasoner:
    """Reasons about uncertainty across hypotheses and outputs."""

    def reason(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Reason about uncertainty given context.

        Args:
            context: Optional reasoning context.

        Returns:
            Dict[str, Any]: Uncertainty assessment.
        """
        base_uncertainty = 0.3
        if context:
            base_uncertainty = context.get("uncertainty_factor", base_uncertainty)

        return {
            "level": "medium" if base_uncertainty > 0.5 else "low",
            "factor": base_uncertainty,
            "sources": context.get("sources", []) if context else [],
        }

    def reset(self) -> None:
        """Reset the uncertainty reasoner."""
        pass

</final_file_content>
</write_to_file>