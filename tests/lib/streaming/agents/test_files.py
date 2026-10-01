from __future__ import annotations

import json
import asyncio
from io import BytesIO
from typing import Any, Callable
from pathlib import Path
from typing_extensions import override

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from openai.lib.beta.agents import AgentFileStagingError, AgentFilePreparationError
from tests.lib.streaming.agents.test_streams import Server, sdk as sdk


class FilesServer(Server):
    def __init__(self) -> None:
        super().__init__()
        self.uploads = 0
        self.fail_upload = 0
        self.fail_stage = False
        self.cancel_upload = 0
        self.cancel_stage = False
        self.after_upload: Callable[[], None] | None = None

    @override
    def handle(self, request: httpx2.Request) -> httpx2.Response:
        self.requests.append(request)
        if request.url.path == "/v1/files":
            self.uploads += 1
            if self.after_upload is not None:
                self.after_upload()
            if self.uploads == self.cancel_upload:
                raise asyncio.CancelledError()
            if self.uploads == self.fail_upload:
                return httpx2.Response(500, json={"error": {"message": "Synthetic upload failure"}})
            return httpx2.Response(
                200,
                json={
                    "id": f"file_{self.uploads}",
                    "bytes": 3,
                    "created_at": 1,
                    "filename": "synthetic.txt",
                    "object": "file",
                    "purpose": "user_data",
                    "status": "processed",
                },
            )
        assert request.url.path == "/v1/agents/environments/env_test/files"
        if self.cancel_stage:
            raise asyncio.CancelledError()
        if self.fail_stage:
            return httpx2.Response(500, json={"error": {"message": "Synthetic staging failure"}})
        body = json.loads(request.content)
        return httpx2.Response(
            200,
            json={
                "id": "envfile_test",
                "object": "agent.environment.file",
                "environment_id": "env_test",
                "path": body["path"],
                "size_bytes": 3,
                "created_at": 1,
            },
        )


@pytest.fixture
def server() -> FilesServer:
    return FilesServer()


async def prepare(sdk: OpenAI | AsyncOpenAI, files: dict[str, Path], **options: Any) -> Any:
    if isinstance(sdk, AsyncOpenAI):
        return await sdk.beta.agents.environments.files.prepare(files, **options)
    return sdk.beta.agents.environments.files.prepare(files, **options)


async def test_prepare_uploads_selected_files_and_preserves_options(
    sdk: OpenAI | AsyncOpenAI, server: FilesServer, tmp_path: Path
) -> None:
    source = tmp_path / "source.txt"
    source.write_text("abc")
    result = await prepare(
        sdk,
        {"/workspace/source.txt": source},
        extra_headers={"X-Synthetic": "test"},
        extra_query={"synthetic": "query"},
        extra_body={"synthetic": "body"},
        timeout=7,
    )
    assert result.files == [{"type": "file_id", "file_id": "file_1", "path": "/workspace/source.txt"}]
    assert result.uploaded_file_ids == ["file_1"]
    assert all(request.headers["X-Synthetic"] == "test" for request in server.requests)
    assert b"abc" in server.requests[0].content
    assert server.requests[0].url.params["synthetic"] == "query"
    assert b"body" in server.requests[0].content


async def test_preflight_all_files_before_upload(
    sdk: OpenAI | AsyncOpenAI, server: FilesServer, tmp_path: Path
) -> None:
    source = tmp_path / "source.txt"
    source.write_text("abc")
    with pytest.raises(ValueError, match="regular files"):
        await prepare(sdk, {"/workspace/source.txt": source, "/workspace/missing.txt": tmp_path / "missing"})
    assert server.uploads == 0
    with pytest.raises(ValueError, match="conflicting"):
        await prepare(sdk, {"/workspace/source.txt": source, "/workspace/source.txt/child": source})
    assert server.uploads == 0
    with pytest.raises(ValueError, match="Idempotency-Key"):
        await prepare(
            sdk, {"/workspace/a": source, "/workspace/b": source}, extra_headers={"idempotency-key": "synthetic"}
        )
    assert server.uploads == 0


