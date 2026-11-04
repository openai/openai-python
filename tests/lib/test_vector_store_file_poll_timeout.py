from __future__ import annotations

from typing import Any, cast
from unittest import mock

import pytest

from openai import OpenAI, AsyncOpenAI
from openai._types import omit
from openai._models import construct_type_unchecked
from openai.resources.vector_stores.files import Files, AsyncFiles
from openai.types.vector_stores.vector_store_file import VectorStoreFile

FILE_ID = "file-synthetic"
VECTOR_STORE_ID = "vs-synthetic"


class Clock:
    now: float = 0

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.now += seconds


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> Clock:
    clock = Clock()
    monkeypatch.setattr("openai.lib._vector_stores.time", clock)
    return clock


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def resource(request: pytest.FixtureRequest, client: OpenAI, async_client: AsyncOpenAI) -> Files | AsyncFiles:
    return (async_client if request.param else client).vector_stores.files


def response(status: str = "in_progress") -> mock.Mock:
    file = construct_type_unchecked(type_=VectorStoreFile, value={"id": FILE_ID, "status": status})
    return mock.Mock(headers={}, parse=mock.Mock(return_value=file))


async def call(resource: Files | AsyncFiles, method: str = "poll", **kwargs: Any) -> VectorStoreFile:
    params = {"vector_store_id": VECTOR_STORE_ID, **kwargs}
    if method == "upload_and_poll":
        params["file"] = ("probe.md", b"synthetic content")
    else:
        params["file_id"] = FILE_ID
    result = getattr(resource, method)(**params)
    if isinstance(resource, AsyncFiles):
        result = await result
    return cast(VectorStoreFile, result)


@pytest.mark.parametrize("interval", [omit, 250], ids=["server-hint", "explicit"])
async def test_deadline_caps_sleep_and_prevents_next_request(
    resource: Files | AsyncFiles, clock: Clock, interval: Any
) -> None:
    pending = response()
    pending.headers = {"openai-poll-after-ms": "10000"}
    with (
        mock.patch.object(resource.with_raw_response, "retrieve", return_value=pending) as retrieve,
        mock.patch.object(resource, "_sleep", side_effect=clock.sleep) as sleep,
    ):
        with pytest.raises(TimeoutError, match=FILE_ID):
            await call(resource, max_wait_seconds=0.625, poll_interval_ms=interval)
        assert clock.now == 0.625
        assert retrieve.call_count == (1 if interval is omit else 3)
        assert [args.args[0] for args in sleep.call_args_list] == ([0.625] if interval is omit else [0.25, 0.25, 0.125])


@pytest.mark.parametrize("request_seconds", [0.5, 3.0])
async def test_request_time_counts_toward_deadline(
    resource: Files | AsyncFiles, clock: Clock, request_seconds: float
) -> None:
    def retrieve(*_args: Any, **_kwargs: Any) -> mock.Mock:
        clock.now += request_seconds
        return response()

    with (
        mock.patch.object(resource.with_raw_response, "retrieve", side_effect=retrieve) as get,
        mock.patch.object(resource, "_sleep", side_effect=clock.sleep) as sleep,
    ):
        with pytest.raises(TimeoutError):
            await call(resource, max_wait_seconds=2.5)
        assert get.call_count == (2 if request_seconds == 0.5 else 1)
        assert [args.args[0] for args in sleep.call_args_list] == ([1.0, 0.5] if request_seconds == 0.5 else [])
        # Preserve the client's per-request timeout and retry policy.
        assert all("timeout" not in args.kwargs for args in get.call_args_list)


@pytest.mark.parametrize("status", ["completed", "failed", "cancelled"])
async def test_terminal_result_is_preserved(resource: Files | AsyncFiles, clock: Clock, status: str) -> None:
    terminal = response(status)

    def retrieve(*_args: Any, **_kwargs: Any) -> mock.Mock:
        clock.now += 2
        return terminal

    with (
        mock.patch.object(resource.with_raw_response, "retrieve", side_effect=retrieve),
        mock.patch.object(resource, "_sleep") as sleep,
    ):
        # A terminal response from an in-flight request is still useful after expiry.
        assert await call(resource, max_wait_seconds=1) is terminal.parse.return_value
        sleep.assert_not_called()


async def test_omitted_limit_preserves_unbounded_wait(resource: Files | AsyncFiles, clock: Clock) -> None:
    terminal = response("completed")
    with (
        mock.patch.object(resource.with_raw_response, "retrieve", side_effect=[response(), response(), terminal]),
        mock.patch.object(resource, "_sleep", side_effect=clock.sleep),
    ):
        assert await call(resource, poll_interval_ms=3600000) is terminal.parse.return_value
        assert clock.now == 7200


@pytest.mark.parametrize("method", ["poll", "create_and_poll", "upload_and_poll"])
@pytest.mark.parametrize("limit", [-1, float("nan"), float("inf"), -float("inf")])
async def test_invalid_limit_fails_before_side_effects(resource: Files | AsyncFiles, method: str, limit: float) -> None:
    with (
        mock.patch.object(resource.with_raw_response, "retrieve") as retrieve,
        mock.patch.object(resource, "create") as attach,
        mock.patch.object(resource._client.files, "create") as upload,
    ):
        with pytest.raises(ValueError, match="finite, non-negative"):
            await call(resource, method, max_wait_seconds=limit)
        retrieve.assert_not_called()
        attach.assert_not_called()
        upload.assert_not_called()


async def test_zero_limit_prevents_polling(resource: Files | AsyncFiles, clock: Clock) -> None:
    with (
        mock.patch.object(resource.with_raw_response, "retrieve") as retrieve,
        mock.patch.object(resource, "_sleep") as sleep,
    ):
        with pytest.raises(TimeoutError):
            await call(resource, max_wait_seconds=0)
        assert clock.now == 0
        retrieve.assert_not_called()
        sleep.assert_not_called()


@pytest.mark.parametrize("method", ["create_and_poll", "upload_and_poll"])
async def test_helpers_start_deadline_after_upload_and_attachment(
    resource: Files | AsyncFiles, clock: Clock, method: str
) -> None:
    def create(*_args: Any, **kwargs: Any) -> mock.Mock:
        assert "max_wait_seconds" not in kwargs
        clock.now += 10
        return mock.Mock(id=FILE_ID)

    with (
        mock.patch.object(resource._client.files, "create", side_effect=create) as upload,
        mock.patch.object(resource, "create", side_effect=create) as attach,
        mock.patch.object(resource.with_raw_response, "retrieve", return_value=response()) as retrieve,
        mock.patch.object(resource, "_sleep", side_effect=clock.sleep),
    ):
        with pytest.raises(TimeoutError):
            await call(resource, method, max_wait_seconds=0.5)
        assert upload.call_count == (1 if method == "upload_and_poll" else 0)
        attach.assert_called_once()
        retrieve.assert_called_once()
        assert clock.now == (20.5 if method == "upload_and_poll" else 10.5)
