# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import Literal, TypedDict

__all__ = ["SessionUpdateParams", "Agent", "AgentReasoning"]


class SessionUpdateParams(TypedDict, total=False):
    agent: Agent
    """Model settings for subsequent turns. Omitted fields stay unchanged."""

    metadata: Optional[Dict[str, str]]
    """Replaces all metadata.

    Omit to leave unchanged, or pass null or {} to clear it. Up to 16 string
    key-value pairs, with keys up to 64 and values up to 512 characters.
    """


class AgentReasoning(TypedDict, total=False):
    """Reasoning settings to update. Omit to keep the current effort."""

    effort: Optional[Literal["none", "minimal", "low", "medium", "high", "xhigh", "max"]]
    """The amount of reasoning effort the model should use."""


class Agent(TypedDict, total=False):
    """Model settings for subsequent turns. Omitted fields stay unchanged."""

    model: str
    """The model for subsequent turns. Omit to keep the current model."""

    reasoning: AgentReasoning
    """Reasoning settings to update. Omit to keep the current effort."""

    service_tier: Optional[Literal["auto", "default", "flex", "priority", "fast"]]
    """The service tier used for model requests.

    - `auto` - Selects the service tier automatically.
    - `default` - Uses the default service tier.
    - `flex` - Uses the flex service tier.
    - `priority` - Uses the priority service tier.
    - `fast` - Uses the fast service tier.
    """
