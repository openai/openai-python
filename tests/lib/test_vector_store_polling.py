from __future__ import annotations

import asyncio
from typing import Any, cast
from unittest import mock
from typing_extensions import TypeAlias

import pytest

from openai._types import Omit, omit
from openai._models import construct_type_unchecked
from openai.resources.vector_stores.files import Files, AsyncFiles
from openai.resources.vector_stores.file_batches import FileBatches, AsyncFileBatches
from openai.types.vector_stores.vector_store_file import VectorStoreFile
from openai.types.vector_stores.vector_store_file_batch import VectorStoreFileBatch

PollResource: TypeAlias = Files | AsyncFiles | FileBatches | AsyncFileBatches
ITEM_ID = "item-synthetic"
VECTOR_STORE_ID = "vs-synthetic"


@pytest.fixture(params=[Files, AsyncFiles, FileBatches, AsyncFileBatches])
def resource(request: pytest.FixtureRequest) -> PollResource:
    resource_type = cast(type[PollResource], request.param)
    return resource_type(cast(Any, mock.Mock()))


def raw_response(resource: PollResource, *, pending: bool = False, headers: dict[str, str] | None = None) -> mock.Mock:
    result: VectorStoreFile | VectorStoreFileBatch
    if isinstance(resource, (Files, AsyncFiles)):
        result = construct_type_unchecked(
            type_=VectorStoreFile, value={"id": ITEM_ID, "status": "in_progress" if pending else "completed"}
        )
    else:
        result = construct_type_unchecked(
            type_=VectorStoreFileBatch, value={"id": ITEM_ID, "file_counts": {"in_progress": int(pending)}}
        )
    return mock.Mock(headers=headers or {}, parse=mock.Mock(return_value=result))


async def poll(resource: PollResource, interval: int | Omit = omit) -> VectorStoreFile | VectorStoreFileBatch:
    if isinstance(resource, (AsyncFiles, AsyncFileBatches)):
        return await resource.poll(ITEM_ID, vector_store_id=VECTOR_STORE_ID, poll_interval_ms=interval)
    return resource.poll(ITEM_ID, vector_store_id=VECTOR_STORE_ID, poll_interval_ms=interval)


async def test_terminal_result(resource: PollResource) -> None:
    terminal = raw_response(resource)
    with (
        mock.patch.object(resource.with_raw_response, "retrieve", return_value=terminal) as retrieve,
        mock.patch.object(resource, "_sleep") as sleep,
    ):
        assert await poll(resource) is terminal.parse.return_value
        retrieve.assert_called_once_with(
            ITEM_ID, vector_store_id=VECTOR_STORE_ID, extra_headers={"X-Stainless-Poll-Helper": "true"}
        )
        sleep.assert_not_called()


@pytest.mark.parametrize(
    ("interval", "headers", "seconds"),
    [(omit, {}, 1.0), (omit, {"openai-poll-after-ms": "2000"}, 2.0), (250, {"openai-poll-after-ms": "2000"}, 0.25)],
    ids=["default", "server-hint", "explicit"],
)
async def test_poll_interval_and_headers(
    resource: PollResource, interval: int | Omit, headers: dict[str, str], seconds: float
) -> None:
    terminal = raw_response(resource)
    with (
        mock.patch.object(
            resource.with_raw_response,
            "retrieve",
            side_effect=[raw_response(resource, pending=True, headers=headers), terminal],
        ) as retrieve,
        mock.patch.object(resource, "_sleep") as sleep,
    ):
        assert await poll(resource, interval) is terminal.parse.return_value
        expected_headers = {"X-Stainless-Poll-Helper": "true"}
        if isinstance(interval, int):
            expected_headers["X-Stainless-Custom-Poll-Interval"] = str(interval)
        assert (
            retrieve.call_args_list
            == [mock.call(ITEM_ID, vector_store_id=VECTOR_STORE_ID, extra_headers=expected_headers)] * 2
        )
        sleep.assert_called_once_with(seconds)


async def test_retrieve_error_propagates(resource: PollResource) -> None:
    error = RuntimeError("synthetic retrieval failure")
    with mock.patch.object(resource.with_raw_response, "retrieve", side_effect=error):
        with pytest.raises(RuntimeError) as caught:
            await poll(resource)
        assert caught.value is error


@pytest.mark.parametrize("resource_type", [AsyncFiles, AsyncFileBatches])
async def test_async_cancellation_propagates(resource_type: type[AsyncFiles] | type[AsyncFileBatches]) -> None:
    resource = resource_type(cast(Any, mock.Mock()))
    cancellation = asyncio.CancelledError()
    with (
        mock.patch.object(resource.with_raw_response, "retrieve", return_value=raw_response(resource, pending=True)),
        mock.patch.object(resource, "_sleep", side_effect=cancellation),
    ):
        with pytest.raises(asyncio.CancelledError) as caught:
            await poll(resource)
        assert caught.value is cancellation
