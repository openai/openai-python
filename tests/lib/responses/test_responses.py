from __future__ import annotations

from typing_extensions import TypeVar

import pytest
import pydantic
from respx import MockRouter
from inline_snapshot import snapshot

from openai import OpenAI, AsyncOpenAI
from openai._utils import assert_signatures_in_sync
from openai._models import construct_type_unchecked
from openai.types.responses import (
    ResponseCreatedEvent,
    ResponseTextDoneEvent,
    ResponseCompletedEvent as RawResponseCompletedEvent,
    ResponseIncompleteEvent,
    ResponseOutputItemAddedEvent,
    ResponseContentPartAddedEvent,
)
from openai.lib.streaming.responses._responses import ResponseStreamState

from ...conftest import base_url
from ..snapshots import make_snapshot_request

_T = TypeVar("_T")


class _StructuredText(pydantic.BaseModel):
    answer: str


def _response_payload(*, status: str, output: list[object] | None = None) -> dict[str, object]:
    return {
        "id": "resp_test",
        "object": "response",
        "created_at": 0,
        "model": "gpt-4.1",
        "output": output or [],
        "parallel_tool_calls": True,
        "temperature": None,
        "tool_choice": "auto",
        "tools": [],
        "top_p": None,
        "status": status,
    }


def _message_payload(*, text: str, status: str) -> dict[str, object]:
    return {
        "id": "msg_test",
        "type": "message",
        "role": "assistant",
        "status": status,
        "content": [
            {
                "type": "output_text",
                "text": text,
                "annotations": [],
                "logprobs": [],
            }
        ],
    }


def _start_response_stream(state: ResponseStreamState[_StructuredText]) -> None:
    state.handle_event(
        construct_type_unchecked(
            type_=ResponseCreatedEvent,
            value={
                "type": "response.created",
                "sequence_number": 0,
                "response": _response_payload(status="in_progress"),
            },
        )
    )
    state.handle_event(
        construct_type_unchecked(
            type_=ResponseOutputItemAddedEvent,
            value={
                "type": "response.output_item.added",
                "sequence_number": 1,
                "output_index": 0,
                "item": _message_payload(text="", status="in_progress"),
            },
        )
    )
    state.handle_event(
        construct_type_unchecked(
            type_=ResponseContentPartAddedEvent,
            value={
                "type": "response.content_part.added",
                "sequence_number": 2,
                "output_index": 0,
                "content_index": 0,
                "item_id": "msg_test",
                "part": {
                    "type": "output_text",
                    "text": "",
                    "annotations": [],
                    "logprobs": [],
                },
            },
        )
    )


# all the snapshots in this file are auto-generated from the live API
#
# you can update them with
#
# `OPENAI_LIVE=1 pytest --inline-snapshot=fix -p no:xdist -o addopts=""`


@pytest.mark.respx(base_url=base_url)
def test_output_text(client: OpenAI, respx_mock: MockRouter) -> None:
    response = make_snapshot_request(
        lambda c: c.responses.create(
            model="gpt-4o-mini",
            input="What's the weather like in SF?",
        ),
        content_snapshot=snapshot(
            '{"id": "resp_689a0b2545288193953c892439b42e2800b2e36c65a1fd4b", "object": "response", "created_at": 1754925861, "status": "completed", "background": false, "error": null, "incomplete_details": null, "instructions": null, "max_output_tokens": null, "max_tool_calls": null, "model": "gpt-4o-mini-2024-07-18", "output": [{"id": "msg_689a0b2637b08193ac478e568f49e3f900b2e36c65a1fd4b", "type": "message", "status": "completed", "content": [{"type": "output_text", "annotations": [], "logprobs": [], "text": "I can\'t provide real-time updates, but you can easily check the current weather in San Francisco using a weather website or app. Typically, San Francisco has cool, foggy summers and mild winters, so it\'s good to be prepared for variable weather!"}], "role": "assistant"}], "parallel_tool_calls": true, "previous_response_id": null, "prompt_cache_key": null, "reasoning": {"effort": null, "summary": null}, "safety_identifier": null, "service_tier": "default", "store": true, "temperature": 1.0, "text": {"format": {"type": "text"}, "verbosity": "medium"}, "tool_choice": "auto", "tools": [], "top_logprobs": 0, "top_p": 1.0, "truncation": "disabled", "usage": {"input_tokens": 14, "input_tokens_details": {"cached_tokens": 0}, "output_tokens": 50, "output_tokens_details": {"reasoning_tokens": 0}, "total_tokens": 64}, "user": null, "metadata": {}}'
        ),
        path="/responses",
        mock_client=client,
        respx_mock=respx_mock,
    )

    assert response.output_text == snapshot(
        "I can't provide real-time updates, but you can easily check the current weather in San Francisco using a weather website or app. Typically, San Francisco has cool, foggy summers and mild winters, so it's good to be prepared for variable weather!"
    )


