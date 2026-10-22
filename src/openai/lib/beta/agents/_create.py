"""Local output binding and tool dispatch for generated session creation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping, TypeVar, cast
from dataclasses import dataclass

import httpx2

from ._output import bind_output_type, with_output_schema
from ...._types import Omit, Headers, NotGiven
from ...streaming.agents import ToolHandler, AsyncToolHandler
from ...streaming.agents._dispatch import ToolDispatcher, AsyncToolDispatcher
from ....types.beta.agents.session_create_params import Agent

if TYPE_CHECKING:
    from ....resources.beta.agents.sessions import Sessions, AsyncSessions

ResponseT = TypeVar("ResponseT")


@dataclass
class SessionCreateContext:
    body: dict[str, object]
    output_type: type[Any] | None
    dispatcher: ToolDispatcher | AsyncToolDispatcher | None

    def post_parser(self, response: ResponseT) -> ResponseT:
        return bind_output_type(response, self.output_type, self.dispatcher)


def prepare_session_create(
    resource: Sessions,
    body: dict[str, object],
    *,
    output_type: type[Any] | None,
    tool_handlers: Mapping[str, ToolHandler] | None,
    stream: object,
    extra_headers: Headers | None,
    timeout: float | httpx2.Timeout | None | NotGiven,
) -> SessionCreateContext:
    body["agent"] = with_output_schema(cast("Agent | Omit", body["agent"]), output_type)
    if tool_handlers is not None and stream is not True:
        raise ValueError("tool_handlers requires stream=True")
    dispatcher = (
        ToolDispatcher(resource, tool_handlers, extra_headers=extra_headers, timeout=timeout) if tool_handlers else None
    )
    return SessionCreateContext(body, output_type, dispatcher)


def prepare_async_session_create(
    resource: AsyncSessions,
    body: dict[str, object],
    *,
    output_type: type[Any] | None,
    tool_handlers: Mapping[str, AsyncToolHandler] | None,
    stream: object,
    extra_headers: Headers | None,
    timeout: float | httpx2.Timeout | None | NotGiven,
) -> SessionCreateContext:
    body["agent"] = with_output_schema(cast("Agent | Omit", body["agent"]), output_type)
    if tool_handlers is not None and stream is not True:
        raise ValueError("tool_handlers requires stream=True")
    dispatcher = (
        AsyncToolDispatcher(resource, tool_handlers, extra_headers=extra_headers, timeout=timeout)
        if tool_handlers
        else None
    )
    return SessionCreateContext(body, output_type, dispatcher)
