from __future__ import annotations

from typing import Any, Dict, List, cast

from openai._types import omit
from openai.types.chat import ChatCompletion
from openai.lib._parsing import parse_chat_completion

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


def _dump_tool_calls(completion: ChatCompletion) -> List[Dict[str, Any]]:
    parsed = parse_chat_completion(chat_completion=completion, response_format=omit, input_tools=omit)
    # `cast` avoids the generic `ResponseFormatT` (unbound here) leaking `Unknown`
    # into attribute access under strict type checking. Dump each tool call
    # individually so a custom call is serialized by its own type rather than the
    # message field's declared `list[ParsedFunctionToolCall]`.
    tool_calls = cast("Any", parsed).choices[0].message.tool_calls
    assert tool_calls is not None
    return [tc.model_dump() for tc in tool_calls]


def test_parse_preserves_custom_tool_call() -> None:
    # Regression: a `custom` tool call used to be logged and discarded by
    # `parse_chat_completion`, so `.parse()` returned `tool_calls=None` and the
    # call the model made vanished from the parsed completion.
    dumped = _dump_tool_calls(_completion_with_tool_calls([_CUSTOM_CALL]))

    assert len(dumped) == 1
    assert dumped[0]["type"] == "custom"
    assert dumped[0]["id"] == "call_custom"
    assert dumped[0]["custom"]["name"] == "run_python"
    assert dumped[0]["custom"]["input"] == "print(1)"


def test_parse_preserves_custom_alongside_function_tool_call() -> None:
    dumped = _dump_tool_calls(_completion_with_tool_calls([_FUNCTION_CALL, _CUSTOM_CALL]))

    assert [tc["type"] for tc in dumped] == ["function", "custom"]
    # the function call is still parsed as before (gets `parsed_arguments`)
    assert dumped[0]["function"]["name"] == "get_weather"
    assert "parsed_arguments" in dumped[0]["function"]
    # the custom call is surfaced unchanged rather than dropped
    assert dumped[1]["id"] == "call_custom"
    assert dumped[1]["custom"]["name"] == "run_python"