async def test_partial_upload_ownership_is_available(
    sdk: OpenAI | AsyncOpenAI, server: FilesServer, tmp_path: Path
) -> None:
    source = tmp_path / "source.txt"
    source.write_text("abc")
    server.fail_upload = 2
    with pytest.raises(AgentFilePreparationError) as caught:
        await prepare(sdk, {"/workspace/a": source, "/workspace/b": source})
    assert vars(caught.value)["prepared"].uploaded_file_ids == ["file_1"]
    assert caught.value.prepared.files[0]["path"] == "/workspace/a"
    assert all(request.method == "POST" for request in server.requests)


async def test_directory_selection_and_symlink_preflight(
    sdk: OpenAI | AsyncOpenAI, server: FilesServer, tmp_path: Path
) -> None:
    (tmp_path / "keep.md").write_text("abc")
    (tmp_path / "omit.txt").write_text("secret")
    if isinstance(sdk, AsyncOpenAI):
        result = await sdk.beta.agents.environments.files.prepare_directory(
            tmp_path, destination="/workspace/docs", include=["*.md"]
        )
    else:
        result = sdk.beta.agents.environments.files.prepare_directory(
            tmp_path, destination="/workspace/docs", include=["*.md"]
        )
    assert result.files[0]["path"] == "/workspace/docs/keep.md"
    assert server.uploads == 1
    (tmp_path / "link.md").symlink_to(tmp_path / "omit.txt")
    with pytest.raises(ValueError, match="symlink"):
        if isinstance(sdk, AsyncOpenAI):
            await sdk.beta.agents.environments.files.prepare_directory(
                tmp_path, destination="/workspace/docs", include=["*.md"]
            )
        else:
            sdk.beta.agents.environments.files.prepare_directory(
                tmp_path, destination="/workspace/docs", include=["*.md"]
            )
    assert server.uploads == 1


async def test_live_staging_and_failure_ownership(sdk: OpenAI | AsyncOpenAI, server: FilesServer) -> None:
    async def stage() -> Any:
        if isinstance(sdk, AsyncOpenAI):
            return await sdk.beta.agents.environments.files.upload(
                "env_test",
                file=("source.txt", b"abc"),
                path="/workspace/source.txt",
                extra_query={"synthetic": "query"},
                extra_body={"synthetic": "body"},
            )
        return sdk.beta.agents.environments.files.upload(
            "env_test",
            file=("source.txt", b"abc"),
            path="/workspace/source.txt",
            extra_query={"synthetic": "query"},
            extra_body={"synthetic": "body"},
        )

    result = await stage()
    assert result.uploaded_file_id == "file_1"
    assert result.file.path == "/workspace/source.txt"
    assert all(request.url.params["synthetic"] == "query" for request in server.requests)
    assert all(b"body" in request.content for request in server.requests)
    server.fail_stage = True
    with pytest.raises(AgentFileStagingError) as caught:
        await stage()
    assert vars(caught.value)["uploaded_file_id"] == "file_2"
    assert all(request.method == "POST" for request in server.requests)


async def test_count_and_aggregate_size_limits_precede_upload(
    sdk: OpenAI | AsyncOpenAI, server: FilesServer, tmp_path: Path
) -> None:
    source = tmp_path / "large"
    with source.open("wb") as content:
        content.truncate(26 * 1024 * 1024)
    with pytest.raises(ValueError, match="in total"):
        await prepare(sdk, {"/workspace/a": source, "/workspace/b": source})
    with pytest.raises(ValueError, match="50 files"):
        await prepare(sdk, {f"/workspace/{index}": source for index in range(51)})
    with source.open("wb") as content:
        content.truncate(50 * 1024 * 1024 + 1)
    with pytest.raises(ValueError, match="50 MiB"):
        await prepare(sdk, {"/workspace/a": source})
    assert server.uploads == 0


