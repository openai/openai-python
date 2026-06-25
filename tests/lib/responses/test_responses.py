from __future__ import annotations

from typing_extensions import TypeVar

import pytest
from respx import MockRouter
from inline_snapshot import snapshot

from openai import OpenAI, AsyncOpenAI
from openai._types import NOT_GIVEN
from openai.types.responses.response import Response
from openai.types.responses.response_output_text import ResponseOutputText
from openai.types.responses.response_output_message import ResponseOutputMessage
from openai.lib.streaming.responses._responses import ResponseStreamState
from openai._utils import assert_signatures_in_sync

from ...conftest import base_url
from ..snapshots import make_snapshot_request

_T = TypeVar("_T")

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


def test_output_text_tolerates_none_output() -> None:
    response = Response.construct(
        id="resp_test",
        object="response",
        created_at=0,
        model="gpt-test",
        output=None,
        parallel_tool_calls=False,
        tool_choice="auto",
        tools=[],
    )

    assert response.output_text == ""


def test_parse_response_tolerates_none_output() -> None:
    from openai.lib._parsing._responses import parse_response
    response = Response.construct(
        id="resp_test",
        object="response",
        created_at=0,
        model="gpt-test",
        output=None,
        parallel_tool_calls=False,
        tool_choice="auto",
        tools=[],
    )

    parsed = parse_response(text_format=NOT_GIVEN, input_tools=NOT_GIVEN, response=response)

    assert parsed.output == []


@pytest.mark.parametrize("terminal_output", [None, []])
def test_response_stream_preserves_snapshot_when_terminal_output_is_missing(terminal_output: object) -> None:
    state = ResponseStreamState(input_tools=[], text_format=NOT_GIVEN)

    state.handle_event(
        _Event(
            type="response.created",
            response=Response.construct(
                id="resp_test",
                object="response",
                created_at=0,
                model="gpt-test",
                output=[],
                parallel_tool_calls=False,
                tool_choice="auto",
                tools=[],
            ),
        )
    )
    state.handle_event(
        _Event(
            type="response.output_item.added",
            output_index=0,
            item=ResponseOutputMessage.construct(
                id="msg_test",
                type="message",
                role="assistant",
                status="in_progress",
                content=[],
            ),
        )
    )
    state.handle_event(
        _Event(
            type="response.content_part.added",
            output_index=0,
            content_index=0,
            part=ResponseOutputText.construct(type="output_text", text="", annotations=[]),
        )
    )
    state.handle_event(
        _Event(
            type="response.output_text.delta",
            output_index=0,
            content_index=0,
            item_id="msg_test",
            delta="streamed text",
            sequence_number=1,
            logprobs=[],
        )
    )

    events = state.handle_event(
        _Event(
            type="response.completed",
            sequence_number=2,
            response=Response.construct(
                id="resp_test",
                object="response",
                created_at=0,
                model="gpt-test",
                output=terminal_output,
                parallel_tool_calls=False,
                tool_choice="auto",
                tools=[],
            ),
        )
    )

    completed = events[0].response
    assert completed.output_text == "streamed text"
    assert completed.output[0].content[0].text == "streamed text"


class _Event:
    def __init__(self, **kwargs: object) -> None:
        self.__dict__.update(kwargs)
