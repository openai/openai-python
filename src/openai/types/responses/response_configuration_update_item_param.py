# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from ..shared.reasoning_effort import ReasoningEffort
from ..shared.response_format_text import ResponseFormatText
from .response_format_text_json_schema_config import ResponseFormatTextJSONSchemaConfig

__all__ = ["ResponseConfigurationUpdateItemParam", "Reasoning", "Text", "TextFormat"]


class Reasoning(BaseModel):
    """Updates to reasoning configuration. Only effort is supported."""

    effort: Optional[ReasoningEffort] = None
    """
    The reasoning effort to use for subsequent responses until another configuration
    update replaces it.
    """


TextFormat: TypeAlias = Annotated[
    Union[ResponseFormatText, ResponseFormatTextJSONSchemaConfig], PropertyInfo(discriminator="type")
]


class Text(BaseModel):
    """The text output configuration for subsequent responses."""

    format: TextFormat
    """Use a JSON schema for structured output or text to return to plain text."""


class ResponseConfigurationUpdateItemParam(BaseModel):
    """An update to the conversation's response configuration.

    Supply reasoning,
    text, or both. Each setting stays in effect until a later update replaces it.
    """

    type: Literal["configuration_update"]
    """The item type. Always `configuration_update`."""

    id: Optional[str] = None
    """The unique ID of the configuration update item."""

    reasoning: Optional[Reasoning] = None
    """Updates to reasoning configuration. Only effort is supported."""

    text: Optional[Text] = None
    """The text output configuration for subsequent responses."""
