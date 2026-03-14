"""Tests for optional logprobs in response event types.

Regression tests for https://github.com/openai/openai-python/issues/2489
Non-OpenAI providers may not include logprobs in streaming responses.
"""

from openai.types.responses.response_text_done_event import ResponseTextDoneEvent
from openai.types.responses.response_text_delta_event import ResponseTextDeltaEvent

_DELTA_BASE = {
    "content_index": 0,
    "delta": "Hello",
    "item_id": "item_1",
    "output_index": 0,
    "sequence_number": 1,
    "type": "response.output_text.delta",
}

_DONE_BASE = {
    "content_index": 0,
    "item_id": "item_1",
    "output_index": 0,
    "sequence_number": 2,
    "text": "Hello world",
    "type": "response.output_text.done",
}

_SAMPLE_LOGPROBS = [{"token": "Hello", "logprob": -0.1, "top_logprobs": None}]


class TestResponseTextDeltaEventLogprobs:
    def test_without_logprobs(self) -> None:
        event = ResponseTextDeltaEvent.model_validate(_DELTA_BASE)
        assert event.logprobs is None

    def test_with_logprobs(self) -> None:
        data = {**_DELTA_BASE, "logprobs": _SAMPLE_LOGPROBS}
        event = ResponseTextDeltaEvent.model_validate(data)
        assert event.logprobs is not None
        assert len(event.logprobs) == 1
        assert event.logprobs[0].token == "Hello"

    def test_with_empty_logprobs(self) -> None:
        data = {**_DELTA_BASE, "logprobs": []}
        event = ResponseTextDeltaEvent.model_validate(data)
        assert event.logprobs == []


class TestResponseTextDoneEventLogprobs:
    def test_without_logprobs(self) -> None:
        event = ResponseTextDoneEvent.model_validate(_DONE_BASE)
        assert event.logprobs is None

    def test_with_logprobs(self) -> None:
        data = {**_DONE_BASE, "logprobs": _SAMPLE_LOGPROBS}
        event = ResponseTextDoneEvent.model_validate(data)
        assert event.logprobs is not None
        assert len(event.logprobs) == 1
        assert event.logprobs[0].token == "Hello"

    def test_with_empty_logprobs(self) -> None:
        data = {**_DONE_BASE, "logprobs": []}
        event = ResponseTextDoneEvent.model_validate(data)
        assert event.logprobs == []
