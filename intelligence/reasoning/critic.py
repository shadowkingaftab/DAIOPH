"""Critic - provides critical feedback on reasoning results."""

from typing import Any, Dict, List, Optional


class Critic:
    """Critiques reasoning outputs and suggests improvements."""

    def critique(self, verified: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Critique a list of verified hypotheses.

        Args:
            verified: List of verified hypotheses.
            context: Optional context.

        Returns:
            List[Dict[str, Any]]: Critiqued results.
        """
        critiqued = []
        for hyp in verified:
            # Simple critique: note any gaps or weaknesses
            issues = []
            if "evidence" not in hyp or not hyp.get("evidence"):
                issues.append("no supporting evidence")
            if hyp.get("status") != "verified":
                issues.append("unverified status")
            critique = {
                "hypothesis_id": hyp.get("id"),
                "issues": issues,
                "suggestions": self._suggest_improvements(hyp),
            }
            critiqued.append(critique)
        return critiqued

    def _suggest_improvements(self, hyp: Dict[str, Any]) -> List[str]:
        """Suggest improvements for a hypothesis.

        Args:
            hyp: Hypothesis dict.

        Returns:
            List[str]: Improvement suggestions.
        """
        suggestions = []
        if not hyp.get("evidence"):
            suggestions.append("gather supporting evidence")
        if hyp.get("status") != "verified":
            suggestions.append("re-evaluate with additional data")
        return suggestions

    def reset(self) -> None:
        """Reset the critic."""
        pass

</final_file_content>
</write_to_file>