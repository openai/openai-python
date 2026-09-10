# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["BetaResponseConfigurationUpdateItem", "Agent", "Reasoning"]


class Agent(BaseModel):
    """The agent that produced this item."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class Reasoning(BaseModel):
    """The reasoning configuration applied by this update."""

    effort: Optional[Literal["none", "minimal", "low", "medium", "high", "xhigh", "max"]] = None
    """
    The reasoning effort used for subsequent responses until another configuration
    update replaces it.
    """


class BetaResponseConfigurationUpdateItem(BaseModel):
    """
    A configuration update that applies to subsequent responses until it is
    replaced by another configuration update.
    """

    id: str
    """The unique ID of the configuration update item."""

    type: Literal["configuration_update"]
    """The item type. Always `configuration_update`."""

    agent: Optional[Agent] = None
    """The agent that produced this item."""

    reasoning: Optional[Reasoning] = None
    """The reasoning configuration applied by this update."""
