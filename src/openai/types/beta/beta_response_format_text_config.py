# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .beta_response_format_text_json_schema_config import BetaResponseFormatTextJSONSchemaConfig

__all__ = ["BetaResponseFormatTextConfig", "Text", "JSONObject"]


class Text(BaseModel):
    """Default response format. Used to generate text responses."""

    type: Literal["text"]
    """The type of response format being defined. Always `text`."""


class JSONObject(BaseModel):
    """JSON object response format.

    An older method of generating JSON responses.
    Using `json_schema` is recommended for models that support it. Note that the
    model will not generate JSON without a system or user message instructing it
    to do so.
    """

    type: Literal["json_object"]
    """The type of response format being defined. Always `json_object`."""


BetaResponseFormatTextConfig: TypeAlias = Annotated[
    Union[Text, BetaResponseFormatTextJSONSchemaConfig, JSONObject], PropertyInfo(discriminator="type")
]
