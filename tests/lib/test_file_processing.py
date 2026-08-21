from __future__ import annotations

import asyncio
import inspect
from types import SimpleNamespace
from typing import Any, Callable, cast
from unittest import mock

import pytest

from openai import OpenAI, AsyncOpenAI
from openai.lib import _files as file_helpers
from openai._models import construct_type_unchecked
from openai.resources.files import Files, AsyncFiles
from openai.types.file_object import FileObject

FILE_ID = "file-synthetic"


def make_file(status: str) -> FileObject:
    return construct_type_unchecked(
        type_=FileObject,
        value={
            "id": FILE_ID,
            "bytes": 0,
            "created_at": 0,
            "filename": "synthetic.txt",
            "object": "file",
            "purpose": "user_data",
            "status": status,
        },
    )


@pytest.fixture(params=["sync", "async"])
def files_resource(request: pytest.FixtureRequest) -> Files | AsyncFiles:
    client = mock.Mock()
    if request.param == "sync":
        return Files(cast(OpenAI, client))
    return AsyncFiles(cast(AsyncOpenAI, client))


def configure(
    monkeypatch: pytest.MonkeyPatch,
    resource: Files | AsyncFiles,
    *,
    responses: list[FileObject | BaseException],
    times: list[float],
    on_sleep: Callable[[float], None] | None = None,
) -> list[tuple[str, object]]:
    events: list[tuple[str, object]] = []
    response_iterator = iter(responses)
    time_iterator = iter(times)

    def clock() -> float:
        value = next(time_iterator)
        events.append(("clock", value))
        return value

    def retrieve(id: str) -> FileObject:
        events.append(("retrieve", id))
        response = next(response_iterator)
        if isinstance(response, BaseException):
            raise response
        return response

    def sleep(seconds: float) -> None:
        events.append(("sleep", seconds))
        if on_sleep is not None:
            on_sleep(seconds)

    async def async_retrieve(id: str) -> FileObject:
        return retrieve(id)

    async def async_sleep(seconds: float) -> None:
        sleep(seconds)

    monkeypatch.setattr(file_helpers, "time", SimpleNamespace(time=clock))
    monkeypatch.setattr(resource, "retrieve", async_retrieve if isinstance(resource, AsyncFiles) else retrieve)
    monkeypatch.setattr(resource, "_sleep", async_sleep if isinstance(resource, AsyncFiles) else sleep)
    return events


async def wait(resource: Files | AsyncFiles, id: str = FILE_ID, **kwargs: Any) -> FileObject:
    if isinstance(resource, AsyncFiles):
        return await resource.wait_for_processing(id, **kwargs)
    return resource.wait_for_processing(id, **kwargs)


@pytest.mark.parametrize("status", ["processed", "error", "deleted"])
@pytest.mark.parametrize("max_wait_seconds", [-1.0, 0.0, 1800.0])
async def test_initial_terminal_file_returns_without_sleep_or_timeout_check(
    files_resource: Files | AsyncFiles,
    monkeypatch: pytest.MonkeyPatch,
    status: str,
    max_wait_seconds: float,
) -> None:
    terminal = make_file(status)
    events = configure(monkeypatch, files_resource, responses=[terminal], times=[100.0])

    assert await wait(files_resource, max_wait_seconds=max_wait_seconds) is terminal
    assert events == [("clock", 100.0), ("retrieve", FILE_ID)]


@pytest.mark.parametrize("status", ["processed", "error", "deleted"])
@pytest.mark.parametrize("elapsed", [9.999, 10.0, 10.001], ids=["before", "exact", "after"])
async def test_timeout_boundary_is_checked_after_retrieval_even_for_terminal_files(
    files_resource: Files | AsyncFiles,
    monkeypatch: pytest.MonkeyPatch,
    status: str,
    elapsed: float,
) -> None:
    terminal = make_file(status)
    events = configure(
        monkeypatch,
        files_resource,
        responses=[make_file("uploaded"), terminal],
        times=[100.0, 100.0 + elapsed],
    )

    if elapsed > 10:
        with pytest.raises(RuntimeError) as caught:
            await wait(files_resource, poll_interval=0.25, max_wait_seconds=10)
        assert str(caught.value) == f"Giving up on waiting for file {FILE_ID} to finish processing after 10 seconds."
    else:
        assert await wait(files_resource, poll_interval=0.25, max_wait_seconds=10) is terminal
    assert events == [
        ("clock", 100.0),
        ("retrieve", FILE_ID),
        ("sleep", 0.25),
        ("retrieve", FILE_ID),
        ("clock", 100.0 + elapsed),
    ]


