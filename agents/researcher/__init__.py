"""ResearcherAgent role package."""

from agents.researcher.agent import AgentCapabilityError, ResearcherAgent
from agents.researcher.prompts import ROLE, SYSTEM_PROMPT, build_prompt

__all__ = ["ResearcherAgent", "AgentCapabilityError", "ROLE", "SYSTEM_PROMPT", "build_prompt"]
