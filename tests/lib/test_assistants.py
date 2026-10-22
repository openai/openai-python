from __future__ import annotations

from typing import Any, cast

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from tests.respx2 import MockRouter
from openai._utils import assert_signatures_in_sync

from ..conftest import base_url


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
@pytest.mark.parametrize("helper", ["stream", "submit_tool_outputs_stream", "create_and_run_stream"])
@pytest.mark.respx2(base_url=base_url)
@pytest.mark.filterwarnings("ignore:The Assistants API is deprecated:DeprecationWarning")
async def test_stream_error_event(
    sync: bool, helper: str, client: OpenAI, async_client: AsyncOpenAI, respx2_mock: MockRouter
) -> None:
    body = 'event: error\ndata: {"message":"Example failure","type":"server_error","code":null,"param":null}\n\n'
    respx2_mock.post().mock(
        return_value=httpx2.Response(200, text=body + "data: [DONE]\n\n", headers={"content-type": "text/event-stream"})
    )
    threads = cast(Any, client if sync else async_client).beta.threads
    if helper == "create_and_run_stream":
        manager = threads.create_and_run_stream(assistant_id="asst_test")
    elif helper == "submit_tool_outputs_stream":
        manager = threads.runs.submit_tool_outputs_stream(thread_id="thread_test", run_id="run_test", tool_outputs=[])
    else:
        manager = threads.runs.stream(thread_id="thread_test", assistant_id="asst_test")

    if sync:
        with manager as stream:
            events = list(stream)
    else:
        async with manager as stream:
            events = [event async for event in stream]

    assert len(events) == 1
    assert events[0].event == "error"
    assert events[0].data.message == "Example failure"


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_create_and_run_poll_method_definition_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    assert_signatures_in_sync(
        checking_client.beta.threads.create_and_run,  # pyright: ignore[reportDeprecated]
        checking_client.beta.threads.create_and_run_poll,
        exclude_params={"stream"},
    )


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_create_and_run_stream_method_definition_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    assert_signatures_in_sync(
        checking_client.beta.threads.create_and_run,  # pyright: ignore[reportDeprecated]
        checking_client.beta.threads.create_and_run_stream,
        exclude_params={"stream"},
    )


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_run_stream_method_definition_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    assert_signatures_in_sync(
        checking_client.beta.threads.runs.create,  # pyright: ignore[reportDeprecated]
        checking_client.beta.threads.runs.stream,  # pyright: ignore[reportDeprecated]
        exclude_params={"stream"},
    )


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_create_and_poll_method_definition_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    assert_signatures_in_sync(
        checking_client.beta.threads.runs.create,  # pyright: ignore[reportDeprecated]
        checking_client.beta.threads.runs.create_and_poll,  # pyright: ignore[reportDeprecated]
        exclude_params={"stream"},
    )
