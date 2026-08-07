"""Regression tests for ResponseStreamState null-output handling (issue #3325).

The chatgpt.com Codex backend sometimes sends `response.output: null` in the
consolidated `response.completed` event even when valid `output_item.done` events
were streamed earlier. These tests verify that:

1. Accumulated text/items survive when `response.completed.output` is `None`.
2. Authoritative done-event fields (status, text, arguments) are applied.
3. Parsed function arguments/text formats still run in the fallback path.
4. The no-prior-items case returns an empty output.
"""

from __future__ import annotations

from openai._types import omit
from openai._models import construct_type_unchecked
from openai.types.responses import (
    Response,
    ResponseStreamEvent as RawResponseStreamEvent,
)
from openai.lib.streaming.responses._responses import ResponseStreamState
from openai.types.responses.response_created_event import ResponseCreatedEvent
from openai.types.responses.response_completed_event import ResponseCompletedEvent
from openai.types.responses.response_output_item_done_event import (
    ResponseOutputItemDoneEvent,
)
from openai.types.responses.response_output_item_added_event import (
    ResponseOutputItemAddedEvent,
)
from openai.types.responses.response_function_call_arguments_done_event import (
    ResponseFunctionCallArgumentsDoneEvent,
)


def _make_created_event() -> RawResponseStreamEvent:
    """Create a minimal `response.created` event to seed the stream state.

    The ``response`` field is passed as the *model object* (not a dict) so that
    ``construct_type_unchecked`` preserves it as a ``Response`` instance.
    ``ResponseStreamState._create_initial_response`` calls
    ``event.response.to_dict()``, which would raise ``AttributeError`` on a
    plain dict.
    """
    response = construct_type_unchecked(
        type_=Response,
        value={
            "id": "resp_test",
            "object": "response",
            "created_at": 1754925861,
            "status": "in_progress",
            "model": "gpt-4o",
            "output": [],
        },
    )
    return construct_type_unchecked(
        type_=ResponseCreatedEvent,
        value={
            "type": "response.created",
            "sequence_number": 0,
            "response": response,
        },
    )


def _make_output_item_added_message() -> RawResponseStreamEvent:
    """Create a `response.output_item.added` event for a message item."""
    return construct_type_unchecked(
        type_=ResponseOutputItemAddedEvent,
        value={
            "type": "response.output_item.added",
            "sequence_number": 1,
            "output_index": 0,
            "item": {
                "type": "message",
                "id": "msg_001",
                "status": "in_progress",
                "role": "assistant",
                "content": [],
            },
        },
    )


def _make_output_item_done_message(text: str = "Hello world") -> RawResponseStreamEvent:
    """Create a `response.output_item.done` event for a message."""
    return construct_type_unchecked(
        type_=ResponseOutputItemDoneEvent,
        value={
            "type": "response.output_item.done",
            "sequence_number": 4,
            "output_index": 0,
            "item": {
                "type": "message",
                "id": "msg_001",
                "status": "completed",
                "role": "assistant",
                "content": [
                    {
                        "type": "output_text",
                        "text": text,
                        "annotations": [],
                        "logprobs": [],
                    }
                ],
            },
        },
    )


def _make_completed_event_null_output() -> RawResponseStreamEvent:
    """Create a `response.completed` event with `output: null`.

    Build the event from a raw dict to avoid calling ``to_dict()`` on a
    ``Response(output=None)``, which would trigger a Pydantic serializer
    warning (and the repo's pytest config treats warnings as errors).
    """
    return construct_type_unchecked(
        type_=ResponseCompletedEvent,
        value={
            "type": "response.completed",
            "sequence_number": 5,
            "response": {
                "id": "resp_test",
                "object": "response",
                "created_at": 1754925861,
                "status": "completed",
                "model": "gpt-4o",
                "output": None,  # The bug: output is null
            },
        },
    )


