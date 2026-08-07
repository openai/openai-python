"""Tests for parse_response handling of null/None output fields."""

from __future__ import annotations

from openai._models import construct_type_unchecked
from openai._types import Omit
from openai.lib._parsing._responses import parse_response
from openai.types.responses import Response, ParsedResponse


def _make_response(output=None, **kwargs):
    """Helper to construct a Response with a given output field."""
    base = {
        "id": "resp_test123",
        "created_at": 1234567890.0,
        "model": "gpt-4o",
        "object": "response",
        "status": "completed",
        "output": output,
        "parallel_tool_calls": True,
        "tool_choice": "auto",
        "tools": [],
        "temperature": 1.0,
        "top_p": 1.0,
    }
    base.update(kwargs)
    return construct_type_unchecked(type_=Response, value=base)


def test_parse_response_with_none_output():
    """Test that parse_response handles null output without crashing."""
    response = _make_response(output=None)
    assert response.output is None

    result = parse_response(
        text_format=None,
        input_tools=None,
        response=response,
    )

    assert isinstance(result, ParsedResponse)
    assert result.output == []


def test_parse_response_with_empty_list_output():
    """Test that parse_response handles empty list output correctly."""
    response = _make_response(output=[])
    assert response.output == []

    result = parse_response(
        text_format=None,
        input_tools=None,
        response=response,
    )

    assert isinstance(result, ParsedResponse)
    assert result.output == []


def test_parse_response_with_message_output():
    """Test that parse_response still works correctly with actual output items."""
    output_data = [
        {
            "id": "msg_test123",
            "type": "message",
            "status": "completed",
            "role": "assistant",
            "content": [
                {
                    "type": "output_text",
                    "text": "Hello, world!",
                    "annotations": [],
                }
            ],
        }
    ]
    response = _make_response(output=output_data)

    result = parse_response(
        text_format=Omit(),
        input_tools=None,
        response=response,
    )

    assert isinstance(result, ParsedResponse)
    assert len(result.output) == 1
    assert result.output[0].type == "message"