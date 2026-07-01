from __future__ import annotations

from openai._types import omit
from openai.lib._parsing._responses import parse_response
from openai.types.responses import Response


def _minimal_response(**overrides: object) -> Response:
    # Build a Response with the required scalar fields set; `output` is the
    # field under test. Uses construct() to avoid pulling a full live payload.
    base: dict[str, object] = dict(
        id="resp_test",
        created_at=0.0,
        error=None,
        incomplete_details=None,
        instructions=None,
        metadata=None,
        model="gpt-4o-mini",
        object="response",
        output=[],
        parallel_tool_calls=True,
        temperature=1.0,
        tool_choice="auto",
        tools=[],
        top_p=1.0,
    )
    base.update(overrides)
    return Response.construct(**base)


def test_parse_response_handles_none_output() -> None:
    # `output` can be None for incomplete/failed/reasoning-only responses and
    # via some proxy/aggregator backends. parse_response must not raise
    # TypeError('NoneType' object is not iterable) — it should yield empty output.
    response = _minimal_response(output=None)

    parsed = parse_response(text_format=omit, input_tools=None, response=response)

    assert parsed.output == []
