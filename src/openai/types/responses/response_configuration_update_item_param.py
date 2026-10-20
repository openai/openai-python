# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel
from ..shared.reasoning_effort import ReasoningEffort

__all__ = ["ResponseConfigurationUpdateItemParam", "Reasoning"]


class Reasoning(BaseModel):
    """Updates to reasoning configuration. Only effort is supported."""

    effort: Optional[ReasoningEffort] = None
    """
    The reasoning effort to use for subsequent responses until another configuration
    update replaces it.
    """


class ResponseConfigurationUpdateItemParam(BaseModel):
    """An update to the conversation's response configuration.

    The configuration
    remains in effect for subsequent responses until it is replaced by another
    configuration update.
    """

    type: Literal["configuration_update"]
    """The item type. Always `configuration_update`."""

    id: Optional[str] = None
    """The unique ID of the configuration update item."""

    reasoning: Optional[Reasoning] = None
    """Updates to reasoning configuration. Only effort is supported."""
