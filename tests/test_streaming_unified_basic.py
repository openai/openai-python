import pytest
from openai._streaming import (
    StreamEvent,
    extract_text,
    ResponsesEventAdapter,
    ChatCompletionsEventAdapter,
)

def test_responses_delta_mapping():
    class FakeEvt:
        type = "response.output_text.delta"
        delta = "foo"
    ev: StreamEvent = ResponsesEventAdapter.adapt(FakeEvt())
    assert ev.type == "output_text.delta"
    assert ev.delta == "foo"

def test_responses_completed_mapping():
    class FakeEvt:
        type = "response.completed"
    ev = ResponsesEventAdapter.adapt(FakeEvt())
    assert ev.type == "response.completed"

def test_chat_delta_mapping():
    class FakeDelta: content = "bar"
    class FakeChoice: delta = FakeDelta()
    class FakeChunk: choices = [FakeChoice()]
    ev: StreamEvent = ChatCompletionsEventAdapter.adapt(FakeChunk())
    assert ev.type == "output_text.delta"
    assert ev.delta == "bar"

def test_chat_completed_when_no_delta():
    class FakeChunk: choices = []  # no delta available
    ev = ChatCompletionsEventAdapter.adapt(FakeChunk())
    assert ev.type == "response.completed"

def test_extract_text_returns_delta_or_empty():
    assert extract_text(StreamEvent(type="output_text.delta", delta="X")) == "X"
    assert extract_text(StreamEvent(type="response.completed")) == ""
