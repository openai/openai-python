# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["BetaResponseConfigurationUpdateItemParamParam", "Agent", "Reasoning"]


class Agent(TypedDict, total=False):
    """The agent that produced this item."""

    agent_name: Required[str]
    """The canonical name of the agent that produced this item."""


class Reasoning(TypedDict, total=False):
    """Updates to reasoning configuration. Only effort is supported."""

    effort: Optional[Literal["none", "minimal", "low", "medium", "high", "xhigh", "max"]]
    """
    The reasoning effort to use for subsequent responses until another configuration
    update replaces it.
    """


class BetaResponseConfigurationUpdateItemParamParam(TypedDict, total=False):
    """An update to the conversation's response configuration.

    The configuration
    remains in effect for subsequent responses until it is replaced by another
    configuration update.
    """

    type: Required[Literal["configuration_update"]]
    """The item type. Always `configuration_update`."""

    id: Optional[str]
    """The unique ID of the configuration update item."""

    agent: Optional[Agent]
    """The agent that produced this item."""

    reasoning: Reasoning
    """Updates to reasoning configuration. Only effort is supported."""
