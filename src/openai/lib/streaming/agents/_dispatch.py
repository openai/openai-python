from __future__ import annotations

import inspect
from copy import deepcopy
from uuid import uuid4
from typing import TYPE_CHECKING, Any, Generic, Mapping, TypeVar
from typing_extensions import TypedDict

import httpx2

from ._tools import ToolInvocation, failed_event, result_event, is_pending_call_race
from ._types import ToolHandler, AsyncToolHandler
from ...._types import Headers, NotGiven, not_given
from ...._constants import RAW_RESPONSE_HEADER
from ...._exceptions import BadRequestError
from ...beta.agents._tool_error import ToolErrorHandler, AsyncToolErrorHandler
from ....types.beta.agent_session_event import AgentSessionEvent
from ....types.beta.agent_function_call_item import AgentFunctionCallItem
from ....types.beta.agent_session_input_param import SessionInputParamAgentSessionInputToolResult

if TYPE_CHECKING:
    from ....resources.beta.agents.sessions.sessions import Sessions, AsyncSessions


class _RequestOptions(TypedDict):
    extra_headers: Headers | None
    timeout: float | httpx2.Timeout | None | NotGiven


def _request_options(options: _RequestOptions) -> _RequestOptions:
    headers = options["extra_headers"]
    return {
        **options,
        "extra_headers": {
            key: value
            for key, value in headers.items()
            if key.lower() not in ("idempotency-key", RAW_RESPONSE_HEADER.lower())
        }
        if headers is not None
        else None,
    }


HandlerT = TypeVar("HandlerT", ToolHandler, AsyncToolHandler)


class _Dispatcher(Generic[HandlerT]):
    def __init__(self, handlers: Mapping[str, HandlerT] | None) -> None:
        self.handlers: dict[str, HandlerT] = dict(handlers or {})
        self._handled_calls: set[tuple[str, str]] = set()

    def prepare(self, event: AgentSessionEvent) -> tuple[str, AgentFunctionCallItem, HandlerT] | None:
        if event.type != "agent.session.turn.item.added" or event.item.type != "function_call":
            return None
        call = event.item
        handler = self.handlers.get(call.name)
        key = (call.turn_id, call.call_id)
        if handler is None or key in self._handled_calls:
            return None
        self._handled_calls.add(key)
        # Capture routing and arguments before exposing the mutable event.
        return event.session_id, deepcopy(call), handler


class ToolDispatcher(_Dispatcher[ToolHandler]):
    def __init__(
        self,
        sessions: Sessions,
        handlers: Mapping[str, ToolHandler] | None,
        *,
        on_tool_error: ToolErrorHandler | None = None,
        extra_headers: Headers | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> None:
        super().__init__(handlers)
        self._sessions = sessions
        self._on_tool_error = on_tool_error
        self._options = _request_options({"extra_headers": extra_headers, "timeout": timeout})

    def dispatch(self, pending: tuple[str, AgentFunctionCallItem, ToolHandler]) -> None:
        session_id, call, handler = pending
        invocation = ToolInvocation(session_id, call)
        try:
            output: Any = invocation.invoke(handler)
            if inspect.isawaitable(output):
                close = getattr(output, "close", None)
                if callable(close):
                    close()
                raise TypeError("Async tool handlers require AsyncOpenAI")
            invocation.stage = "output"
            result = result_event(call, output)
        except Exception as error:
            result = failed_event(call)
            if self._on_tool_error is not None:
                try:
                    notification: Any = self._on_tool_error(invocation.failure(error))
                    # A sync stream cannot await an async observer.
                    if inspect.iscoroutine(notification):
                        notification.close()
                except Exception:
                    # Observer failures must not change tool submission or the turn result.
                    pass
        self._submit_result(session_id, result)

    def _submit_result(self, session_id: str, result: SessionInputParamAgentSessionInputToolResult) -> None:
        # Reuse one key for transport retries and the pending-call registration race.
        # An input-specific key in extra_headers must not be reused for tool results.
        idempotency_key = str(uuid4())
        for delay in (0.1, 0.3, 0.6, None):
            try:
                self._sessions.events.create(
                    session_id, events=[result], idempotency_key=idempotency_key, **self._options
                )
                return
            except BadRequestError as error:
                if delay is None or not is_pending_call_race(error, result["call_id"]):
                    raise
                self._sessions._sleep(delay)


class AsyncToolDispatcher(_Dispatcher[AsyncToolHandler]):
    def __init__(
        self,
        sessions: AsyncSessions,
        handlers: Mapping[str, AsyncToolHandler] | None,
        *,
        on_tool_error: AsyncToolErrorHandler | None = None,
        extra_headers: Headers | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> None:
        super().__init__(handlers)
        self._sessions = sessions
        self._on_tool_error = on_tool_error
        self._options = _request_options({"extra_headers": extra_headers, "timeout": timeout})

    async def dispatch(self, pending: tuple[str, AgentFunctionCallItem, AsyncToolHandler]) -> None:
        session_id, call, handler = pending
        invocation = ToolInvocation(session_id, call)
        try:
            output = invocation.invoke(handler)
            if inspect.isawaitable(output):
                output = await output
            invocation.stage = "output"
            result = result_event(call, output)
        except Exception as error:
            result = failed_event(call)
            if self._on_tool_error is not None:
                try:
                    notification: Any = self._on_tool_error(invocation.failure(error))
                    if inspect.isawaitable(notification):
                        await notification
                except Exception:
                    # Observer failures must not change tool submission or the turn result.
                    pass
        await self._submit_result(session_id, result)

    async def _submit_result(self, session_id: str, result: SessionInputParamAgentSessionInputToolResult) -> None:
        # Reuse one key for transport retries and the pending-call registration race.
        # An input-specific key in extra_headers must not be reused for tool results.
        idempotency_key = str(uuid4())
        for delay in (0.1, 0.3, 0.6, None):
            try:
                await self._sessions.events.create(
                    session_id, events=[result], idempotency_key=idempotency_key, **self._options
                )
                return
            except BadRequestError as error:
                if delay is None or not is_pending_call_race(error, result["call_id"]):
                    raise
                await self._sessions._sleep(delay)
