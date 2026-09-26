"""SupervisorAgent role package."""

from agents.supervisor.agent import AgentCapabilityError, SupervisorAgent
from agents.supervisor.prompts import ROLE, SYSTEM_PROMPT, build_prompt

__all__ = ["SupervisorAgent", "AgentCapabilityError", "ROLE", "SYSTEM_PROMPT", "build_prompt"]