def _make_completed_event_with_output() -> RawResponseStreamEvent:
    """Create a `response.completed` event with normal output."""
    response = construct_type_unchecked(
        type_=Response,
        value={
            "id": "resp_test",
            "object": "response",
            "created_at": 1754925861,
            "status": "completed",
            "model": "gpt-4o",
            "output": [
                {
                    "type": "message",
                    "id": "msg_001",
                    "status": "completed",
                    "role": "assistant",
                    "content": [
                        {
                            "type": "output_text",
                            "text": "Hello world",
                            "annotations": [],
                            "logprobs": [],
                        }
                    ],
                }
            ],
        },
    )
    return construct_type_unchecked(
        type_=ResponseCompletedEvent,
        value={
            "type": "response.completed",
            "sequence_number": 5,
            "response": response,
        },
    )


def _make_completed_event_empty_output() -> RawResponseStreamEvent:
    """Create a `response.completed` event with empty output list."""
    response = construct_type_unchecked(
        type_=Response,
        value={
            "id": "resp_test",
            "object": "response",
            "created_at": 1754925861,
            "status": "completed",
            "model": "gpt-4o",
            "output": [],
        },
    )
    return construct_type_unchecked(
        type_=ResponseCompletedEvent,
        value={
            "type": "response.completed",
            "sequence_number": 5,
            "response": response,
        },
    )


def _make_state() -> ResponseStreamState:
    """Create a ResponseStreamState with no text format or tools."""
    return ResponseStreamState(
        input_tools=omit,
        text_format=omit,
    )


class TestNullOutputFallback:
    """Tests for the null-output fallback path in ResponseStreamState."""

    def test_accumulated_text_survives_null_output(self):
        """When response.completed has output=None, the accumulated text
        from done events must survive in the final parsed response."""
        state = _make_state()
        state.handle_event(_make_created_event())
        state.handle_event(_make_output_item_added_message())
        state.handle_event(_make_output_item_done_message("Hello world"))

        events = state.handle_event(_make_completed_event_null_output())

        # The completed event should produce a ResponseCompletedEvent
        assert len(events) == 1
        assert events[0].type == "response.completed"

        response = events[0].response
        # The output should contain the accumulated message, not be empty
        assert len(response.output) == 1
        assert response.output[0].type == "message"
        assert response.output[0].content[0].text == "Hello world"

    def test_done_event_status_survives_null_output(self):
        """The authoritative status from output_item.done must survive
        in the null-output fallback path."""
        state = _make_state()
        state.handle_event(_make_created_event())
        state.handle_event(_make_output_item_added_message())
        state.handle_event(_make_output_item_done_message("Hello world"))

        events = state.handle_event(_make_completed_event_null_output())

        response = events[0].response
        # The status should be "completed" from the done event, not "in_progress"
        assert response.output[0].status == "completed"

    def test_no_prior_items_returns_empty_output(self):
        """When response.completed has output=None and no items were
        accumulated, the result should be an empty output list."""
        state = _make_state()
        state.handle_event(_make_created_event())

        events = state.handle_event(_make_completed_event_null_output())

        assert len(events) == 1
        assert events[0].type == "response.completed"
        # No items were accumulated, so output should be empty
        assert len(events[0].response.output) == 0

    def test_normal_completed_with_output_still_works(self):
        """The normal path (output is not None) should still work correctly."""
        state = _make_state()
        state.handle_event(_make_created_event())
        state.handle_event(_make_output_item_added_message())
        state.handle_event(_make_output_item_done_message("Hello world"))

        events = state.handle_event(_make_completed_event_with_output())

        assert len(events) == 1
        assert events[0].type == "response.completed"
        response = events[0].response
        assert len(response.output) == 1
        assert response.output[0].type == "message"
        assert response.output[0].content[0].text == "Hello world"

    def test_empty_output_completed_still_works(self):
        """An empty output list (not None) should also produce empty output."""
        state = _make_state()
        state.handle_event(_make_created_event())

        events = state.handle_event(_make_completed_event_empty_output())

        assert len(events) == 1
        assert events[0].type == "response.completed"
        assert len(events[0].response.output) == 0

    def test_dict_response_coerced_before_null_output_check(self):
        """When the discriminator fallback leaves event.response as a raw dict
        (because validation of Response(output=None) failed), the null-output
        guard must coerce it to a Response model before dereferencing .output
        instead of raising AttributeError."""
        state = _make_state()
        state.handle_event(_make_created_event())
        state.handle_event(_make_output_item_added_message())
        state.handle_event(_make_output_item_done_message("Hello world"))

        # Build a completed event where `response` is a plain dict (simulating
        # the discriminator fallback from construct_type on invalid null output)
        completed_with_dict_response = construct_type_unchecked(
            type_=ResponseCompletedEvent,
            value={
                "type": "response.completed",
                "sequence_number": 5,
                "response": {
                    "id": "resp_test",
                    "object": "response",
                    "created_at": 1754925861,
                    "status": "completed",
                    "model": "gpt-4o",
                    "output": None,
                },
            },
        )

        events = state.handle_event(completed_with_dict_response)

        assert len(events) == 1
        assert events[0].type == "response.completed"
        response = events[0].response
        assert len(response.output) == 1
        assert response.output[0].type == "message"
        assert response.output[0].content[0].text == "Hello world"


