# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Dict, Union
from typing_extensions import Literal, Annotated, TypeAlias

from pydantic import Field as FieldInfo

from ..._utils import PropertyInfo
from ..._models import BaseModel

__all__ = ["TextFormat", "TextFormatResourceText", "TextFormatResourceJSONSchema"]


class TextFormatResourceText(BaseModel):
    """Generates ordinary text without a structured-output constraint."""

    type: Literal["text"]
    """The type of the object. Always `text`."""


class TextFormatResourceJSONSchema(BaseModel):
    """Constrains generated text to a JSON Schema."""

    schema_: Dict[str, object] = FieldInfo(alias="schema")
    """The JSON Schema that generated text must match."""

    type: Literal["json_schema"]
    """The type of the object. Always `json_schema`."""


TextFormat: TypeAlias = Annotated[
    Union[TextFormatResourceText, TextFormatResourceJSONSchema], PropertyInfo(discriminator="type")
]
