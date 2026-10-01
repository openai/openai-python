from __future__ import annotations

from os import PathLike
from typing import TYPE_CHECKING

import httpx2

from ._result import AgentTurnResult
from ...._types import Headers, NotGiven, not_given
from ....types.beta.agents.sessions.session_artifact import SessionArtifact

if TYPE_CHECKING:
    from ....resources.beta.agents.sessions.artifacts import Artifacts, AsyncArtifacts


class AgentResultArtifacts:
    """Beta: look up immutable artifacts from one completed turn."""

    def __init__(self, resource: Artifacts, result: AgentTurnResult) -> None:
        self._resource = resource
        self._session_id = result.session_id
        self._turn_id = result.turn_id

    def download(
        self,
        path: str,
        *,
        to: str | PathLike[str],
        extra_headers: Headers | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> SessionArtifact:
        """Download one exact turn/path to an explicit local destination."""
        selected: SessionArtifact | None = None
        for artifact in self._resource.list(self._session_id, extra_headers=extra_headers, timeout=timeout):
            if artifact.session_id == self._session_id and artifact.turn_id == self._turn_id and artifact.path == path:
                if selected is not None:
                    raise ValueError("More than one artifact matches this turn and path")
                selected = artifact
        if selected is None:
            raise ValueError("No artifact matches this turn and path")
        with self._resource.with_streaming_response.content(
            selected.id, session_id=self._session_id, extra_headers=extra_headers, timeout=timeout
        ) as content:
            content.stream_to_file(to)
        return selected


class AsyncAgentResultArtifacts:
    """Beta: async artifact downloads from one completed turn."""

    def __init__(self, resource: AsyncArtifacts, result: AgentTurnResult) -> None:
        self._resource = resource
        self._session_id = result.session_id
        self._turn_id = result.turn_id

    async def download(
        self,
        path: str,
        *,
        to: str | PathLike[str],
        extra_headers: Headers | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> SessionArtifact:
        """Download one exact turn/path to an explicit local destination."""
        selected: SessionArtifact | None = None
        async for artifact in self._resource.list(self._session_id, extra_headers=extra_headers, timeout=timeout):
            if artifact.session_id == self._session_id and artifact.turn_id == self._turn_id and artifact.path == path:
                if selected is not None:
                    raise ValueError("More than one artifact matches this turn and path")
                selected = artifact
        if selected is None:
            raise ValueError("No artifact matches this turn and path")
        async with self._resource.with_streaming_response.content(
            selected.id, session_id=self._session_id, extra_headers=extra_headers, timeout=timeout
        ) as content:
            await content.stream_to_file(to)
        return selected
