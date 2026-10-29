# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ...._models import BaseModel
from ..agent_text import AgentText
from ..agent_tool import AgentTool
from ..agent_reasoning import AgentReasoning
from ..multi_agent_config import MultiAgentConfig

__all__ = ["AutomationAgentConfig", "Compaction", "Experimental"]


class Compaction(BaseModel):
    """The effective context compaction settings."""

    async_: bool = FieldInfo(alias="async")
    """Whether context is compacted in the background. Defaults to true."""


class Experimental(BaseModel):
    """The effective experimental settings for the agent."""

    time_awareness: bool
    """Whether the model receives periodic current-time reminders."""


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

    compaction: Optional[Compaction] = None
    """The effective context compaction settings."""

    experimental: Optional[Experimental] = None
    """The effective experimental settings for the agent."""
