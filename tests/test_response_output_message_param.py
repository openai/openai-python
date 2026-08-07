from typing_extensions import assert_type

from openai.types.responses.response_output_message_param import ResponseOutputMessageParam


def test_response_output_message_param_id_is_optional() -> None:
    message: ResponseOutputMessageParam = {
        "role": "assistant",
        "status": "completed",
        "type": "message",
        "content": [
            {
                "type": "output_text",
                "text": "hello",
                "annotations": [],
            }
        ],
    }

    assert_type(message, ResponseOutputMessageParam)
    assert "id" not in message
