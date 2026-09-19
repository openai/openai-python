from __future__ import annotations

from typing import Optional

from pydantic import Field, BaseModel

from openai.lib._pydantic import to_strict_json_schema


class NestedExample(BaseModel):
    value: str = Field(
        description="A nested value",
        examples=["alpha", "beta"],
    )


class ExampleModel(BaseModel):
    answer: str = Field(
        description="The final answer",
        examples=["x = -3", "x = 2"],
    )
    nested: NestedExample


def test_strict_json_schema_strips_examples_recursively() -> None:
    schema = to_strict_json_schema(ExampleModel)

    answer = schema["properties"]["answer"]
    assert "examples" not in answer
    assert answer["description"] == "The final answer"

    nested_ref = schema["properties"]["nested"]
    assert "examples" not in nested_ref

    nested = schema["$defs"]["NestedExample"]["properties"]["value"]
    assert "examples" not in nested
    assert nested["description"] == "A nested value"


def test_strict_json_schema_keeps_validation_keywords() -> None:
    schema = to_strict_json_schema(ExampleModel)

    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False
    assert schema["required"] == ["answer", "nested"]


class OptionalExample(BaseModel):
    maybe: Optional[str] = Field(
        default=None,
        description="An optional value",
        examples=["optional-example"],
    )


def test_strict_json_schema_strips_examples_from_anyof_property() -> None:
    schema = to_strict_json_schema(OptionalExample)

    maybe = schema["properties"]["maybe"]
    assert "examples" not in maybe
    assert "anyOf" in maybe
    assert maybe["description"] == "An optional value"
