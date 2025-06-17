from __future__ import annotations

import pytest # noqa: F401
from typing import Union

from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageToolCallParam,  # noqa: F401
    FunctionToolCallParam, # noqa: F401
    FunctionCallParamDetails, # noqa: F401
    CodeInterpreterCallParam, # noqa: F401
    CodeInterpreterOutputLogParam, # noqa: F401
    CodeInterpreterOutputImageParam, # noqa: F401
    CodeInterpreterOutputImageFileParam, # noqa: F401
)
from openai.types.chat.chat_completion_user_message_param import ChatCompletionUserMessageParam
from openai.types.chat.chat_completion_system_message_param import ChatCompletionSystemMessageParam

def test_can_construct_assistant_message_with_function_tool_call() -> None:
    params: ChatCompletionAssistantMessageParam = {
        "role": "assistant",
        "tool_calls": [
            {
                "id": "tool_call_123",
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "arguments": '{"location": "Boston"}',
                },
            }
        ],
    }
    assert params["role"] == "assistant"
    assert params["tool_calls"] is not None
    tool_call = params["tool_calls"][0] # type: ignore
    assert tool_call["id"] == "tool_call_123"
    assert tool_call["type"] == "function"
    # We need to assert that tool_call is FunctionToolCallParam for type checkers
    assert "function" in tool_call 
    assert tool_call["function"]["name"] == "get_weather" # type: ignore


def test_can_construct_assistant_message_with_code_interpreter_log_output() -> None:
    params: ChatCompletionAssistantMessageParam = {
        "role": "assistant",
        "tool_calls": [
            {
                "id": "tool_call_abc",
                "type": "code_interpreter",
                "code": "print('Hello World')",
                "outputs": [
                    {
                        "type": "logs",
                        "logs": "Hello World\n",
                    }
                ],
            }
        ],
    }
    assert params["role"] == "assistant"
    assert params["tool_calls"] is not None
    tool_call = params["tool_calls"][0] # type: ignore
    assert tool_call["id"] == "tool_call_abc"
    assert tool_call["type"] == "code_interpreter"
    # We need to assert that tool_call is CodeInterpreterCallParam for type checkers
    assert "code" in tool_call
    assert tool_call["code"] == "print('Hello World')" # type: ignore
    assert tool_call["outputs"] is not None # type: ignore
    output = tool_call["outputs"][0] # type: ignore
    assert output["type"] == "logs"
    assert "logs" in output # For type checker
    assert output["logs"] == "Hello World\n" # type: ignore


def test_can_construct_assistant_message_with_code_interpreter_image_output() -> None:
    params: ChatCompletionAssistantMessageParam = {
        "role": "assistant",
        "tool_calls": [
            {
                "id": "tool_call_xyz",
                "type": "code_interpreter",
                "code": "# generate image",
                "outputs": [
                    {
                        "type": "image",
                        "image": {
                            "file_id": "file_def456",
                        },
                    }
                ],
            }
        ],
    }
    assert params["role"] == "assistant"
    assert params["tool_calls"] is not None
    tool_call = params["tool_calls"][0] # type: ignore
    assert tool_call["id"] == "tool_call_xyz"
    assert tool_call["type"] == "code_interpreter"
    assert "code" in tool_call # For type checker
    assert tool_call["code"] == "# generate image" # type: ignore
    assert tool_call["outputs"] is not None # type: ignore
    output = tool_call["outputs"][0] # type: ignore
    assert output["type"] == "image"
    assert "image" in output # For type checker
    assert output["image"]["file_id"] == "file_def456" # type: ignore

# Example of constructing a list of messages for ChatCompletionCreateParams
def test_message_list_construction() -> None:
    messages: list[
        Union[
            ChatCompletionUserMessageParam,
            ChatCompletionSystemMessageParam,
            ChatCompletionAssistantMessageParam,
            # Add other message types if necessary, e.g., ToolMessageParam
        ]
    ] = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
        {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": "tool_call_xyz",
                    "type": "code_interpreter",
                    "code": "# generate image",
                    "outputs": [
                        {
                            "type": "image",
                            "image": {"file_id": "file_def456"},
                        }
                    ],
                }
            ],
        },
    ]
    assert len(messages) == 3
    assert messages[2]["role"] == "assistant" # type: ignore