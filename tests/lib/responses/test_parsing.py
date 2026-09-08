from __future__ import annotations

from typing import Any

import pydantic

import openai._models as models
from openai.lib._parsing._responses import parse_response
from openai.types.responses import Response


_MOCK_RESPONSE_JSON: dict[str, Any] = {
    "id": "resp_poc",
    "object": "response",
    "created_at": 1234567890.0,
    "model": "gpt-5.4",
    "parallel_tool_calls": True,
    "status": "completed",
    "tool_choice": "auto",
    "tools": [],
    "output": [
        {
            "type": "message",
            "id": "msg_poc",
            "status": "completed",
            "role": "assistant",
            "content": [
                {
                    "type": "output_text",
                    "text": '{"message": "Hello! How can I help?"}',
                    "annotations": [],
                }
            ],
        }
    ],
    "text": {"format": {"type": "text"}},
    "usage": {
        "input_tokens": 10,
        "output_tokens": 20,
        "total_tokens": 30,
        "input_tokens_details": {"cached_tokens": 0},
        "output_tokens_details": {"reasoning_tokens": 0},
    },
}


class ChatbotResponse(pydantic.BaseModel):
    message: str
    intent: str | None = None


def test_parse_response_does_not_use_non_model_validation(monkeypatch: Any) -> None:
    def fail_if_called(*, type_: Any, value: object) -> Any:
        raise AssertionError(f"unexpected non-model validation for {type_}")

    monkeypatch.setattr(models, "_validate_non_model_type", fail_if_called)

    raw_response = Response.model_validate(_MOCK_RESPONSE_JSON)
    parsed = parse_response(response=raw_response, text_format=ChatbotResponse, input_tools=None)

    assert parsed.output[0].type == "message"
    output_text = parsed.output[0].content[0]
    assert output_text.type == "output_text"
    assert output_text.parsed is not None
    assert output_text.parsed.message == "Hello! How can I help?"
