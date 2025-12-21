from openai.types.chat import ChatCompletionNamedToolChoiceParam


def test_chat_completion_named_tool_choice_param_name() -> None:
    annotations = ChatCompletionNamedToolChoiceParam.__annotations__

    assert "type" in annotations
    assert "name" in annotations
    assert "function" not in annotations