async def test_async_cancellation_retains_only_observed_uploads(
    sdk: OpenAI | AsyncOpenAI, server: FilesServer, tmp_path: Path
) -> None:
    if not isinstance(sdk, AsyncOpenAI):
        pytest.skip("Async cancellation contract")
    source = tmp_path / "source.txt"
    source.write_text("abc")
    server.cancel_upload = 2
    with pytest.raises(asyncio.CancelledError) as caught:
        await sdk.beta.agents.environments.files.prepare({"/workspace/a": source, "/workspace/b": source})
    assert vars(caught.value)["prepared"].uploaded_file_ids == ["file_1"]
    assert all(request.method == "POST" for request in server.requests)


async def test_client_default_idempotency_key_is_rejected_for_batch(
    sdk: OpenAI | AsyncOpenAI, server: FilesServer, tmp_path: Path
) -> None:
    source = tmp_path / "source.txt"
    source.write_text("abc")
    sdk._custom_headers = {"Idempotency-Key": "synthetic"}
    with pytest.raises(ValueError, match="Idempotency-Key"):
        await prepare(sdk, {"/workspace/a": source, "/workspace/b": source})
    assert server.uploads == 0


@pytest.mark.parametrize(
    "destination",
    [
        "/tmp/source",
        "/workspace/../source",
        "/workspace//source",
        "/workspace/./source",
        "/workspace/source/",
        "/workspace/a\\b",
        "/workspace/\x00",
        "/workspace/.codex/source",
        "/workspace/.managed-agents/source",
        "/workspace/.managed-agents-internal/source",
        "/workspace/outputs",
        "/workspace/" + "x" * 4096,
    ],
)
async def test_invalid_hosted_destination_fails_before_upload(
    sdk: OpenAI | AsyncOpenAI, server: FilesServer, tmp_path: Path, destination: str
) -> None:
    source = tmp_path / "source.txt"
    source.write_text("abc")
    with pytest.raises(ValueError):
        await prepare(sdk, {destination: source})
    assert server.uploads == 0


async def test_cancelled_staging_preserves_observed_upload_id(sdk: OpenAI | AsyncOpenAI, server: FilesServer) -> None:
    if not isinstance(sdk, AsyncOpenAI):
        pytest.skip("Async cancellation contract")
    server.cancel_stage = True
    with pytest.raises(asyncio.CancelledError) as caught:
        await sdk.beta.agents.environments.files.upload(
            "env_test", file=("source.txt", b"abc"), path="/workspace/source.txt"
        )
    assert vars(caught.value)["uploaded_file_id"] == "file_1"
    assert all(request.method == "POST" for request in server.requests)


async def test_system_alias_ancestor_is_allowed_but_directory_entries_are_not_followed(
    sdk: OpenAI | AsyncOpenAI, server: FilesServer, tmp_path: Path
) -> None:
    actual = tmp_path / "actual"
    root = actual / "chosen"
    root.mkdir(parents=True)
    (root / "keep.md").write_text("abc")
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "private.md").write_text("private")
    (root / "linked").symlink_to(outside, target_is_directory=True)
    alias = tmp_path / "system-alias"
    alias.symlink_to(actual, target_is_directory=True)
    if isinstance(sdk, AsyncOpenAI):
        prepared = await sdk.beta.agents.environments.files.prepare_directory(
            alias / "chosen", destination="/workspace/docs", include=["**/*.md"]
        )
    else:
        prepared = sdk.beta.agents.environments.files.prepare_directory(
            alias / "chosen", destination="/workspace/docs", include=["**/*.md"]
        )
    assert [item["path"] for item in prepared.files] == ["/workspace/docs/keep.md"]
    assert server.uploads == 1


async def test_prepared_files_keep_opened_sources_during_batch_upload(
    sdk: OpenAI | AsyncOpenAI, server: FilesServer, tmp_path: Path
) -> None:
    first = tmp_path / "first.txt"
    second = tmp_path / "second.txt"
    first.write_text("first-original")
    second.write_text("second-original")

    def replace_later_source() -> None:
        if server.uploads == 1:
            second.unlink()
            second.write_text("replacement")

    server.after_upload = replace_later_source
    await prepare(sdk, {"/workspace/first": first, "/workspace/second": second})
    assert b"second-original" in server.requests[1].content
    assert b"replacement" not in server.requests[1].content


