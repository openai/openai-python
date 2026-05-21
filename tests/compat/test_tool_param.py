from openai.types.chat import ChatCompletionToolParam


def test_tool_param_can_be_instantiated() -> None:
    assert ChatCompletionToolParam(type="function", function={"name": "test"}) == {
        "function": {"name": "test"},
        "type": "function",
    }
