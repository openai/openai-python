from __future__ import annotations

from openai._types import NOT_GIVEN
from openai.types.responses import Response
from openai.lib._parsing._responses import parse_response


def test_parse_response_handles_null_output() -> None:
    response = Response.construct(
        id="resp_123",
        object="response",
        created_at=0,
        status="completed",
        output=None,
        parallel_tool_calls=True,
        tool_choice="auto",
        tools=[],
    )

    parsed = parse_response(
        text_format=NOT_GIVEN,
        input_tools=NOT_GIVEN,
        response=response,
    )

    assert parsed.output == []