@pytest.mark.parametrize("file_backed", [False, True])
async def test_known_stream_sizes_fail_before_upload_without_moving_position(
    sdk: OpenAI | AsyncOpenAI, server: FilesServer, tmp_path: Path, file_backed: bool
) -> None:
    content = (tmp_path / "large").open("w+b") if file_backed else BytesIO()
    with content:
        content.seek(50 * 1024 * 1024)
        content.write(b"x")
        content.seek(3)
        with pytest.raises(ValueError, match="50 MiB"):
            if isinstance(sdk, AsyncOpenAI):
                await sdk.beta.agents.environments.files.upload(
                    "env_test", file=("large", content), path="/workspace/large"
                )
            else:
                sdk.beta.agents.environments.files.upload("env_test", file=("large", content), path="/workspace/large")
        assert content.tell() == 3
    assert not server.requests


async def test_empty_environment_id_fails_before_upload(sdk: OpenAI | AsyncOpenAI, server: FilesServer) -> None:
    with pytest.raises(ValueError, match="environment_id"):
        if isinstance(sdk, AsyncOpenAI):
            await sdk.beta.agents.environments.files.upload(
                "", file=("source.txt", b"abc"), path="/workspace/source.txt"
            )
        else:
            sdk.beta.agents.environments.files.upload("", file=("source.txt", b"abc"), path="/workspace/source.txt")
    assert not server.requests


@pytest.mark.parametrize("staging", [False, True])
def test_trio_cancellation_preserves_observed_uploads(tmp_path: Path, staging: bool) -> None:
    import trio
    import anyio

    source = tmp_path / "source.txt"
    source.write_text("abc")
    server = FilesServer()
    captured: list[BaseException] = []

    async def run() -> None:
        with trio.CancelScope() as scope:

            async def handle(request: httpx2.Request) -> httpx2.Response:
                should_cancel = request.url.path.endswith("env_test/files") if staging else server.uploads == 1
                if should_cancel:
                    scope.cancel()
                    await trio.lowlevel.checkpoint()
                return server.handle(request)

            async with AsyncOpenAI(
                api_key="synthetic",
                base_url="https://sdk-test.example/v1",
                max_retries=0,
                http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handle), trust_env=False),
            ) as client:
                try:
                    if staging:
                        await client.beta.agents.environments.files.upload(
                            "env_test", file=source, path="/workspace/source.txt"
                        )
                    else:
                        await client.beta.agents.environments.files.prepare(
                            {"/workspace/a": source, "/workspace/b": source}
                        )
                except trio.Cancelled as error:
                    captured.append(error)
                    raise

    anyio.run(run, backend="trio")
    assert len(captured) == 1
    if staging:
        assert vars(captured[0])["uploaded_file_id"] == "file_1"
    else:
        assert vars(captured[0])["prepared"].uploaded_file_ids == ["file_1"]


