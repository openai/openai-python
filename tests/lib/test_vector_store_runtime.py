from __future__ import annotations

import io
import inspect
import threading
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import Mock, AsyncMock

import anyio
import pytest

from openai.lib import _vector_stores as runtime
from openai.resources.vector_stores import files as files_module, file_batches as batches_module

from . import test_vector_store_file_poll_timeout as deadline_contracts
from .test_vector_store_file_poll_timeout import clock as clock, resource as resource

# Exercise the released public-entrypoint deadline contracts with both implementations.
test_deadline_caps_sleep_and_prevents_next_request = (
    deadline_contracts.test_deadline_caps_sleep_and_prevents_next_request
)
test_request_time_counts_toward_deadline = deadline_contracts.test_request_time_counts_toward_deadline
test_terminal_result_is_preserved = deadline_contracts.test_terminal_result_is_preserved
test_omitted_limit_preserves_unbounded_wait = deadline_contracts.test_omitted_limit_preserves_unbounded_wait
test_invalid_limit_fails_before_side_effects = deadline_contracts.test_invalid_limit_fails_before_side_effects
test_zero_limit_prevents_polling = deadline_contracts.test_zero_limit_prevents_polling
test_helpers_start_deadline_after_upload_and_attachment = (
    deadline_contracts.test_helpers_start_deadline_after_upload_and_attachment
)

BINDINGS = (
    (files_module.Files, "create_and_poll", runtime.create_and_poll_vector_store_file),
    (files_module.Files, "upload", runtime.upload_vector_store_file),
    (files_module.Files, "upload_and_poll", runtime.upload_and_poll_vector_store_file),
    (files_module.AsyncFiles, "create_and_poll", runtime.async_create_and_poll_vector_store_file),
    (files_module.AsyncFiles, "upload", runtime.async_upload_vector_store_file),
    (files_module.AsyncFiles, "upload_and_poll", runtime.async_upload_and_poll_vector_store_file),
    (batches_module.FileBatches, "create_and_poll", runtime.create_and_poll_vector_store_file_batch),
    (batches_module.FileBatches, "upload_and_poll", runtime.upload_and_poll_vector_store_file_batch),
    (batches_module.AsyncFileBatches, "create_and_poll", runtime.async_create_and_poll_vector_store_file_batch),
    (batches_module.AsyncFileBatches, "upload_and_poll", runtime.async_upload_and_poll_vector_store_file_batch),
)
RELEASED = {(cls, name): getattr(cls, name) for cls, name, _ in BINDINGS}