async def test_repeated_unknown_states_and_backward_wall_clock_keep_poll_order(
    files_resource: Files | AsyncFiles, monkeypatch: pytest.MonkeyPatch
) -> None:
    terminal = make_file("processed")
    events = configure(
        monkeypatch,
        files_resource,
        responses=[make_file("uploaded"), make_file("unknown-pending"), terminal],
        times=[100.0, 99.0, 110.0],
    )

    assert await wait(files_resource, poll_interval=0.125, max_wait_seconds=10) is terminal
    assert events == [
        ("clock", 100.0),
        ("retrieve", FILE_ID),
        ("sleep", 0.125),
        ("retrieve", FILE_ID),
        ("clock", 99.0),
        ("sleep", 0.125),
        ("retrieve", FILE_ID),
        ("clock", 110.0),
    ]


async def test_default_interval_and_timeout_error_are_unchanged(
    files_resource: Files | AsyncFiles, monkeypatch: pytest.MonkeyPatch
) -> None:
    events = configure(
        monkeypatch,
        files_resource,
        responses=[make_file("uploaded"), make_file("processed")],
        times=[0.0, 1801.0],
    )

    with pytest.raises(RuntimeError) as caught:
        await wait(files_resource)
    assert str(caught.value) == f"Giving up on waiting for file {FILE_ID} to finish processing after 1800 seconds."
    assert events[2] == ("sleep", 5.0)


async def test_custom_float_timeout_keeps_exact_error(
    files_resource: Files | AsyncFiles, monkeypatch: pytest.MonkeyPatch
) -> None:
    configure(
        monkeypatch,
        files_resource,
        responses=[make_file("uploaded"), make_file("processed")],
        times=[0.0, 2.5001],
    )

    with pytest.raises(RuntimeError) as caught:
        await wait(files_resource, max_wait_seconds=2.5)
    assert str(caught.value) == f"Giving up on waiting for file {FILE_ID} to finish processing after 2.5 seconds."


@pytest.mark.parametrize("stage", ["initial", "sleep", "retry"])
@pytest.mark.parametrize("error_type", [RuntimeError, ValueError, asyncio.CancelledError])
async def test_retrieve_sleep_and_cancellation_errors_propagate_unchanged(
    files_resource: Files | AsyncFiles,
    monkeypatch: pytest.MonkeyPatch,
    stage: str,
    error_type: type[BaseException],
) -> None:
    error = error_type("synthetic failure")
    responses: list[FileObject | BaseException] = [make_file("uploaded")]
    if stage == "initial":
        responses = [error]
    elif stage == "retry":
        responses.append(error)

    def fail_sleep(_seconds: float) -> None:
        raise error

    events = configure(
        monkeypatch,
        files_resource,
        responses=responses,
        times=[0.0],
        on_sleep=fail_sleep if stage == "sleep" else None,
    )

    with pytest.raises(error_type) as caught:
        await wait(files_resource, poll_interval=0.125)
    assert caught.value is error
    expected: list[tuple[str, object]] = [("clock", 0.0), ("retrieve", FILE_ID)]
    if stage != "initial":
        expected.append(("sleep", 0.125))
    if stage == "retry":
        expected.append(("retrieve", FILE_ID))
    assert events == expected


async def test_retrieve_override_is_looked_up_again_after_sleep(
    files_resource: Files | AsyncFiles, monkeypatch: pytest.MonkeyPatch
) -> None:
    terminal = make_file("processed")
    replacement = (
        mock.AsyncMock(return_value=terminal)
        if isinstance(files_resource, AsyncFiles)
        else mock.Mock(return_value=terminal)
    )

    def replace_retrieve(_seconds: float) -> None:
        monkeypatch.setattr(files_resource, "retrieve", replacement)

    events = configure(
        monkeypatch,
        files_resource,
        responses=[make_file("uploaded")],
        times=[0.0, 0.0],
        on_sleep=replace_retrieve,
    )

    assert await wait(files_resource, poll_interval=0.125) is terminal
    replacement.assert_called_once_with(FILE_ID)
    assert events == [("clock", 0.0), ("retrieve", FILE_ID), ("sleep", 0.125), ("clock", 0.0)]