def test_stream_output_text_done_defers_invalid_structured_parse() -> None:
    state = ResponseStreamState(text_format=_StructuredText, input_tools=[])
    _start_response_stream(state)

    events = state.handle_event(
        construct_type_unchecked(
            type_=ResponseTextDoneEvent,
            value={
                "type": "response.output_text.done",
                "sequence_number": 3,
                "output_index": 0,
                "content_index": 0,
                "item_id": "msg_test",
                "logprobs": [],
                "text": '{"answer":',
            },
        )
    )

    assert len(events) == 1
    assert events[0].type == "response.output_text.done"
    assert events[0].parsed is None

    incomplete_events = state.handle_event(
        construct_type_unchecked(
            type_=ResponseIncompleteEvent,
            value={
                "type": "response.incomplete",
                "sequence_number": 4,
                "response": {
                    **_response_payload(
                        status="incomplete",
                        output=[_message_payload(text='{"answer":', status="incomplete")],
                    ),
                    "incomplete_details": {"reason": "max_output_tokens"},
                },
            },
        )
    )
    assert incomplete_events[0].type == "response.incomplete"


def test_stream_output_text_done_preserves_structured_validation_errors() -> None:
    state = ResponseStreamState(text_format=_StructuredText, input_tools=[])
    _start_response_stream(state)

    with pytest.raises(pydantic.ValidationError):
        state.handle_event(
            construct_type_unchecked(
                type_=ResponseTextDoneEvent,
                value={
                    "type": "response.output_text.done",
                    "sequence_number": 3,
                    "output_index": 0,
                    "content_index": 0,
                    "item_id": "msg_test",
                    "logprobs": [],
                    "text": "{}",
                },
            )
        )


def test_stream_completed_response_still_raises_invalid_structured_parse() -> None:
    state = ResponseStreamState(text_format=_StructuredText, input_tools=[])
    _start_response_stream(state)

    state.handle_event(
        construct_type_unchecked(
            type_=ResponseTextDoneEvent,
            value={
                "type": "response.output_text.done",
                "sequence_number": 3,
                "output_index": 0,
                "content_index": 0,
                "item_id": "msg_test",
                "logprobs": [],
                "text": '{"answer":',
            },
        )
    )

    with pytest.raises(pydantic.ValidationError):
        state.handle_event(
            construct_type_unchecked(
                type_=RawResponseCompletedEvent,
                value={
                    "type": "response.completed",
                    "sequence_number": 4,
                    "response": _response_payload(
                        status="completed",
                        output=[_message_payload(text='{"answer":', status="completed")],
                    ),
                },
            )
        )


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_stream_method_definition_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    assert_signatures_in_sync(
        checking_client.responses.create,
        checking_client.responses.stream,
        exclude_params={"stream", "tools"},
    )


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_parse_method_definition_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    assert_signatures_in_sync(
        checking_client.responses.create,
        checking_client.responses.parse,
        exclude_params={"tools"},
    )
