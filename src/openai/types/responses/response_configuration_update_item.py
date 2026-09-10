# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from ..shared.reasoning_effort import ReasoningEffort

__all__ = ["ResponseConfigurationUpdateItem", "Reasoning"]


class Reasoning(BaseModel):
    """The reasoning configuration applied by this update."""

    effort: Optional[ReasoningEffort] = None
    """
    The reasoning effort used for subsequent responses until another configuration
    update replaces it.
    """


class ResponseConfigurationUpdateItem(BaseModel):
    """
    A configuration update that applies to subsequent responses until it is
    replaced by another configuration update.
    """

    id: str
    """The unique ID of the configuration update item."""

    type: Literal["configuration_update"]
    """The item type. Always `configuration_update`."""

    reasoning: Optional[Reasoning] = None
    """The reasoning configuration applied by this update."""
