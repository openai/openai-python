# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .beta_response_format_text_json_schema_config import BetaResponseFormatTextJSONSchemaConfig

__all__ = ["BetaResponseConfigurationUpdateItemParam", "Agent", "Reasoning", "Text", "TextFormat", "TextFormatText"]


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


class BetaResponseConfigurationUpdateItemParam(BaseModel):
    """An update to the conversation's response configuration.

    Supply reasoning,
    text, or both. Each setting stays in effect until a later update replaces it.
    """

    type: Literal["configuration_update"]
    """The item type. Always `configuration_update`."""

    id: Optional[str] = None
    """The unique ID of the configuration update item."""

    agent: Optional[Agent] = None
    """The agent that produced this item."""

    reasoning: Optional[Reasoning] = None
    """Updates to reasoning configuration. Only effort is supported."""

    text: Optional[Text] = None
    """The text output configuration for subsequent responses."""
