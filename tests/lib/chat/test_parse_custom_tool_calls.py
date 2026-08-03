from __future__ import annotations

from typing import Any, Dict, List, cast

from openai._types import omit
from openai.types.chat import ChatCompletion, ParsedFunctionToolCall
from openai.lib._parsing import parse_chat_completion
from openai.types.chat.chat_completion_message_custom_tool_call import ChatCompletionMessageCustomToolCall

_FUNCTION_CALL: Dict[str, Any] = {
    "id": "call_fn",
    "type": "function",
    "function": {"name": "get_weather", "arguments": "{}"},
}
_CUSTOM_CALL: Dict[str, Any] = {
    "id": "call_custom",
    "type": "custom",
    "custom": {"name": "run_python", "input": "print(1)"},
}


def _completion_with_tool_calls(tool_calls: List[Dict[str, Any]]) -> ChatCompletion:
    return ChatCompletion.construct(
        id="chatcmpl-test",
        object="chat.completion",
        created=0,
        model="gpt-5",
        choices=[
            {
                "index": 0,
                "finish_reason": "tool_calls",
                "logprobs": None,
                "message": {"role": "assistant", "content": None, "tool_calls": tool_calls},
            }
        ],
    )


def _parse(tool_calls: List[Dict[str, Any]]) -> Any:
    # `cast` avoids the generic `ResponseFormatT` (unbound here) leaking `Unknown`
    # into attribute access under strict type checking.
    return cast(
        "Any",
        parse_chat_completion(
            chat_completion=_completion_with_tool_calls(tool_calls),
            response_format=omit,
            input_tools=omit,
        ),
    )


def _dumped_tool_calls(parsed: Any) -> List[Dict[str, Any]]:
    # Dumps the whole completion rather than each tool call on its own: pydantic
    # serializes by the declared field type, so this is the path that used to
    # silently drop the `custom` payload.
    return cast("List[Dict[str, Any]]", parsed.model_dump()["choices"][0]["message"]["tool_calls"])


def test_parse_preserves_custom_tool_call() -> None:
    # Regression: a `custom` tool call used to be logged and discarded by
    # `parse_chat_completion`, so `.parse()` returned `tool_calls=None` and the
    # call the model made vanished from the parsed completion.
    parsed = _parse([_CUSTOM_CALL])

    tool_calls = parsed.choices[0].message.tool_calls
    assert tool_calls is not None
    assert len(tool_calls) == 1
    assert isinstance(tool_calls[0], ChatCompletionMessageCustomToolCall)
    assert tool_calls[0].custom.name == "run_python"
    assert tool_calls[0].custom.input == "print(1)"

    # ...and it survives serialization of the whole completion, which the narrowed
    # `list[ParsedFunctionToolCall]` annotation used to defeat: the dump came back
    # as `{"id": ..., "type": "custom"}` with `custom` missing entirely.
    assert _dumped_tool_calls(parsed) == [
        {"id": "call_custom", "type": "custom", "custom": {"name": "run_python", "input": "print(1)"}}
    ]


def test_parse_preserves_custom_alongside_function_tool_call() -> None:
    parsed = _parse([_FUNCTION_CALL, _CUSTOM_CALL])

    tool_calls = parsed.choices[0].message.tool_calls
    assert tool_calls is not None
    # the function member still resolves to the parsed subclass, which is what
    # widening the annotation to a union had to preserve. `parsed_arguments` stays
    # None here because no `input_tools` were passed, so there is no schema to parse
    # the arguments against; the point is that the field exists at all.
    assert isinstance(tool_calls[0], ParsedFunctionToolCall)
    assert tool_calls[0].function.name == "get_weather"
    assert tool_calls[0].function.parsed_arguments is None
    assert isinstance(tool_calls[1], ChatCompletionMessageCustomToolCall)

    dumped = _dumped_tool_calls(parsed)
    assert [tc["type"] for tc in dumped] == ["function", "custom"]
    assert dumped[0]["function"] == {"name": "get_weather", "arguments": "{}", "parsed_arguments": None}
    assert dumped[1]["custom"] == {"name": "run_python", "input": "print(1)"}


def test_parse_round_trips_a_custom_tool_call() -> None:
    # A dumped completion has to validate back into an equivalent model, which is
    # what a caller persisting and replaying a parsed completion depends on.
    parsed = _parse([_FUNCTION_CALL, _CUSTOM_CALL])

    reloaded = ChatCompletion.model_validate(parsed.model_dump())

    tool_calls = reloaded.choices[0].message.tool_calls
    assert tool_calls is not None
    assert [tc.type for tc in tool_calls] == ["function", "custom"]
    custom = tool_calls[1]
    assert isinstance(custom, ChatCompletionMessageCustomToolCall)
    assert custom.custom.name == "run_python"
    assert custom.custom.input == "print(1)"
