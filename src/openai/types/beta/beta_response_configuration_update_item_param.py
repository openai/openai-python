# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["BetaResponseConfigurationUpdateItemParam", "Agent", "Reasoning"]


class Agent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class Reasoning(BaseModel):
    """Updates to reasoning configuration. Only effort is supported."""

    effort: Optional[Literal["none", "minimal", "low", "medium", "high", "xhigh", "max"]] = None
    """
    The reasoning effort to use for subsequent responses until another configuration
    update replaces it.
    """


class BetaResponseConfigurationUpdateItemParam(BaseModel):
    """An update to the conversation's response configuration.

    The configuration
    remains in effect for subsequent responses until it is replaced by another
    configuration update.
    """

    type: Literal["configuration_update"]
    """The item type. Always `configuration_update`."""

    id: Optional[str] = None
    """The unique ID of the configuration update item."""

    agent: Optional[Agent] = None
    """The agent that produced this item."""

    reasoning: Optional[Reasoning] = None
    """Updates to reasoning configuration. Only effort is supported."""
