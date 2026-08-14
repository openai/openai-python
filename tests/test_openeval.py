from openai.types.evals import OpenEvalItem, from_openeval, to_openeval


def test_from_openeval_conversion() -> None:
    item: OpenEvalItem = {
        "id": "eval-1",
        "input": [{"role": "user", "content": "Hello world"}],
        "expected_output": "Hi there!",
        "metadata": {"task": "test"},
    }
    converted = from_openeval(item)
    assert converted["id"] == "eval-1"
    assert converted["messages"] == [{"role": "user", "content": "Hello world"}]
    assert converted["expected_output"] == "Hi there!"
    assert converted["metadata"] == {"task": "test"}


def test_to_openeval_conversion() -> None:
    messages = [{"role": "user", "content": "Hello"}]
    exported = to_openeval(messages, id="eval-2", expected_output="World")
    assert exported["id"] == "eval-2"
    assert exported["input"] == [{"role": "user", "content": "Hello"}]
    assert exported["expected_output"] == "World"
