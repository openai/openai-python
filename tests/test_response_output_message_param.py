from __future__ import annotations

from typing_extensions import assert_type

from openai.types.beta import BetaResponseInputParam
from openai.types.responses import ResponseInputParam
from openai.types.beta.beta_response_output_message_param import BetaResponseOutputMessageParam
from openai.types.responses.response_output_message_param import ResponseOutputMessageParam


def test_response_output_message_param_id_and_status_are_optional() -> None:
    # Client-authored assistant message turn without invented id or status
    message: ResponseOutputMessageParam = {
        "type": "message",
        "role": "assistant",
        "content": [
            {
                "type": "output_text",
                "text": "5",
                "annotations": [],
            },
            {
                "type": "output_text",
                "text": "something else?",
                "annotations": [],
            },
        ],
    }

    assert_type(message, ResponseOutputMessageParam)
    assert "id" not in message
    assert "status" not in message

    # Fully valid within ResponseInputParam list
    conversation: ResponseInputParam = [
        {"role": "user", "content": [{"type": "input_text", "text": "2+3=?"}]},
        message,
        {"role": "user", "content": [{"type": "input_text", "text": "what's the square of the result?"}]},
    ]
    assert len(conversation) == 3


def test_response_output_message_param_with_id_and_status() -> None:
    # Optional id and status are still accepted when provided
    message: ResponseOutputMessageParam = {
        "type": "message",
        "id": "msg_123",
        "status": "completed",
        "role": "assistant",
        "content": [
            {
                "type": "output_text",
                "text": "hello",
                "annotations": [],
            }
        ],
    }

    assert_type(message, ResponseOutputMessageParam)
    assert message["id"] == "msg_123"
    assert message["status"] == "completed"


def test_beta_response_output_message_param_id_and_status_are_optional() -> None:
    # Client-authored assistant message turn without invented id or status
    message: BetaResponseOutputMessageParam = {
        "type": "message",
        "role": "assistant",
        "content": [
            {
                "type": "output_text",
                "text": "5",
                "annotations": [],
            },
        ],
    }

    assert_type(message, BetaResponseOutputMessageParam)
    assert "id" not in message
    assert "status" not in message

    conversation: BetaResponseInputParam = [
        {"role": "user", "content": [{"type": "input_text", "text": "hello"}]},
        message,
    ]
    assert len(conversation) == 2
