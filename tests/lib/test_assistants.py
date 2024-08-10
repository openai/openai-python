from __future__ import annotations

import pytest

from openai import OpenAI, AsyncOpenAI
from openai._utils import assert_signatures_in_sync


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_create_and_run_poll_method_definition_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    assert_signatures_in_sync(
        checking_client.beta.threads.create_and_run,
        checking_client.beta.threads.create_and_run_poll,
        exclude_params={"stream"},
    )


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_create_and_run_stream_method_definition_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    assert_signatures_in_sync(
        checking_client.beta.threads.create_and_run,
        checking_client.beta.threads.create_and_run_stream,
        exclude_params={"stream"},
    )


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_run_stream_method_definition_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    assert_signatures_in_sync(
        checking_client.beta.threads.runs.create,
        checking_client.beta.threads.runs.stream,
        exclude_params={"stream"},
    )


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_create_and_poll_method_definition_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    assert_signatures_in_sync(
        checking_client.beta.threads.runs.create,
        checking_client.beta.threads.runs.create_and_poll,
        exclude_params={"stream"},
    )
