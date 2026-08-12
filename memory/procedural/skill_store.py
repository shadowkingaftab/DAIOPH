"""SkillStore - stores skills for procedural memory."""

from typing import Any, Dict, List, Optional


class SkillStore:
    """Stores skills for procedural memory."""

    def __init__(self) -> None:
        """Initialize the skill store."""
        self._skills: Dict[str, Dict[str, Any]] = {}

    def add(self, name: str, skill: Dict[str, Any]) -> None:
        """Add a skill.

        Args:
            name: Skill name.
            skill: Skill definition.
        """
        self._skills[name] = skill

    def get(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a skill.

        Args:
            name: Skill name.

        Returns:
            Optional[Dict[str, Any]]: Skill or None.
        """
        return self._skills.get(name)

    def list_skills(self) -> List[str]:
        """List all skill names.

        Returns:
            List[str]: Skill names.
        """
        return list(self._skills.keys())

</final_file_content>
</write_to_file></tool_call>