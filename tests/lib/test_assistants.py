from __future__ import annotations

from types import SimpleNamespace

import pytest

from openai import OpenAI, AsyncOpenAI
from openai._utils import assert_signatures_in_sync


class _MockPollResponse:
    def __init__(self) -> None:
        self.headers: dict[str, str] = {}

    def parse(self) -> SimpleNamespace:
        return SimpleNamespace(status="completed")


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


def test_poll_adds_no_cache_header(client: OpenAI, monkeypatch: pytest.MonkeyPatch) -> None:
    seen_headers: dict[str, str] | None = None

    def mock_retrieve(
        *,
        thread_id: str,
        run_id: str,
        extra_headers: dict[str, str] | None = None,
        extra_body: object = None,
        extra_query: object = None,
        timeout: object = None,
    ) -> _MockPollResponse:
        del thread_id, run_id, extra_body, extra_query, timeout
        nonlocal seen_headers
        seen_headers = dict(extra_headers or {})
        return _MockPollResponse()

    monkeypatch.setattr(client.beta.threads.runs.with_raw_response, "retrieve", mock_retrieve)

    with pytest.warns(DeprecationWarning):
        run = client.beta.threads.runs.poll("run_id", thread_id="thread_id")

    assert run.status == "completed"
    assert seen_headers is not None
    assert seen_headers["X-Stainless-Poll-Helper"] == "true"
    assert seen_headers["Cache-Control"] == "no-cache"


def test_poll_allows_overriding_cache_control_header(client: OpenAI, monkeypatch: pytest.MonkeyPatch) -> None:
    seen_headers: dict[str, str] | None = None

    def mock_retrieve(
        *,
        thread_id: str,
        run_id: str,
        extra_headers: dict[str, str] | None = None,
        extra_body: object = None,
        extra_query: object = None,
        timeout: object = None,
    ) -> _MockPollResponse:
        del thread_id, run_id, extra_body, extra_query, timeout
        nonlocal seen_headers
        seen_headers = dict(extra_headers or {})
        return _MockPollResponse()

    monkeypatch.setattr(client.beta.threads.runs.with_raw_response, "retrieve", mock_retrieve)

    with pytest.warns(DeprecationWarning):
        client.beta.threads.runs.poll(
            "run_id",
            thread_id="thread_id",
            extra_headers={"Cache-Control": "max-age=60"},
        )

    assert seen_headers is not None
    assert seen_headers["X-Stainless-Poll-Helper"] == "true"
    assert seen_headers["Cache-Control"] == "max-age=60"


async def test_async_poll_adds_no_cache_header(async_client: AsyncOpenAI, monkeypatch: pytest.MonkeyPatch) -> None:
    seen_headers: dict[str, str] | None = None

    async def mock_retrieve(
        *,
        thread_id: str,
        run_id: str,
        extra_headers: dict[str, str] | None = None,
        extra_body: object = None,
        extra_query: object = None,
        timeout: object = None,
    ) -> _MockPollResponse:
        del thread_id, run_id, extra_body, extra_query, timeout
        nonlocal seen_headers
        seen_headers = dict(extra_headers or {})
        return _MockPollResponse()

    monkeypatch.setattr(async_client.beta.threads.runs.with_raw_response, "retrieve", mock_retrieve)

    with pytest.warns(DeprecationWarning):
        run = await async_client.beta.threads.runs.poll("run_id", thread_id="thread_id")

    assert run.status == "completed"
    assert seen_headers is not None
    assert seen_headers["X-Stainless-Poll-Helper"] == "true"
    assert seen_headers["Cache-Control"] == "no-cache"