async def test_sleep_override_is_looked_up_again_on_each_poll(
    files_resource: Files | AsyncFiles, monkeypatch: pytest.MonkeyPatch
) -> None:
    terminal = make_file("processed")
    replacement = mock.AsyncMock() if isinstance(files_resource, AsyncFiles) else mock.Mock()

    def replace_sleep(_seconds: float) -> None:
        monkeypatch.setattr(files_resource, "_sleep", replacement)

    events = configure(
        monkeypatch,
        files_resource,
        responses=[make_file("uploaded"), make_file("uploaded"), terminal],
        times=[0.0, 0.0, 0.0],
        on_sleep=replace_sleep,
    )

    assert await wait(files_resource, poll_interval=0.125) is terminal
    replacement.assert_called_once_with(0.125)
    assert events == [
        ("clock", 0.0),
        ("retrieve", FILE_ID),
        ("sleep", 0.125),
        ("retrieve", FILE_ID),
        ("clock", 0.0),
        ("retrieve", FILE_ID),
        ("clock", 0.0),
    ]


@pytest.mark.parametrize("interval", [-1.0, 0.0, 0.25])
async def test_poll_interval_is_forwarded_without_normalization(
    files_resource: Files | AsyncFiles, monkeypatch: pytest.MonkeyPatch, interval: float
) -> None:
    terminal = make_file("processed")
    events = configure(
        monkeypatch,
        files_resource,
        responses=[make_file("uploaded"), terminal],
        times=[0.0, 0.0],
    )

    assert await wait(files_resource, poll_interval=interval) is terminal
    assert events[2] == ("sleep", interval)


@pytest.mark.parametrize("max_wait_seconds", [float("inf"), float("nan")], ids=["infinity", "nan"])
async def test_nonfinite_timeout_keeps_existing_comparison_behavior(
    files_resource: Files | AsyncFiles, monkeypatch: pytest.MonkeyPatch, max_wait_seconds: float
) -> None:
    terminal = make_file("processed")
    configure(
        monkeypatch,
        files_resource,
        responses=[make_file("uploaded"), terminal],
        times=[0.0, 1_000_000.0],
    )

    assert await wait(files_resource, max_wait_seconds=max_wait_seconds) is terminal


async def test_zero_timeout_still_retrieves_before_strict_deadline_check(
    files_resource: Files | AsyncFiles, monkeypatch: pytest.MonkeyPatch
) -> None:
    events = configure(
        monkeypatch,
        files_resource,
        responses=[make_file("uploaded"), make_file("uploaded"), make_file("processed")],
        times=[0.0, 0.0, 0.001],
    )

    with pytest.raises(RuntimeError) as caught:
        await wait(files_resource, poll_interval=0.0, max_wait_seconds=0)
    assert str(caught.value) == f"Giving up on waiting for file {FILE_ID} to finish processing after 0 seconds."
    assert [event for event in events if event[0] == "retrieve"] == [("retrieve", FILE_ID)] * 3
    assert [event for event in events if event[0] == "sleep"] == [("sleep", 0.0)] * 2


async def test_public_id_keyword_is_preserved(
    files_resource: Files | AsyncFiles, monkeypatch: pytest.MonkeyPatch
) -> None:
    terminal = make_file("processed")
    configure(monkeypatch, files_resource, responses=[terminal], times=[0.0])

    if isinstance(files_resource, AsyncFiles):
        assert await files_resource.wait_for_processing(id=FILE_ID) is terminal
    else:
        assert files_resource.wait_for_processing(id=FILE_ID) is terminal


@pytest.mark.parametrize("resource,is_async", [(Files, False), (AsyncFiles, True)])
def test_public_signature_and_coroutine_kind_are_preserved(
    resource: type[Files] | type[AsyncFiles], is_async: bool
) -> None:
    signature = inspect.signature(resource.wait_for_processing)
    assert list(signature.parameters) == ["self", "id", "poll_interval", "max_wait_seconds"]
    assert signature.parameters["id"].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert signature.parameters["id"].default is inspect.Parameter.empty
    assert signature.parameters["poll_interval"].kind is inspect.Parameter.KEYWORD_ONLY
    assert signature.parameters["poll_interval"].default == 5.0
    assert signature.parameters["max_wait_seconds"].kind is inspect.Parameter.KEYWORD_ONLY
    assert isinstance(signature.parameters["max_wait_seconds"].default, int)
    assert signature.parameters["max_wait_seconds"].default == 1800
    assert signature.return_annotation == "FileObject"
    assert inspect.iscoroutinefunction(resource.wait_for_processing) is is_async
