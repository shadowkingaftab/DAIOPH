"""CoderAgent role package."""

from agents.coder.agent import AgentCapabilityError, CoderAgent
from agents.coder.prompts import ROLE, SYSTEM_PROMPT, build_prompt

__all__ = ["CoderAgent", "AgentCapabilityError", "ROLE", "SYSTEM_PROMPT", "build_prompt"]
