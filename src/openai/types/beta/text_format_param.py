# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union
from typing_extensions import Literal, Required, TypeAlias, TypedDict

__all__ = ["TextFormatParam", "TextFormatParamText", "TextFormatParamJSONSchema"]


class TextFormatParamText(TypedDict, total=False):
    """Generates ordinary text without a structured-output constraint."""

    type: Required[Literal["text"]]
    """The type of the object. Always `text`."""


class TextFormatParamJSONSchema(TypedDict, total=False):
    """Constrains generated text to a JSON Schema."""

    schema: Required[Dict[str, object]]
    """The JSON Schema that generated text must match."""

    type: Required[Literal["json_schema"]]
    """The type of the object. Always `json_schema`."""


TextFormatParam: TypeAlias = Union[TextFormatParamText, TextFormatParamJSONSchema]
