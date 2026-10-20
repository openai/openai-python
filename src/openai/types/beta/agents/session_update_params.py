# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["SessionUpdateParams", "Agent", "AgentReasoning", "SpendControl"]


class SessionUpdateParams(TypedDict, total=False):
    agent: Agent
    """Model settings for subsequent turns. Omitted fields stay unchanged."""

    metadata: Optional[Dict[str, str]]
    """Replaces all metadata.

    Omit to leave unchanged, or pass null or {} to clear it. Up to 16 string
    key-value pairs, with keys up to 64 and values up to 512 characters.
    """

    spend_control: Optional[SpendControl]
    """
    Omit to retain the limit; null or a null limit removes it without resetting
    spend.
    """


class AgentReasoning(TypedDict, total=False):
    """Reasoning settings to update. Omit to keep the current effort."""

    effort: Optional[Literal["none", "minimal", "low", "medium", "high", "xhigh", "max"]]
    """Omit to keep the current effort. Null selects the model's default effort."""


class Agent(TypedDict, total=False):
    """Model settings for subsequent turns. Omitted fields stay unchanged."""

    model: str
    """The model for subsequent turns. Omit to keep the current model."""

    reasoning: AgentReasoning
    """Reasoning settings to update. Omit to keep the current effort."""

    service_tier: Optional[Literal["auto", "default", "flex", "priority", "fast", "ultrafast"]]
    """Omit to keep the current tier. Null resets it to auto.

    - `auto` - Selects the service tier automatically.
    - `default` - Uses the default service tier.
    - `flex` - Uses the flex service tier.
    - `priority` - Uses the priority service tier.
    - `fast` - Uses the fast service tier.
    - `ultrafast` - Uses the ultrafast service tier.
    """


class SpendControl(TypedDict, total=False):
    """
    Omit to retain the limit; null or a null limit removes it without resetting spend.
    """

    limit: Required[Optional[int]]
    """Positive USD cents, or null to remove the limit."""
