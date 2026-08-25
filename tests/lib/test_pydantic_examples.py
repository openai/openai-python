from __future__ import annotations

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