class TestFunctionCallArgumentsDone:
    """Tests for the function_call_arguments.done event handling."""

    def _make_function_call_added(self) -> RawResponseStreamEvent:
        return construct_type_unchecked(
            type_=ResponseOutputItemAddedEvent,
            value={
                "type": "response.output_item.added",
                "sequence_number": 1,
                "output_index": 0,
                "item": {
                    "type": "function_call",
                    "id": "fc_001",
                    "call_id": "call_001",
                    "name": "get_weather",
                    "arguments": "",
                    "status": "in_progress",
                },
            },
        )

    def _make_function_call_arguments_done(self, args: str = '{"city": "SF"}') -> RawResponseStreamEvent:
        return construct_type_unchecked(
            type_=ResponseFunctionCallArgumentsDoneEvent,
            value={
                "type": "response.function_call_arguments.done",
                "sequence_number": 2,
                "output_index": 0,
                "item_id": "fc_001",
                "arguments": args,
            },
        )

    def _make_function_call_item_done(self, args: str = '{"city": "SF"}') -> RawResponseStreamEvent:
        return construct_type_unchecked(
            type_=ResponseOutputItemDoneEvent,
            value={
                "type": "response.output_item.done",
                "sequence_number": 3,
                "output_index": 0,
                "item": {
                    "type": "function_call",
                    "id": "fc_001",
                    "call_id": "call_001",
                    "name": "get_weather",
                    "arguments": args,
                    "status": "completed",
                },
            },
        )

    def _make_completed_null_output(self) -> RawResponseStreamEvent:
        """Build from a raw dict to avoid serializing the invalid null output."""
        return construct_type_unchecked(
            type_=ResponseCompletedEvent,
            value={
                "type": "response.completed",
                "sequence_number": 4,
                "response": {
                    "id": "resp_test",
                    "object": "response",
                    "created_at": 1754925861,
                    "status": "completed",
                    "model": "gpt-4o",
                    "output": None,
                },
            },
        )

    def test_function_call_arguments_survive_null_output(self):
        """Finalized function call arguments from the done event must
        survive in the null-output fallback path."""
        state = _make_state()
        state.handle_event(_make_created_event())
        state.handle_event(self._make_function_call_added())
        state.handle_event(self._make_function_call_arguments_done('{"city": "SF"}'))
        state.handle_event(self._make_function_call_item_done('{"city": "SF"}'))

        events = state.handle_event(self._make_completed_null_output())

        response = events[0].response
        assert len(response.output) == 1
        assert response.output[0].type == "function_call"
        assert response.output[0].arguments == '{"city": "SF"}'
        assert response.output[0].name == "get_weather"
