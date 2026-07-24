"""Regression tests for null-output edge cases in the Responses API."""
from __future__ import annotations

import pytest

from openai.types.responses.response import Response
from openai.lib._parsing._responses import parse_response


def _make_response(output):
    """Build a minimal Response fixture with the given output value."""
    return Response.model_construct(
        id="resp_test",
        object="response",
        created_at=0,
        status="completed",
        background=False,
        error=None,
        incomplete_details=None,
        instructions=None,
        max_output_tokens=None,
        max_tool_calls=None,
        model="gpt-4o-mini",
        output=output,
        parallel_tool_calls=True,
        previous_response_id=None,
        prompt_cache_key=None,
        reasoning=None,
        safety_identifier=None,
        service_tier="default",
        store=True,
        temperature=1.0,
        text=None,
        tool_choice="auto",
        tools=[],
        top_p=1.0,
        truncation="disabled",
        usage=None,
        user=None,
        metadata={},
    )


def test_output_text_property_null_output():
    """Response.output_text must return '' when output is None (issue #3325 / #3063)."""
    resp = _make_response(output=None)
    assert resp.output_text == ""


def test_output_text_property_null_text_in_content():
    """Response.output_text must skip output_text items with text=None (issue #3063)."""
    from openai.types.responses.response_output_message import ResponseOutputMessage
    from openai.types.responses.response_output_text import ResponseOutputText

    content = [
        ResponseOutputText.model_construct(type="output_text", text=None, annotations=[], logprobs=[]),
        ResponseOutputText.model_construct(type="output_text", text='{"ok": true}', annotations=[], logprobs=[]),
    ]
    msg = ResponseOutputMessage.model_construct(
        id="msg_test",
        type="message",
        status="completed",
        role="assistant",
        content=content,
    )
    resp = _make_response(output=[msg])
    # only the non-null text should be concatenated
    assert resp.output_text == '{"ok": true}'


def test_parse_response_null_output_does_not_crash():
    """parse_response must not raise TypeError when response.output is None (issue #3325)."""
    from openai import NOT_GIVEN

    resp = _make_response(output=None)
    # Should not raise
    parsed = parse_response(text_format=NOT_GIVEN, input_tools=NOT_GIVEN, response=resp)
    assert parsed.output == []


def test_parse_response_null_text_skips_structured_parse():
    """parse_response must not crash when an output_text item has text=None (issue #3063)."""
    from openai import NOT_GIVEN
    from openai.types.responses.response_output_message import ResponseOutputMessage
    from openai.types.responses.response_output_text import ResponseOutputText

    content = [
        ResponseOutputText.model_construct(type="output_text", text=None, annotations=[], logprobs=[]),
        ResponseOutputText.model_construct(type="output_text", text="hello", annotations=[], logprobs=[]),
    ]
    msg = ResponseOutputMessage.model_construct(
        id="msg_test",
        type="message",
        status="completed",
        role="assistant",
        content=content,
    )
    resp = _make_response(output=[msg])
    # Should not raise; null-text item gets parsed=None, non-null item gets parsed normally.
    parsed = parse_response(text_format=NOT_GIVEN, input_tools=NOT_GIVEN, response=resp)
    assert len(parsed.output) == 1
