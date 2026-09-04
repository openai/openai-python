"""Regression tests for PydanticSerializationUnexpectedValue warnings.

See https://github.com/openai/openai-python/issues/2872
"""
from __future__ import annotations

import warnings

from pydantic import BaseModel

from openai._models import construct_type_unchecked
from openai.types.responses import Response
from openai.lib._parsing._responses import parse_response


class GuardrailDecision(BaseModel):
    triggered: bool
    reason: str


def _make_raw_response() -> Response:
    """Build a minimal Response object from a dict — no API call needed."""
    return construct_type_unchecked(
        type_=Response,
        value={
            "id": "resp_test123",
            "object": "response",
            "created_at": 1234567890.0,
            "model": "gpt-4o-mini",
            "output": [
                {
                    "id": "msg_test123",
                    "type": "message",
                    "status": "completed",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": '{"triggered": true, "reason": "test content flagged"}',
                            "annotations": [],
                        }
                    ],
                }
            ],
            "parallel_tool_calls": True,
            "tool_choice": "auto",
            "tools": [],
            "temperature": 1.0,
            "top_p": 1.0,
            "text": {"format": {"type": "text"}},
            "truncation": "disabled",
        },
    )


def test_parsed_response_model_dump_no_warnings() -> None:
    """model_dump() should not emit PydanticSerializationUnexpectedValue warnings."""
    raw = _make_raw_response()
    parsed = parse_response(
        text_format=GuardrailDecision, input_tools=None, response=raw
    )

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        data = parsed.model_dump()
        pydantic_warnings = [
            x for x in w if "PydanticSerializationUnexpectedValue" in str(x.message)
        ]

    assert len(pydantic_warnings) == 0, (
        f"Expected 0 PydanticSerializationUnexpectedValue warnings, "
        f"got {len(pydantic_warnings)}: {[str(x.message) for x in pydantic_warnings]}"
    )

    # Verify the parsed data is preserved correctly
    assert data["output"][0]["content"][0]["parsed"] == {
        "triggered": True,
        "reason": "test content flagged",
    }


def test_parsed_response_model_dump_json_no_warnings() -> None:
    """model_dump_json() should not emit PydanticSerializationUnexpectedValue warnings."""
    raw = _make_raw_response()
    parsed = parse_response(
        text_format=GuardrailDecision, input_tools=None, response=raw
    )

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        parsed.model_dump_json()
        pydantic_warnings = [
            x for x in w if "PydanticSerializationUnexpectedValue" in str(x.message)
        ]

    assert len(pydantic_warnings) == 0


def test_parsed_response_output_parsed() -> None:
    """output_parsed property should return the parsed object."""
    raw = _make_raw_response()
    parsed = parse_response(
        text_format=GuardrailDecision, input_tools=None, response=raw
    )

    result = parsed.output_parsed
    assert isinstance(result, GuardrailDecision)
    assert result.triggered is True
    assert result.reason == "test content flagged"
