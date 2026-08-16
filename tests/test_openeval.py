from __future__ import annotations

from openai.types.evals import OpenEvalItem, OpenEvalGrader, to_openeval, from_openeval


def test_to_openeval_single_message() -> None:
    messages = [{"role": "user", "content": "Hello"}]
    exported = to_openeval(messages, graders=["grader-1"], id="eval-1", expected_output="World")
    assert exported["id"] == "eval-1"
    assert exported["input"] == "user: Hello"
    assert exported["graders"] == ["grader-1"]
    assert exported.get("expected_output") == "World"
    metadata = exported.get("metadata")
    assert isinstance(metadata, dict)
    assert metadata.get("openai", {}).get("messages") == [{"role": "user", "content": "Hello"}]


def test_to_openeval_multiple_messages() -> None:
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is 2+2?"},
    ]
    exported = to_openeval(messages, graders=["grader-1", "grader-2"], id="eval-2")
    assert exported["id"] == "eval-2"
    assert exported["input"] == ["system: You are a helpful assistant.", "user: What is 2+2?"]
    assert exported["graders"] == ["grader-1", "grader-2"]
    metadata = exported.get("metadata")
    assert isinstance(metadata, dict)
    assert metadata.get("openai", {}).get("messages") == messages


def test_to_openeval_auto_generates_id() -> None:
    messages = [{"role": "user", "content": "Hi"}]
    exported = to_openeval(messages, graders=["grader-1"])
    assert isinstance(exported["id"], str)
    assert len(exported["id"]) > 0


def test_to_openeval_with_inline_graders() -> None:
    inline_grader: OpenEvalGrader = {
        "id": "g-inline",
        "type": "exact_match",
        "params": {"case_sensitive": True},
    }
    messages = [{"role": "user", "content": "Test"}]
    exported = to_openeval(messages, graders=[inline_grader], id="eval-inline")
    assert exported["graders"] == [inline_grader]


def test_to_openeval_preserves_empty_expected_output() -> None:
    messages = [{"role": "user", "content": "Silence"}]
    exported = to_openeval(messages, graders=["grader-1"], expected_output="")
    assert exported.get("expected_output") == ""


def test_from_openeval_with_openai_metadata_lossless() -> None:
    messages = [
        {"role": "system", "content": "Act as a calculator."},
        {"role": "user", "content": [{"type": "text", "text": "Calculate this"}]},
        {"role": "assistant", "content": None, "tool_calls": [{"id": "call_1", "type": "function"}]},
        {"role": "tool", "tool_call_id": "call_1", "content": "42"},
    ]
    item: OpenEvalItem = {
        "id": "eval-lossless",
        "input": "system: Act as a calculator.",
        "graders": ["grader-1"],
        "expected_output": "42",
        "metadata": {"custom": "meta", "openai": {"messages": messages}},
    }
    converted = from_openeval(item)
    assert converted["id"] == "eval-lossless"
    assert converted["messages"] == messages
    assert converted["expected_output"] == "42"
    assert converted["metadata"] == {"custom": "meta", "openai": {"messages": messages}}


def test_from_openeval_scalar_input_fallback() -> None:
    item: OpenEvalItem = {
        "id": "eval-scalar",
        "input": "What is 2+2?",
        "graders": ["grader-1"],
    }
    converted = from_openeval(item)
    assert converted["id"] == "eval-scalar"
    assert converted["messages"] == [{"role": "user", "content": "What is 2+2?"}]
    assert "expected_output" not in converted


def test_from_openeval_list_input_fallback() -> None:
    item: OpenEvalItem = {
        "id": "eval-list",
        "input": ["Turn 1", "Turn 2"],
        "graders": ["grader-1"],
        "expected_output": "",
    }
    converted = from_openeval(item)
    assert converted["id"] == "eval-list"
    assert converted["messages"] == [
        {"role": "user", "content": "Turn 1"},
        {"role": "user", "content": "Turn 2"},
    ]
    assert converted["expected_output"] == ""


def test_round_trip_conversion() -> None:
    original_messages = [
        {"role": "user", "content": "Translate 'hello' to French."},
    ]
    exported = to_openeval(
        original_messages,
        graders=["exact-match-grader"],
        id="round-trip-1",
        expected_output="bonjour",
        metadata={"source": "unit-test"},
    )
    imported = from_openeval(exported)
    assert imported["id"] == "round-trip-1"
    assert imported["messages"] == original_messages
    assert imported["expected_output"] == "bonjour"
    assert imported["metadata"]["source"] == "unit-test"