@pytest.fixture(autouse=True, params=["released", "extracted"])
def implementation(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    if request.param == "extracted":
        for cls, name, function in BINDINGS:
            monkeypatch.setattr(cls, name, function)


@pytest.mark.parametrize("cls,name,function", BINDINGS)
def test_runtime_retains_facade_parameters(cls: Any, name: str, function: Any) -> None:
    before = inspect.signature(RELEASED[cls, name])
    after = inspect.signature(function)
    # Only the internal receiver gains a resource annotation and name.
    assert list(before.parameters.values())[1:] == list(after.parameters.values())[1:]
    assert before.return_annotation == after.return_annotation
    assert inspect.iscoroutinefunction(RELEASED[cls, name]) == inspect.iscoroutinefunction(function)


async def invoke(target: Any, method: str, **kwargs: Any) -> Any:
    value = getattr(target, method)(**kwargs)
    return await value if inspect.isawaitable(value) else value


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("method", ["create_and_poll", "upload", "upload_and_poll"])
async def test_file_helpers_preserve_dispatch_options_and_caller_stream(
    asynchronous: bool, method: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    factory = AsyncMock if asynchronous else Mock
    upload = factory(return_value=SimpleNamespace(id="uploaded-id"))
    client = Mock(files=SimpleNamespace(create=upload))
    cls = files_module.AsyncFiles if asynchronous else files_module.Files
    target = cls(cast(Any, client))
    result = object()
    create, poll = factory(return_value=result), factory(return_value=result)
    monkeypatch.setattr(target, "create", create)
    monkeypatch.setattr(target, "poll", poll)
    terminal_helper = factory(return_value=result)
    if method == "upload_and_poll":
        monkeypatch.setattr(target, "create_and_poll", terminal_helper)
    attributes = {"verified": True}
    chunking = {"type": "auto"}
    options = {
        "extra_headers": {"X-Probe": "synthetic"},
        "extra_query": {"q": "probe"},
        "extra_body": {"b": 1},
        "timeout": 0.5,
    }
    with io.BytesIO(b"synthetic upload") as stream:
        stream.seek(3)
        payload = ("probe.txt", stream, "text/plain")
        kwargs: dict[str, Any] = {"vector_store_id": "vs-probe", "chunking_strategy": chunking}
        if method == "create_and_poll":
            kwargs.update(
                file_id="existing-id", attributes=attributes, poll_interval_ms=0, max_wait_seconds=2, **options
            )
        elif method == "upload":
            kwargs["file"] = payload
        else:
            kwargs.update(file=payload, attributes=attributes, poll_interval_ms=0, max_wait_seconds=2)
        assert await invoke(target, method, **kwargs) is result
        assert not stream.closed and stream.tell() == 3
        if method == "create_and_poll":
            upload.assert_not_called()
            create.assert_called_once_with(
                vector_store_id="vs-probe",
                file_id="existing-id",
                chunking_strategy=chunking,
                attributes=attributes,
                **options,
            )
            poll.assert_called_once_with(
                "existing-id", vector_store_id="vs-probe", poll_interval_ms=0, max_wait_seconds=2
            )
            assert create.call_args.kwargs["attributes"] is attributes
            assert create.call_args.kwargs["extra_headers"] is options["extra_headers"]
        else:
            upload.assert_called_once_with(file=payload, purpose="assistants")
            assert upload.call_args.kwargs["file"] is payload
            if method == "upload":
                create.assert_called_once_with(
                    vector_store_id="vs-probe", file_id="uploaded-id", chunking_strategy=chunking
                )
                poll.assert_not_called()
            else:
                terminal_helper.assert_called_once_with(
                    vector_store_id="vs-probe",
                    file_id="uploaded-id",
                    chunking_strategy=chunking,
                    poll_interval_ms=0,
                    max_wait_seconds=2,
                    attributes=attributes,
                )
                assert terminal_helper.call_args.kwargs["attributes"] is attributes
                create.assert_not_called()
                poll.assert_not_called()


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
async def test_batch_create_preserves_resource_hooks_and_all_options(
    asynchronous: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    factory = AsyncMock if asynchronous else Mock
    cls = batches_module.AsyncFileBatches if asynchronous else batches_module.FileBatches
    target = cls(cast(Any, Mock()))
    result = object()
    create, poll = factory(return_value=SimpleNamespace(id="batch-probe")), factory(return_value=result)
    monkeypatch.setattr(target, "create", create)
    monkeypatch.setattr(target, "poll", poll)
    kwargs: dict[str, Any] = dict(
        vector_store_id="vs-probe",
        attributes={"verified": True},
        chunking_strategy={"type": "auto"},
        file_ids=["existing-id"],
        files=[{"file_id": "file-probe"}],
        extra_headers={"X-Probe": "synthetic"},
        extra_query={"q": 1},
        extra_body={"b": 2},
        timeout=0.25,
    )
    assert await invoke(target, "create_and_poll", poll_interval_ms=0, **kwargs) is result
    create.assert_called_once_with(**kwargs)
    for key in ("attributes", "file_ids", "files", "extra_headers", "extra_query", "extra_body"):
        assert create.call_args.kwargs[key] is kwargs[key]
    poll.assert_called_once_with("batch-probe", vector_store_id="vs-probe", poll_interval_ms=0)


@pytest.mark.parametrize("backend", ["sync", "asyncio", "trio"])
@pytest.mark.parametrize("limit", [1, 2])
def test_batch_upload_concurrency_ids_and_file_ownership(
    backend: str, limit: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    streams = [io.BytesIO(bytes([index])) for index in range(4)]
    originals = list(streams)
    existing = ["existing-first", "existing-second"]
    completed: list[str] = []
    active = peak = 0
    lock = threading.Lock()
    barrier = threading.Barrier(limit, timeout=5)
    result = object()

    def started() -> None:
        nonlocal active, peak
        active += 1
        peak = max(peak, active)

    def finished(file: Any) -> SimpleNamespace:
        nonlocal active
        active -= 1
        name = f"uploaded-{streams.index(file)}"
        completed.append(name)
        return SimpleNamespace(id=name)

    def upload(*, file: Any, purpose: str) -> SimpleNamespace:
        assert purpose == "assistants"
        with lock:
            started()
        barrier.wait()
        with lock:
            return finished(file)

    def check(create: Any) -> None:
        assert peak == limit and active == 0
        create.assert_called_once()
        kwargs = create.call_args.kwargs
        assert kwargs["vector_store_id"] == "vs-probe"
        assert kwargs["file_ids"][:2] == existing
        assert sorted(kwargs["file_ids"][2:]) == [f"uploaded-{i}" for i in range(4)]
        if backend != "sync":
            assert kwargs["file_ids"][2:] == completed
        assert kwargs["poll_interval_ms"] == 0
        assert kwargs["chunking_strategy"] is chunking
        assert streams == originals and existing == ["existing-first", "existing-second"]
        assert all(not stream.closed and stream.tell() == 0 for stream in streams)

    chunking = {"type": "auto"}
    kwargs: dict[str, Any] = dict(
        vector_store_id="vs-probe",
        files=iter(streams),
        file_ids=existing,
        max_concurrency=limit,
        poll_interval_ms=0,
        chunking_strategy=chunking,
    )
    try:
        if backend == "sync":
            target = batches_module.FileBatches(cast(Any, Mock(files=SimpleNamespace(create=upload))))
            create = Mock(return_value=result)
            monkeypatch.setattr(target, "create_and_poll", create)
            assert target.upload_and_poll(**kwargs) is result
            check(create)
        else:

            async def run() -> None:
                gate = anyio.Event()

                async def async_upload(*, file: Any, purpose: str) -> SimpleNamespace:
                    assert purpose == "assistants"
                    started()
                    if active == limit:
                        gate.set()
                    await gate.wait()
                    await anyio.lowlevel.checkpoint()
                    return finished(file)

                target = batches_module.AsyncFileBatches(cast(Any, Mock(files=SimpleNamespace(create=async_upload))))
                create = AsyncMock(return_value=result)
                monkeypatch.setattr(target, "create_and_poll", create)
                assert await target.upload_and_poll(**kwargs) is result
                check(create)

            anyio.run(run, backend=backend)
    finally:
        for stream in streams:
            stream.close()


@pytest.mark.parametrize("backend", ["sync", "asyncio", "trio"])
def test_batch_upload_failure_preserves_backend_cleanup(backend: str, monkeypatch: pytest.MonkeyPatch) -> None:
    failure = RuntimeError("synthetic upload failure")
    first, second = io.BytesIO(b"first"), io.BytesIO(b"second")
    events: list[str] = []
    create = Mock() if backend == "sync" else AsyncMock()

    def assert_failure(exc: Exception) -> None:
        leaves = list(getattr(exc, "exceptions", [exc]))
        assert failure in leaves
        create.assert_not_called()
        assert not first.closed and not second.closed

    try:
        if backend == "sync":

            def upload(*, file: Any, purpose: str) -> SimpleNamespace:
                assert purpose == "assistants"
                if file is first:
                    raise failure
                events.append("second-finished")
                return SimpleNamespace(id="second")

            target = batches_module.FileBatches(cast(Any, Mock(files=SimpleNamespace(create=upload))))
            monkeypatch.setattr(target, "create_and_poll", create)
            with pytest.raises(RuntimeError, match="synthetic upload failure") as caught:
                target.upload_and_poll("vs-probe", files=[first, second], max_concurrency=2)
            assert_failure(caught.value)
            # The released executor context waits for submitted uploads before raising.
            assert events == ["second-finished"]
        else:

            async def run() -> None:
                started, release, finished = anyio.Event(), anyio.Event(), anyio.Event()

                async def upload(*, file: Any, purpose: str) -> SimpleNamespace:
                    assert purpose == "assistants"
                    if file is first:
                        await started.wait()
                        raise failure
                    started.set()
                    try:
                        await release.wait()
                        events.append("second-finished")
                        return SimpleNamespace(id="second")
                    finally:
                        events.append("second-cleaned")
                        finished.set()

                target = batches_module.AsyncFileBatches(cast(Any, Mock(files=SimpleNamespace(create=upload))))
                monkeypatch.setattr(target, "create_and_poll", create)
                try:
                    await target.upload_and_poll("vs-probe", files=[first, second], max_concurrency=2)
                except Exception as exc:
                    assert_failure(exc)
                else:
                    pytest.fail("upload failure did not propagate")
                if backend == "asyncio":
                    # gather propagates the first failure without cancelling its sibling.
                    assert events == []
                    release.set()
                    await finished.wait()
                    assert events == ["second-finished", "second-cleaned"]
                else:
                    assert events == ["second-cleaned"]

            anyio.run(run, backend=backend)
    finally:
        first.close()
        second.close()


@pytest.mark.parametrize("backend", ["asyncio", "trio"])
def test_batch_upload_cancellation_preserves_stream_ownership(backend: str, monkeypatch: pytest.MonkeyPatch) -> None:
    async def run() -> None:
        started = anyio.Event()
        cleaned: list[bool] = []
        with io.BytesIO(b"synthetic content") as stream:

            async def upload(**kwargs: Any) -> Any:
                assert kwargs["file"] is stream
                started.set()
                try:
                    await anyio.sleep_forever()
                finally:
                    cleaned.append(True)

            target = batches_module.AsyncFileBatches(cast(Any, Mock(files=SimpleNamespace(create=upload))))
            create = AsyncMock()
            monkeypatch.setattr(target, "create_and_poll", create)

            async def call() -> None:
                await target.upload_and_poll("vs-probe", files=[stream])

            async with anyio.create_task_group() as group:
                group.start_soon(call)
                await started.wait()
                group.cancel_scope.cancel()
            assert cleaned == [True]
            assert not stream.closed
            create.assert_not_called()

    anyio.run(run, backend=backend)


async def test_unsupported_async_backend_fails_before_upload(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Mock(files=SimpleNamespace(create=AsyncMock()))
    target = batches_module.AsyncFileBatches(cast(Any, client))
    with monkeypatch.context() as patch:
        patch.setattr(runtime.sniffio, "current_async_library", lambda: "unsupported-probe")
        with pytest.raises(RuntimeError, match="Only asyncio or trio is supported"):
            await target.upload_and_poll("vs-probe", files=[b"synthetic"])
    client.files.create.assert_not_called()
