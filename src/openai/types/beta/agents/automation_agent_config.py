# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ...._models import BaseModel
from ..agent_text import AgentText
from ..agent_tool import AgentTool
from ..agent_reasoning import AgentReasoning
from ..multi_agent_config import MultiAgentConfig

__all__ = ["AutomationAgentConfig"]


class AutomationAgentConfig(BaseModel):
    """Inline agent configuration without a generated session-local identity."""

    instructions: Optional[str] = None
    """Custom instructions, or null when absent."""

    model: str
    """The requested model name."""

    multi_agent: MultiAgentConfig
    """The configuration for creating and coordinating subagents."""

    reasoning: AgentReasoning
    """The configured reasoning policy."""

    service_tier: Literal["auto", "default", "flex", "priority", "fast", "ultrafast"]
    """The configured service-tier policy."""

    text: AgentText
    """The configured output format and verbosity."""

    tools: List[AgentTool]
    """Configured tools, excluding confidential credentials."""
