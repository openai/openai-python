# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["ResponseFormatJSONSchema", "JSONSchema"]


class JSONSchema(BaseModel):
    name: str
    """The name of the response format.

    Must be a-z, A-Z, 0-9, or contain underscores and dashes, with a maximum length
    of 64.
    """

    description: Optional[str] = None
    """
    A description of what the response format is for, used by the model to determine
    how to respond in the format.
    """

    schema_: Optional[Dict[str, object]] = FieldInfo(alias="schema", default=None)
    """The schema for the response format, described as a JSON Schema object."""

    strict: Optional[bool] = None
    """Whether to enable strict schema adherence when generating the output.

    If set to true, the model will always follow the exact schema defined in the
    `schema` field. Only a subset of JSON Schema is supported when `strict` is
    `true`. To learn more, read the
    [Structured Outputs guide](https://platform.openai.com/docs/guides/structured-outputs).
    """


class ResponseFormatJSONSchema(BaseModel):
    json_schema: JSONSchema

    type: Literal["json_schema"]
    """The type of response format being defined: `json_schema`"""
