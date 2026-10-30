# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from ..shared.reasoning_effort import ReasoningEffort
from ..shared_params.response_format_text import ResponseFormatText
from .response_format_text_json_schema_config_param import ResponseFormatTextJSONSchemaConfigParam

__all__ = ["ResponseConfigurationUpdateItemParamParam", "Reasoning", "Text", "TextFormat"]


class Reasoning(TypedDict, total=False):
    """Updates to reasoning configuration. Only effort is supported."""

    effort: Optional[ReasoningEffort]
    """
    The reasoning effort to use for subsequent responses until another configuration
    update replaces it.
    """


TextFormat: TypeAlias = Union[ResponseFormatText, ResponseFormatTextJSONSchemaConfigParam]


class Text(TypedDict, total=False):
    """The text output configuration for subsequent responses."""

    format: Required[TextFormat]
    """Use a JSON schema for structured output or text to return to plain text."""


class ResponseConfigurationUpdateItemParamParam(TypedDict, total=False):
    """An update to the conversation's response configuration.

    Supply reasoning,
    text, or both. Each setting stays in effect until a later update replaces it.
    """

    type: Required[Literal["configuration_update"]]
    """The item type. Always `configuration_update`."""

    id: Optional[str]
    """The unique ID of the configuration update item."""

    reasoning: Reasoning
    """Updates to reasoning configuration. Only effort is supported."""

    text: Text
    """The text output configuration for subsequent responses."""