async def test_async_directory_selection_runs_off_event_loop(
    sdk: OpenAI | AsyncOpenAI, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import threading

    from openai.lib.beta.agents import _files

    if not isinstance(sdk, AsyncOpenAI):
        pytest.skip("Async traversal contract")
    (tmp_path / "source.txt").write_text("abc")
    current_thread = threading.get_ident()
    original = _files.directory_files

    def select(root: Any, destination: str, include: Any) -> Any:
        assert threading.get_ident() != current_thread
        return original(root, destination, include)

    monkeypatch.setattr(_files, "directory_files", select)
    prepared = await sdk.beta.agents.environments.files.prepare_directory(
        tmp_path, destination="/workspace/docs", include=["*.txt"]
    )
    assert prepared.uploaded_file_ids == ["file_1"]


async def prepare_directory(sdk: OpenAI | AsyncOpenAI, root: Path, destination: str = "/workspace/docs") -> Any:
    if isinstance(sdk, AsyncOpenAI):
        return await sdk.beta.agents.environments.files.prepare_directory(
            root, destination=destination, include=["**/*.txt"]
        )
    return sdk.beta.agents.environments.files.prepare_directory(root, destination=destination, include=["**/*.txt"])


async def test_directory_walk_error_is_not_a_partial_success(
    sdk: OpenAI | AsyncOpenAI, server: FilesServer, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from openai.lib.beta.agents import _files

    (tmp_path / "keep.txt").write_text("abc")

    def failed_walk(root: Any, **options: Any) -> Any:
        yield str(root), [], ["keep.txt"]
        options["onerror"](PermissionError("synthetic unreadable subtree"))

    monkeypatch.setattr(_files, "walk", failed_walk)
    with pytest.raises(PermissionError, match="synthetic"):
        await prepare_directory(sdk, tmp_path)
    assert not server.requests


async def test_cached_directory_entry_cannot_leave_selected_root(
    sdk: OpenAI | AsyncOpenAI, server: FilesServer, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from openai.lib.beta.agents import _files

    root = tmp_path / "chosen"
    child = root / "child"
    child.mkdir(parents=True)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "other.txt").write_text("outside")

    def changed_walk(directory: Any, **_options: Any) -> Any:
        yield str(directory), ["child"], []
        child.rename(root / "original-child")
        child.symlink_to(outside, target_is_directory=True)
        yield str(child), [], ["other.txt"]

    monkeypatch.setattr(_files, "walk", changed_walk)
    with pytest.raises(ValueError, match="left its root"):
        await prepare_directory(sdk, root)
    assert not server.requests


async def test_directory_selection_keeps_file_identity_until_open(
    sdk: OpenAI | AsyncOpenAI, server: FilesServer, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from openai.lib.beta.agents import _files
    from openai.resources.beta.agents.environments import files as resource_files

    source = tmp_path / "chosen.txt"
    source.write_text("abc")
    original = _files.directory_files

    def select_then_replace(root: Any, destination: str, include: Any) -> Any:
        selected = original(root, destination, include)
        source.rename(tmp_path / "original.txt")
        source.write_text("xyz")
        return selected

    monkeypatch.setattr(_files, "directory_files", select_then_replace)
    monkeypatch.setattr(resource_files, "directory_files", select_then_replace)
    with pytest.raises(ValueError, match="changed after directory selection"):
        await prepare_directory(sdk, tmp_path)
    assert not server.requests


async def test_directory_destination_uses_actual_filename_length(
    sdk: OpenAI | AsyncOpenAI, server: FilesServer, tmp_path: Path
) -> None:
    (tmp_path / "a").write_text("abc")
    destination = "/workspace/" + "x" * (4094 - len("/workspace/"))
    if isinstance(sdk, AsyncOpenAI):
        prepared = await sdk.beta.agents.environments.files.prepare_directory(
            tmp_path, destination=destination, include=["a"]
        )
    else:
        prepared = sdk.beta.agents.environments.files.prepare_directory(
            tmp_path, destination=destination, include=["a"]
        )
    assert len(prepared.files[0]["path"]) == 4096
    assert server.uploads == 1


async def test_async_path_reads_run_off_event_loop(
    sdk: OpenAI | AsyncOpenAI, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import threading

    from openai.lib.beta.agents import _files

    if not isinstance(sdk, AsyncOpenAI):
        pytest.skip("Async disk read contract")
    source = tmp_path / "source.txt"
    source.write_text("abc")
    current_thread = threading.get_ident()
    original = _files._read_local
    calls: list[int] = []

    def read(handle: Any, length: int) -> bytes:
        assert threading.get_ident() != current_thread
        calls.append(length)
        return original(handle, length)

    monkeypatch.setattr(_files, "_read_local", read)
    await sdk.beta.agents.environments.files.prepare({"/workspace/source.txt": source})
    await sdk.beta.agents.environments.files.upload("env_test", file=source, path="/workspace/source.txt")
    assert calls == [3, 3]


@pytest.mark.parametrize("staging", [False, True])
async def test_sync_interruption_preserves_observed_uploads(
    sdk: OpenAI | AsyncOpenAI, server: FilesServer, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, staging: bool
) -> None:
    if isinstance(sdk, AsyncOpenAI):
        pytest.skip("Synchronous interruption contract")
    source = tmp_path / "source.txt"
    source.write_text("abc")

    def interrupt(*_args: Any, **_kwargs: Any) -> Any:
        raise KeyboardInterrupt()

    if staging:
        monkeypatch.setattr(sdk.beta.agents.environments.files, "create", interrupt)
        with pytest.raises(KeyboardInterrupt) as caught:
            sdk.beta.agents.environments.files.upload("env_test", file=source, path="/workspace/source.txt")
        assert vars(caught.value)["uploaded_file_id"] == "file_1"
    else:

        def after_upload() -> None:
            if server.uploads == 2:
                raise KeyboardInterrupt()

        server.after_upload = after_upload
        with pytest.raises(KeyboardInterrupt) as caught:
            sdk.beta.agents.environments.files.prepare({"/workspace/a": source, "/workspace/b": source})
        assert vars(caught.value)["prepared"].uploaded_file_ids == ["file_1"]


async def test_async_selection_cancellation_does_not_wait_for_scan(monkeypatch: pytest.MonkeyPatch) -> None:
    import threading

    import anyio

    from openai.lib.beta.agents import _files

    started = threading.Event()
    release = threading.Event()
    timer = threading.Timer(2, release.set)

    def scan(*_args: Any) -> Any:
        started.set()
        release.wait()
        return {}

    async def select() -> None:
        await _files.async_directory_files("synthetic", "/workspace/docs", ["*"])

    monkeypatch.setattr(_files, "directory_files", scan)
    timer.start()
    try:
        async with anyio.create_task_group() as tasks:
            tasks.start_soon(select)
            while not started.is_set():
                await anyio.sleep(0)
            tasks.cancel_scope.cancel()
        assert not release.is_set()
    finally:
        release.set()
        timer.cancel()


@pytest.mark.parametrize("mode", ["prepare", "directory", "upload"])
async def test_native_cancellation_keeps_opened_handles_owned_by_worker(
    sdk: OpenAI | AsyncOpenAI, server: FilesServer, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    import threading

    from openai.lib.beta.agents import _files

    if not isinstance(sdk, AsyncOpenAI):
        pytest.skip("Native async cancellation contract")
    source = tmp_path / "source.txt"
    source.write_text("abc")
    entered = threading.Event()
    release = threading.Event()
    finished = threading.Event()
    handles: list[Any] = []
    original_open = _files._open_local
    snapshot_name = "_snapshot_upload" if mode == "upload" else "_snapshot_selection"
    original_snapshot = getattr(_files, snapshot_name)

    def delayed_open(*args: Any, **kwargs: Any) -> Any:
        entered.set()
        release.wait()
        handle, size = original_open(*args, **kwargs)
        handles.append(handle)
        return handle, size

    def snapshot(*args: Any, **kwargs: Any) -> Any:
        try:
            return original_snapshot(*args, **kwargs)
        finally:
            finished.set()

    monkeypatch.setattr(_files, "_open_local", delayed_open)
    monkeypatch.setattr(_files, snapshot_name, snapshot)
    if mode == "upload":
        operation = sdk.beta.agents.environments.files.upload("env_test", file=source, path="/workspace/source.txt")
    elif mode == "directory":
        operation = sdk.beta.agents.environments.files.prepare_directory(
            tmp_path, destination="/workspace/docs", include=["*.txt"]
        )
    else:
        operation = sdk.beta.agents.environments.files.prepare({"/workspace/source.txt": source})
    task = asyncio.create_task(operation)
    try:
        await asyncio.wait_for(asyncio.to_thread(entered.wait), 2)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    finally:
        release.set()
        await asyncio.wait_for(asyncio.to_thread(finished.wait), 2)
    assert len(handles) == 1
    assert handles[0].closed
    assert not server.requests
