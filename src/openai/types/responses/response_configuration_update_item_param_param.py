# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

from ..shared.reasoning_effort import ReasoningEffort

__all__ = ["ResponseConfigurationUpdateItemParamParam", "Reasoning"]


class Reasoning(TypedDict, total=False):
    """Updates to reasoning configuration. Only effort is supported."""

    effort: Optional[ReasoningEffort]
    """
    The reasoning effort to use for subsequent responses until another configuration
    update replaces it.
    """


class ResponseConfigurationUpdateItemParamParam(TypedDict, total=False):
    """An update to the conversation's response configuration.

    The configuration
    remains in effect for subsequent responses until it is replaced by another
    configuration update.
    """

    type: Required[Literal["configuration_update"]]
    """The item type. Always `configuration_update`."""

    id: Optional[str]
    """The unique ID of the configuration update item."""

    reasoning: Reasoning
    """Updates to reasoning configuration. Only effort is supported."""
