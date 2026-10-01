from __future__ import annotations

import json
from typing import Any
from asyncio import CancelledError
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

    @override
    def handle(self, request: httpx2.Request) -> httpx2.Response:
        self.requests.append(request)
        if request.url.path == "/v1/files":
            self.uploads += 1
            if self.uploads == self.cancel_upload:
                raise CancelledError()
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
            raise CancelledError()
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
    result = await prepare(sdk, {"/workspace/source.txt": source}, extra_headers={"X-Synthetic": "test"}, timeout=7)
    assert result.files == [{"type": "file_id", "file_id": "file_1", "path": "/workspace/source.txt"}]
    assert result.uploaded_file_ids == ["file_1"]
    assert all(request.headers["X-Synthetic"] == "test" for request in server.requests)
    assert b"abc" in server.requests[0].content


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
                "env_test", file=("source.txt", b"abc"), path="/workspace/source.txt"
            )
        return sdk.beta.agents.environments.files.upload(
            "env_test", file=("source.txt", b"abc"), path="/workspace/source.txt"
        )

    result = await stage()
    assert result.uploaded_file_id == "file_1"
    assert result.file.path == "/workspace/source.txt"
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
    with pytest.raises(CancelledError) as caught:
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
    with pytest.raises(CancelledError) as caught:
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
