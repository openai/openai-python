from __future__ import annotations

import asyncio
from typing import Any, cast
from unittest import mock

import pytest

from openai import OpenAI, AsyncOpenAI
from openai.lib import _files as file_helpers
from openai._models import construct_type_unchecked
from openai.resources.files import Files, AsyncFiles
from openai.types.file_object import FileObject

FILE_ID = "file-synthetic"


def make_file(status: str) -> FileObject:
    return construct_type_unchecked(type_=FileObject, value={"id": FILE_ID, "status": status})


@pytest.fixture(params=["sync", "async"])
def files_resource(request: pytest.FixtureRequest) -> Files | AsyncFiles:
    client = mock.Mock()
    if request.param == "sync":
        return Files(cast(OpenAI, client))
    return AsyncFiles(cast(AsyncOpenAI, client))


async def wait(resource: Files | AsyncFiles, **kwargs: Any) -> FileObject:
    if isinstance(resource, AsyncFiles):
        return await resource.wait_for_processing(FILE_ID, **kwargs)
    return resource.wait_for_processing(FILE_ID, **kwargs)


@pytest.mark.parametrize("status", ["processed", "error", "deleted"])
async def test_terminal_result(files_resource: Files | AsyncFiles, status: str) -> None:
    terminal = make_file(status)
    with (
        mock.patch.object(files_resource, "retrieve", return_value=terminal) as retrieve,
        mock.patch.object(files_resource, "_sleep") as sleep,
    ):
        assert await wait(files_resource) is terminal
        retrieve.assert_called_once_with(FILE_ID)
        sleep.assert_not_called()


async def test_poll_until_processed(files_resource: Files | AsyncFiles) -> None:
    terminal = make_file("processed")
    with (
        mock.patch.object(files_resource, "retrieve", side_effect=[make_file("uploaded"), terminal]) as retrieve,
        mock.patch.object(files_resource, "_sleep") as sleep,
    ):
        assert await wait(files_resource, poll_interval=0.25) is terminal
        assert retrieve.call_count == 2
        sleep.assert_called_once_with(0.25)


async def test_timeout(files_resource: Files | AsyncFiles) -> None:
    with (
        mock.patch.object(file_helpers, "time") as clock,
        mock.patch.object(files_resource, "retrieve", return_value=make_file("uploaded")),
        mock.patch.object(files_resource, "_sleep"),
    ):
        clock.time.side_effect = [0.0, 11.0]
        with pytest.raises(RuntimeError, match=f"Giving up on waiting for file {FILE_ID}"):
            await wait(files_resource, max_wait_seconds=10)


async def test_retrieve_error_propagates(files_resource: Files | AsyncFiles) -> None:
    error = RuntimeError("synthetic retrieval failure")
    with mock.patch.object(files_resource, "retrieve", side_effect=error):
        with pytest.raises(RuntimeError) as caught:
            await wait(files_resource)
        assert caught.value is error


async def test_async_cancellation_propagates() -> None:
    resource = AsyncFiles(cast(AsyncOpenAI, mock.Mock()))
    cancellation = asyncio.CancelledError()
    with (
        mock.patch.object(resource, "retrieve", return_value=make_file("uploaded")),
        mock.patch.object(resource, "_sleep", side_effect=cancellation),
    ):
        with pytest.raises(asyncio.CancelledError) as caught:
            await resource.wait_for_processing(FILE_ID)
        assert caught.value is cancellation
