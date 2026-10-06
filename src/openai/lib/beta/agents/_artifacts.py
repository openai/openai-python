from __future__ import annotations

from os import PathLike
from typing import TYPE_CHECKING

import httpx2

from ._files import _RequestOptions
from ._result import AgentTurnResult
from ...._types import Body, Query, Headers, NotGiven, not_given
from ...._legacy_response import HttpxBinaryResponseContent
from ....types.beta.agents.sessions.session_artifact import SessionArtifact

if TYPE_CHECKING:
    from ....resources.beta.agents.sessions.artifacts import Artifacts, AsyncArtifacts


class AgentResultArtifacts:
    """Beta: look up immutable artifacts from one completed turn."""

    def __init__(self, resource: Artifacts, result: AgentTurnResult) -> None:
        self._resource = resource
        self._session_id = result.session_id
        self._turn_id = result.turn_id

    def content(
        self,
        path: str,
        *,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> HttpxBinaryResponseContent:
        """Read one exact turn/path using the SDK's native binary response."""
        options: _RequestOptions = {
            "extra_headers": extra_headers,
            "extra_query": extra_query,
            "extra_body": extra_body,
            "timeout": timeout,
        }
        selected = self._find(path, options)
        return self._resource.content(selected.id, session_id=self._session_id, **options)

    def download(
        self,
        path: str,
        *,
        to: str | PathLike[str],
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> SessionArtifact:
        """Download one exact turn/path to an explicit local destination."""
        options: _RequestOptions = {
            "extra_headers": extra_headers,
            "extra_query": extra_query,
            "extra_body": extra_body,
            "timeout": timeout,
        }
        selected = self._find(path, options)
        with self._resource.with_streaming_response.content(
            selected.id,
            session_id=self._session_id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        ) as content:
            content.stream_to_file(to)
        return selected

    def _find(self, path: str, options: _RequestOptions) -> SessionArtifact:
        selected: SessionArtifact | None = None
        for artifact in self._resource.list(
            self._session_id,
            **options,
        ):
            if artifact.session_id == self._session_id and artifact.turn_id == self._turn_id and artifact.path == path:
                if selected is not None:
                    raise ValueError("More than one artifact matches this turn and path")
                selected = artifact
        if selected is None:
            raise ValueError("No artifact matches this turn and path")
        return selected


class AsyncAgentResultArtifacts:
    """Beta: async artifact downloads from one completed turn."""

    def __init__(self, resource: AsyncArtifacts, result: AgentTurnResult) -> None:
        self._resource = resource
        self._session_id = result.session_id
        self._turn_id = result.turn_id

    async def content(
        self,
        path: str,
        *,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> HttpxBinaryResponseContent:
        """Read one exact turn/path using the SDK's native binary response."""
        options: _RequestOptions = {
            "extra_headers": extra_headers,
            "extra_query": extra_query,
            "extra_body": extra_body,
            "timeout": timeout,
        }
        selected = await self._find(path, options)
        return await self._resource.content(selected.id, session_id=self._session_id, **options)

    async def download(
        self,
        path: str,
        *,
        to: str | PathLike[str],
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> SessionArtifact:
        """Download one exact turn/path to an explicit local destination."""
        options: _RequestOptions = {
            "extra_headers": extra_headers,
            "extra_query": extra_query,
            "extra_body": extra_body,
            "timeout": timeout,
        }
        selected = await self._find(path, options)
        async with self._resource.with_streaming_response.content(
            selected.id,
            session_id=self._session_id,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        ) as content:
            await content.stream_to_file(to)
        return selected

    async def _find(self, path: str, options: _RequestOptions) -> SessionArtifact:
        selected: SessionArtifact | None = None
        async for artifact in self._resource.list(
            self._session_id,
            **options,
        ):
            if artifact.session_id == self._session_id and artifact.turn_id == self._turn_id and artifact.path == path:
                if selected is not None:
                    raise ValueError("More than one artifact matches this turn and path")
                selected = artifact
        if selected is None:
            raise ValueError("No artifact matches this turn and path")
        return selected
