"""Reflection - provides metacognitive reflection on reasoning processes."""

from typing import Any, Dict, List, Optional


class Reflection:
    """Metacognitive reflection on reasoning processes."""

    def reflect(self, critiqued: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Reflect on critiqued reasoning results.

        Args:
            critiqued: List of critiqued hypotheses/results.
            context: Optional context.

        Returns:
            Dict[str, Any]: Reflection summary.
        """
        total = len(critiqued)
        issues_found = sum(len(c.get("issues", [])) for c in critiqued)
        suggestions = []
        for c in critiqued:
            suggestions.extend(c.get("suggestions", []))

        return {
            "total_items": total,
            "total_issues": issues_found,
            "suggestions": list(set(suggestions)),  # deduplicate
            "reflection_level": "deep" if issues_found > total * 0.5 else "shallow",
        }

    def reset(self) -> None:
        """Reset the reflection engine."""
        pass

</final_file_content>
</write_to_file>