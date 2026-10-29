# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable, Optional
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from .agent_text_param import AgentTextParam
from .agent_reasoning_param import AgentReasoningParam
from .multi_agent_config_param import MultiAgentConfigParam
from .persisted_agent_tool_param import PersistedAgentToolParam

__all__ = ["AgentCreateParams", "Compaction", "Experimental"]


class AgentCreateParams(TypedDict, total=False):
    model: Required[str]
    """The model to use for the agent. The requested model name is preserved."""

    compaction: Optional[Compaction]
    """Context compaction settings. Omission or null enables background compaction."""

    experimental: Experimental
    """Experimental agent settings. All experimental features default to disabled."""

    instructions: Optional[str]
    """Additional instructions appended to the agent's default base instructions.

    Omit or set to null to add no custom instructions.
    """

    metadata: Optional[Dict[str, str]]
    """
    Up to 16 string key-value pairs, with keys up to 64 and values up to 512
    characters. Omission or null defaults to an empty map.
    """

    multi_agent: Optional[MultiAgentConfigParam]
    """Configuration for creating and coordinating subagents.

    Subagent tools are disabled by default.
    """

    name: Optional[str]
    """A human-readable name for the agent. Omission or null leaves the agent unnamed."""

    reasoning: Optional[AgentReasoningParam]
    """Configuration for model reasoning. Omission uses the model's default effort."""

    service_tier: Optional[Literal["auto", "default", "flex", "priority", "fast", "ultrafast"]]
    """The service tier used for model requests. Defaults to `auto`.

    - `auto` - Selects the service tier automatically.
    - `default` - Uses the default service tier.
    - `flex` - Uses the flex service tier.
    - `priority` - Uses the priority service tier.
    - `fast` - Uses the fast service tier.
    - `ultrafast` - Uses the ultrafast service tier.
    """

    text: Optional[AgentTextParam]
    """Configuration for generated text.

    Defaults to the `text` format and medium verbosity.
    """

    tools: Optional[Iterable[PersistedAgentToolParam]]
    """Tools available to the agent.

    Defaults to an empty list. The tool list must fit within 3 MiB (3,145,728 bytes)
    of compact UTF-8 JSON.
    """


class Compaction(TypedDict, total=False):
    """Context compaction settings. Omission or null enables background compaction."""

    async_: Annotated[Optional[bool], PropertyInfo(alias="async")]
    """Whether to compact context in the background.

    Omission or null defaults to true. Set to false to use blocking compaction.
    Background compaction may increase token usage.
    """


class Experimental(TypedDict, total=False):
    """Experimental agent settings. All experimental features default to disabled."""

    time_awareness: bool
    """Whether to give the model periodic current-time reminders. Defaults to false."""
