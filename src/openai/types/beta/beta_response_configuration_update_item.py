# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .beta_response_format_text_json_schema_config import BetaResponseFormatTextJSONSchemaConfig

__all__ = ["BetaResponseConfigurationUpdateItem", "Agent", "Reasoning", "Text", "TextFormat", "TextFormatText"]


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


class TextFormatText(BaseModel):
    """Default response format. Used to generate text responses."""

    type: Literal["text"]
    """The type of response format being defined. Always `text`."""


TextFormat: TypeAlias = Annotated[
    Union[TextFormatText, BetaResponseFormatTextJSONSchemaConfig], PropertyInfo(discriminator="type")
]


class Text(BaseModel):
    """The text output configuration for subsequent responses."""

    format: TextFormat
    """Use a JSON schema for structured output or text to return to plain text."""


class BetaResponseConfigurationUpdateItem(BaseModel):
    """A configuration update for subsequent responses.

    Each setting stays in effect
    until a later update replaces that setting.
    """

    id: str
    """The unique ID of the configuration update item."""

    type: Literal["configuration_update"]
    """The item type. Always `configuration_update`."""

    agent: Optional[Agent] = None
    """The agent that produced this item."""

    reasoning: Optional[Reasoning] = None
    """The reasoning configuration applied by this update."""

    text: Optional[Text] = None
    """The text output configuration for subsequent responses."""
