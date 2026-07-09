from openai.types.responses import ResponseOutputMessageParam


def make_assistant_message() -> ResponseOutputMessageParam:
    return {
        "content": [{"annotations": [], "text": "hello", "type": "output_text"}],
        "role": "assistant",
        "status": "completed",
        "type": "message",
    }


def test_response_output_message_param_id_is_optional() -> None:
    message = make_assistant_message()

    assert "id" not in message
    assert "id" not in ResponseOutputMessageParam.__required_keys__
    assert "id" in ResponseOutputMessageParam.__optional_keys__
