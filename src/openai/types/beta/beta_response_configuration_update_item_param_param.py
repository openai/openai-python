# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .beta_response_format_text_json_schema_config_param import BetaResponseFormatTextJSONSchemaConfigParam

__all__ = [
    "BetaResponseConfigurationUpdateItemParamParam",
    "Agent",
    "Reasoning",
    "Text",
    "TextFormat",
    "TextFormatText",
]


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


class TextFormatText(TypedDict, total=False):
    """Default response format. Used to generate text responses."""

    type: Required[Literal["text"]]
    """The type of response format being defined. Always `text`."""


TextFormat: TypeAlias = Union[TextFormatText, BetaResponseFormatTextJSONSchemaConfigParam]


class Text(TypedDict, total=False):
    """The text output configuration for subsequent responses."""

    format: Required[TextFormat]
    """Use a JSON schema for structured output or text to return to plain text."""


class BetaResponseConfigurationUpdateItemParamParam(TypedDict, total=False):
    """An update to the conversation's response configuration.

    Supply reasoning,
    text, or both. Each setting stays in effect until a later update replaces it.
    """

    type: Required[Literal["configuration_update"]]
    """The item type. Always `configuration_update`."""

    id: Optional[str]
    """The unique ID of the configuration update item."""

    agent: Optional[Agent]
    """The agent that produced this item."""

    reasoning: Reasoning
    """Updates to reasoning configuration. Only effort is supported."""

    text: Text
    """The text output configuration for subsequent responses."""
