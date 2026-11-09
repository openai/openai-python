# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from ..shared.reasoning_effort import ReasoningEffort
from ..shared.response_format_text import ResponseFormatText
from .response_format_text_json_schema_config import ResponseFormatTextJSONSchemaConfig

__all__ = ["ResponseConfigurationUpdateItem", "Reasoning", "Text", "TextFormat"]


class Reasoning(BaseModel):
    """The reasoning configuration applied by this update."""

    effort: Optional[ReasoningEffort] = None
    """
    The reasoning effort used for subsequent responses until another configuration
    update replaces it.
    """


TextFormat: TypeAlias = Annotated[
    Union[ResponseFormatText, ResponseFormatTextJSONSchemaConfig], PropertyInfo(discriminator="type")
]


class Text(BaseModel):
    """The text output configuration for subsequent responses."""

    format: TextFormat
    """Use a JSON schema for structured output or text to return to plain text."""


class ResponseConfigurationUpdateItem(BaseModel):
    """A configuration update for subsequent responses.

    Each setting stays in effect
    until a later update replaces that setting.
    """

    id: str
    """The unique ID of the configuration update item."""

    type: Literal["configuration_update"]
    """The item type. Always `configuration_update`."""

    reasoning: Optional[Reasoning] = None
    """The reasoning configuration applied by this update."""

    text: Optional[Text] = None
    """The text output configuration for subsequent responses."""
