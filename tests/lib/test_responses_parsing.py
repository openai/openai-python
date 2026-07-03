from __future__ import annotations

from openai.lib._parsing._responses import parse_response
from openai.types.responses.response import Response
from openai import NOT_GIVEN


def test_parse_response_handles_none_output() -> None:
    response = Response.model_construct(output=None)

    parsed = parse_response(
        text_format=NOT_GIVEN,
        input_tools=NOT_GIVEN,
        response=response,
    )

    assert parsed.output == []
