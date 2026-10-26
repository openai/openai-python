from __future__ import annotations

from typing import Any, Iterator, AsyncIterator
from pathlib import Path
from typing_extensions import override

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from openai._compat import model_parse
from openai.lib.beta.agents import AgentTurnResult
from openai.types.beta.agents.sessions.turn import Turn
from tests.lib.streaming.agents.test_streams import Server, sdk as sdk, turn_event


class ArtifactBody(httpx2.SyncByteStream, httpx2.AsyncByteStream):
    def __init__(self) -> None:
        self.closed = False
        self.chunks = 0

    @override
    def __iter__(self) -> Iterator[bytes]:
        for value in (b"report", b"-", b"done"):
            self.chunks += 1
            yield value

    @override
    async def __aiter__(self) -> AsyncIterator[bytes]:
        for value in self:
            yield value

    @override
    def close(self) -> None:
        self.closed = True

    @override
    async def aclose(self) -> None:
        self.closed = True


def artifact(id: str, turn_id: str = "turn_root") -> dict[str, Any]:
    return {
        "id": id,
        "created_at": 1,
        "environment_id": "env_test",
        "object": "agent.session.artifact",
        "path": "/workspace/outputs/report.md",
        "session_id": "session_test",
        "size_bytes": 11,
        "turn_id": turn_id,
    }


class ArtifactServer(Server):
    def __init__(self) -> None:
        super().__init__()
        self.artifacts = [artifact("old", "old_turn"), artifact("selected")]
        self.content = ArtifactBody()

    @override
    def handle(self, request: httpx2.Request) -> httpx2.Response:
        self.requests.append(request)
        if request.url.path.endswith("/content"):
            assert request.url.path.endswith("/selected/content")
            return httpx2.Response(200, headers={"content-type": "application/octet-stream"}, stream=self.content)
        after = request.url.params.get("after")
        offset = next((index + 1 for index, value in enumerate(self.artifacts) if value["id"] == after), 0)
        return httpx2.Response(
            200,
            json={
                "object": "list",
                "data": self.artifacts[offset : offset + 1],
                "has_more": offset + 1 < len(self.artifacts),
            },
        )


@pytest.fixture
def server() -> ArtifactServer:
    return ArtifactServer()


def result() -> AgentTurnResult:
    return AgentTurnResult(turn=model_parse(Turn, turn_event("completed")["turn"]), messages=[])


async def download(sdk: OpenAI | AsyncOpenAI, path: Path) -> Any:
    if isinstance(sdk, AsyncOpenAI):
        return await sdk.beta.agents.sessions.artifacts.for_result(result()).download(
            "/workspace/outputs/report.md",
            to=path,
            extra_headers={"X-Synthetic": "test"},
            extra_query={"synthetic": "query"},
            extra_body={"synthetic": "body"},
            timeout=7,
        )
    return sdk.beta.agents.sessions.artifacts.for_result(result()).download(
        "/workspace/outputs/report.md",
        to=path,
        extra_headers={"X-Synthetic": "test"},
        extra_query={"synthetic": "query"},
        extra_body={"synthetic": "body"},
        timeout=7,
    )


async def test_exact_turn_artifact_pagination_streaming_and_options(
    sdk: OpenAI | AsyncOpenAI, server: ArtifactServer, tmp_path: Path
) -> None:
    path = tmp_path / "chosen.md"
    selected = await download(sdk, path)
    assert selected.id == "selected"
    assert path.read_bytes() == b"report-done"
    assert len(server.requests) == 3
    assert server.content.chunks == 3
    assert server.content.closed
    assert all(request.headers["X-Synthetic"] == "test" for request in server.requests)
    assert all(request.url.params["synthetic"] == "query" for request in server.requests)
    assert all(request.extensions["timeout"]["read"] == 7 for request in server.requests)


@pytest.mark.parametrize("ambiguous", [False, True])
async def test_missing_or_ambiguous_artifact_does_not_open_destination(
    sdk: OpenAI | AsyncOpenAI, server: ArtifactServer, tmp_path: Path, ambiguous: bool
) -> None:
    server.artifacts = [artifact("selected"), artifact("duplicate")] if ambiguous else [artifact("old", "old_turn")]
    path = tmp_path / "chosen.md"
    path.write_text("keep")
    with pytest.raises(ValueError, match="More than one" if ambiguous else "No artifact"):
        await download(sdk, path)
    assert path.read_text() == "keep"
    assert server.content.chunks == 0


async def test_native_binary_content_matches_exact_turn_and_preserves_options(
    sdk: OpenAI | AsyncOpenAI, server: ArtifactServer
) -> None:
    from openai._legacy_response import HttpxBinaryResponseContent

    options: Any = {"extra_headers": {"X-Synthetic": "test"}, "extra_query": {"synthetic": "query"}, "timeout": 7}
    content = (
        await sdk.beta.agents.sessions.artifacts.for_result(result()).content("/workspace/outputs/report.md", **options)
        if isinstance(sdk, AsyncOpenAI)
        else sdk.beta.agents.sessions.artifacts.for_result(result()).content("/workspace/outputs/report.md", **options)
    )
    assert isinstance(content, HttpxBinaryResponseContent)
    assert content.content == b"report-done"
    assert len(server.requests) == 3
    assert all(request.url.params["synthetic"] == "query" for request in server.requests)
    assert all(request.headers["X-Synthetic"] == "test" for request in server.requests)
    assert all(request.extensions["timeout"]["read"] == 7 for request in server.requests)
    assert server.content.closed


@pytest.mark.parametrize("ambiguous", [False, True])
async def test_native_content_rejects_missing_or_ambiguous_artifact(
    sdk: OpenAI | AsyncOpenAI, server: ArtifactServer, ambiguous: bool
) -> None:
    server.artifacts = [artifact("selected"), artifact("duplicate")] if ambiguous else [artifact("old", "old_turn")]
    with pytest.raises(ValueError, match="More than one" if ambiguous else "No artifact"):
        if isinstance(sdk, AsyncOpenAI):
            await sdk.beta.agents.sessions.artifacts.for_result(result()).content("/workspace/outputs/report.md")
        else:
            sdk.beta.agents.sessions.artifacts.for_result(result()).content("/workspace/outputs/report.md")
    assert server.content.chunks == 0
