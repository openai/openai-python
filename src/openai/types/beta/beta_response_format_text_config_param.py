# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .beta_response_format_text_json_schema_config_param import BetaResponseFormatTextJSONSchemaConfigParam

__all__ = ["BetaResponseFormatTextConfigParam", "Text", "JSONObject"]


class Text(TypedDict, total=False):
    """Default response format. Used to generate text responses."""

    type: Required[Literal["text"]]
    """The type of response format being defined. Always `text`."""


class JSONObject(TypedDict, total=False):
    """JSON object response format.

    An older method of generating JSON responses.
    Using `json_schema` is recommended for models that support it. Note that the
    model will not generate JSON without a system or user message instructing it
    to do so.
    """

    type: Required[Literal["json_object"]]
    """The type of response format being defined. Always `json_object`."""


BetaResponseFormatTextConfigParam: TypeAlias = Union[Text, BetaResponseFormatTextJSONSchemaConfigParam, JSONObject]
