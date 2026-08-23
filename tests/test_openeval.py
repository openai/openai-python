from __future__ import annotations

import pytest

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
    assert metadata.get("openeval", {}).get("openai_messages") == [{"role": "user", "content": "Hello"}]


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
    assert metadata.get("openeval", {}).get("openai_messages") == messages


def test_to_openeval_auto_generates_id() -> None:
    messages = [{"role": "user", "content": "Hi"}]
    exported = to_openeval(messages, graders=["grader-1"])
    assert isinstance(exported["id"], str)
    assert len(exported["id"]) > 0


def test_to_openeval_rejects_empty_messages() -> None:
    with pytest.raises(ValueError, match="messages must contain at least one message"):
        to_openeval([], graders=["grader-1"])


def test_to_openeval_rejects_empty_graders() -> None:
    with pytest.raises(ValueError, match="graders must contain at least one grader"):
        to_openeval([{"role": "user", "content": "hi"}], graders=[])


def test_to_openeval_with_inline_graders_and_optional_fields() -> None:
    inline_grader: OpenEvalGrader = {
        "id": "g-inline",
        "type": "exact_match",
        "name": "Exact match grader",
        "description": "Checks exact output string",
        "weight": 1.5,
        "params": {"case_sensitive": True},
    }
    messages = [{"role": "user", "content": "Test"}]
    exported = to_openeval(messages, graders=[inline_grader], id="eval-inline")
    assert exported["graders"] == [inline_grader]


def test_to_openeval_preserves_empty_expected_output() -> None:
    messages = [{"role": "user", "content": "Silence"}]
    exported = to_openeval(messages, graders=["grader-1"], expected_output="")
    assert exported.get("expected_output") == ""


def test_to_openeval_preserves_caller_openai_metadata() -> None:
    messages = [{"role": "user", "content": "Hello"}]
    caller_openai_meta = {"messages": ["caller-owned-marker"], "source": "nightly-job"}
    exported = to_openeval(
        messages,
        graders=["grader-1"],
        metadata={"openai": caller_openai_meta, "extra": 123},
    )
    assert exported["metadata"]["openai"] == caller_openai_meta
    assert exported["metadata"]["extra"] == 123
    assert exported["metadata"]["openeval"]["openai_messages"] == messages

    imported = from_openeval(exported)
    assert imported["messages"] == messages
    assert imported["metadata"]["openai"] == caller_openai_meta


def test_from_openeval_with_openeval_metadata_lossless() -> None:
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
        "metadata": {"custom": "meta", "openeval": {"openai_messages": messages}},
    }
    converted = from_openeval(item)
    assert converted["id"] == "eval-lossless"
    assert converted["messages"] == messages
    assert converted["expected_output"] == "42"
    assert converted["metadata"] == {"custom": "meta", "openeval": {"openai_messages": messages}}


def test_from_openeval_legacy_openai_metadata_fallback() -> None:
    legacy_messages = [{"role": "user", "content": "Legacy message"}]
    item: OpenEvalItem = {
        "id": "eval-legacy",
        "input": "user: Legacy message",
        "graders": ["grader-1"],
        "metadata": {"openai": {"messages": legacy_messages}},
    }
    converted = from_openeval(item)
    assert converted["messages"] == legacy_messages


def test_from_openeval_preserves_extra_fields() -> None:
    item: OpenEvalItem = {
        "id": "eval-extra",
        "input": "Question",
        "graders": ["grader-1"],
        "context": "Retrieved doc text",
        "retrieval_context": ["doc1", "doc2"],
        "tools_called": ["search"],
        "expected_tools": ["search"],
    }
    converted = from_openeval(item)
    assert converted["id"] == "eval-extra"
    assert converted["messages"] == [{"role": "user", "content": "Question"}]
    assert converted["context"] == "Retrieved doc text"
    assert converted["retrieval_context"] == ["doc1", "doc2"]
    assert converted["tools_called"] == ["search"]
    assert converted["expected_tools"] == ["search"]


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

