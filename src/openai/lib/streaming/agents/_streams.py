from __future__ import annotations

from uuid import uuid4
from types import TracebackType
from typing import TYPE_CHECKING, Generic, Mapping, Iterable, Iterator, AsyncIterator
from collections import deque
from typing_extensions import Self

import httpx2

from ._types import ToolHandler, AsyncToolHandler
from ...._types import Omit, Headers, NotGiven, omit, not_given
from ._dispatch import ToolDispatcher, AsyncToolDispatcher, _request_options
from ...._streaming import Stream, AsyncStream
from ...beta.agents._result import (
    OutputT,
    AgentTurnResult,
    AgentTurnResultError,
    AgentOutputParseError,
    AgentTurnResultCollection,
)
from ...beta.agents._tool_error import ToolErrorHandler, AsyncToolErrorHandler
from ....types.beta.agent_session_event import AgentSessionEvent
from ....types.beta.agent_session_input_param import (
    SessionInputParamAgentSessionInputMessage,
)
from ....types.beta.agent_session_input_message_param import AgentSessionInputMessageParam

if TYPE_CHECKING:
    from ....resources.beta.agents.sessions.sessions import Sessions, AsyncSessions


def _input_key(idempotency_key: str | Omit, headers: Headers | None) -> str | Omit:
    # As with other SDK methods, extra_headers overrides the named parameter.
    # Consume it here so differing header capitalization cannot append a second key.
    for key, value in (headers or {}).items():
        if key.lower() == "idempotency-key":
            return value
    return str(uuid4()) if isinstance(idempotency_key, Omit) else idempotency_key


def _input_event(input: str | Iterable[AgentSessionInputMessageParam]) -> SessionInputParamAgentSessionInputMessage:
    messages: list[AgentSessionInputMessageParam]
    if isinstance(input, str):
        if not input:
            raise ValueError("input must not be empty")
        messages = [{"role": "user", "content": [{"type": "input_text", "text": input}]}]
    else:
        messages = list(input)
        if not messages:
            raise ValueError("input must not be empty")
    return {"type": "agent.session.input.message", "input": messages}


_RECENT_EVENT_LIMIT = 1024


class _TurnState:
    def __init__(self) -> None:
        self.turn_id: str | None = None
        self.turn_ended = False
        self.event_ids: set[str] = set()
        self.recent_events: deque[str] = deque()

    def accept(self, event: AgentSessionEvent) -> bool:
        if event.event_id in self.event_ids:
            return False
        # Suppress recent duplicate deliveries without retaining every text delta.
        # Tool calls are tracked separately for the full invocation.
        if len(self.recent_events) == _RECENT_EVENT_LIMIT:
            self.event_ids.remove(self.recent_events.popleft())
        self.recent_events.append(event.event_id)
        self.event_ids.add(event.event_id)
        if event.type == "agent.session.turn.created" and event.turn.subagent_id is None and self.turn_id is None:
            self.turn_id = event.turn_id
        if (
            event.type == "agent.session.turn.completed"
            or event.type == "agent.session.turn.failed"
            or event.type == "agent.session.turn.cancelled"
        ):
            if self.turn_id is not None and event.turn_id == self.turn_id:
                self.turn_ended = True
        return True

    def terminal(self, event: AgentSessionEvent) -> bool:
        return event.type == "agent.session.failed" or (event.type == "agent.session.idle" and self.turn_ended)


class AgentSessionStream(Generic[OutputT]):
    """Submit input to an idle session and stream through the resulting turn's terminal session event.

    Use as a context manager. Only one caller may submit input to this session while
    the helper runs: the input endpoint does not return a turn ID for correlating
    concurrent writers. Initial idle events and subagent turn completions do not
    end iteration. Failed/cancelled turns remain visible as events; an unexpected
    end of the connection raises RuntimeError. Closing the stream does not cancel
    the backend turn.

    Optional tool handlers run sequentially during iteration, after their call
    event is yielded. Unregistered tools are left for the caller to handle. A
    handler exception submits a generic failure result without exception text.
    Input and tool submissions each use an idempotency key across retries. The
    optional idempotency_key argument applies only to the input submission.
    """

    def __init__(
        self,
        sessions: Sessions,
        session_id: str,
        *,
        input: str | Iterable[AgentSessionInputMessageParam],
        output_type: type[OutputT] | None = None,
        tool_handlers: Mapping[str, ToolHandler] | None = None,
        on_tool_error: ToolErrorHandler | None = None,
        idempotency_key: str | Omit = omit,
        extra_headers: Headers | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> None:
        self._sessions = sessions
        self._session_id = session_id
        self._input = _input_event(input)
        self._dispatcher = ToolDispatcher(
            sessions, tool_handlers, on_tool_error=on_tool_error, extra_headers=extra_headers, timeout=timeout
        )
        self._handlers = self._dispatcher.handlers
        self._idempotency_key = _input_key(idempotency_key, extra_headers)
        self._options = _request_options({"extra_headers": extra_headers, "timeout": timeout})
        self._state = _TurnState()
        self._collection: AgentTurnResultCollection[OutputT] = AgentTurnResultCollection(session_id, output_type)
        self._stream: Stream[AgentSessionEvent] | None = None
        self._iterator: Iterator[AgentSessionEvent] | None = None
        self._entered = False
        self._closed = False

    def __enter__(self) -> Self:
        if self._entered or self._closed:
            raise RuntimeError("An AgentSessionStream can only be entered once")
        self._entered = True
        session = self._sessions.retrieve(self._session_id, **self._options)
        if session.status != "idle":
            raise ValueError(
                "sessions.stream requires an idle session; use sessions.events.stream to follow an active session"
            )
        self._stream = self._sessions.events.stream(self._session_id, **self._options)
        try:
            self._sessions.events.create(
                self._session_id, events=[self._input], idempotency_key=self._idempotency_key, **self._options
            )
        except BaseException:
            self.close()
            raise
        self._iterator = self._iterate()
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        self.close()

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> AgentSessionEvent:
        if self._closed:
            raise StopIteration
        if self._iterator is None:
            raise RuntimeError("Use sessions.stream in a with block")
        return next(self._iterator)

    def until_done(self) -> None:
        """Consume the remaining events, including any registered tool calls."""
        for _ in self:
            pass

    def with_result_collection(self) -> Self:
        """Beta: retain final messages for a result; call before consuming events."""
        self._collection.enable()
        return self

    def get_final_result(self) -> AgentTurnResult[OutputT]:
        """Beta: drain this turn, executing handlers, and collect its final answer.

        Raises AgentTurnResultError when a successful complete result cannot be
        established. Draining executes registered handlers and submits their
        outputs. Result properties themselves do not execute handlers.
        To iterate first, call with_result_collection() before consuming events.
        """
        collector = self._collection.enable()
        try:
            collector.check_outcome(self._handlers)
            if not collector.is_done():
                for _ in self:
                    collector.check_outcome(self._handlers)
                    if collector.is_done():
                        break
            return self._collection.result()
        except (AgentTurnResultError, AgentOutputParseError):
            raise
        except Exception as error:
            self._collection.record_error(error)
            raise collector.error("observation_failed") from error
        finally:
            self.close()

    def close(self) -> None:
        """Close the event connection without cancelling the backend turn."""
        self._closed = True
        if self._stream is not None:
            self._stream.close()

    def _iterate(self) -> Iterator[AgentSessionEvent]:
        assert self._stream is not None
        try:
            for event in self._stream:
                if not self._state.accept(event):
                    continue
                self._collection.accept(event)
                terminal = self._state.terminal(event)
                if terminal:
                    self.close()
                pending = self._dispatcher.prepare(event)
                yield event
                if terminal or self._closed:
                    return
                if pending is not None:
                    self._dispatcher.dispatch(pending)
            raise RuntimeError("Session event stream ended before the turn reached idle or failed")
        except Exception as error:
            self._collection.record_error(error)
            raise
        finally:
            self.close()


class AsyncAgentSessionStream(Generic[OutputT]):
    """Async counterpart of AgentSessionStream; use with ``async with``.

    Requires an idle session with a single input writer. Handlers may return a
    value or an awaitable; synchronous handlers run inline, without a thread
    pool. Cancellation propagates and closes the event connection. It does not
    cancel the backend turn.
    """

    def __init__(
        self,
        sessions: AsyncSessions,
        session_id: str,
        *,
        input: str | Iterable[AgentSessionInputMessageParam],
        output_type: type[OutputT] | None = None,
        tool_handlers: Mapping[str, AsyncToolHandler] | None = None,
        on_tool_error: AsyncToolErrorHandler | None = None,
        idempotency_key: str | Omit = omit,
        extra_headers: Headers | None = None,
        timeout: float | httpx2.Timeout | None | NotGiven = not_given,
    ) -> None:
        self._sessions = sessions
        self._session_id = session_id
        self._input = _input_event(input)
        self._dispatcher = AsyncToolDispatcher(
            sessions, tool_handlers, on_tool_error=on_tool_error, extra_headers=extra_headers, timeout=timeout
        )
        self._handlers = self._dispatcher.handlers
        self._idempotency_key = _input_key(idempotency_key, extra_headers)
        self._options = _request_options({"extra_headers": extra_headers, "timeout": timeout})
        self._state = _TurnState()
        self._collection: AgentTurnResultCollection[OutputT] = AgentTurnResultCollection(session_id, output_type)
        self._stream: AsyncStream[AgentSessionEvent] | None = None
        self._iterator: AsyncIterator[AgentSessionEvent] | None = None
        self._entered = False
        self._closed = False

    async def __aenter__(self) -> Self:
        if self._entered or self._closed:
            raise RuntimeError("An AsyncAgentSessionStream can only be entered once")
        self._entered = True
        session = await self._sessions.retrieve(self._session_id, **self._options)
        if session.status != "idle":
            raise ValueError(
                "sessions.stream requires an idle session; use sessions.events.stream to follow an active session"
            )
        self._stream = await self._sessions.events.stream(self._session_id, **self._options)
        try:
            await self._sessions.events.create(
                self._session_id, events=[self._input], idempotency_key=self._idempotency_key, **self._options
            )
        except BaseException:
            await self.close()
            raise
        self._iterator = self._iterate()
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, exc_tb: TracebackType | None
    ) -> None:
        await self.close()

    def __aiter__(self) -> Self:
        return self

    async def __anext__(self) -> AgentSessionEvent:
        if self._closed:
            raise StopAsyncIteration
        if self._iterator is None:
            raise RuntimeError("Use sessions.stream in an async with block")
        return await self._iterator.__anext__()

    async def until_done(self) -> None:
        """Consume the remaining events, including any registered tool calls."""
        async for _ in self:
            pass

    def with_result_collection(self) -> Self:
        """Beta: retain final messages for a result; call before consuming events."""
        self._collection.enable()
        return self

    async def get_final_result(self) -> AgentTurnResult[OutputT]:
        """Beta: drain this turn, executing handlers, and collect its final answer.

        Raises AgentTurnResultError when a successful complete result cannot be
        established. Draining executes registered handlers and submits their
        outputs. Result properties themselves do not execute handlers.
        To iterate first, call with_result_collection() before consuming events.
        """
        collector = self._collection.enable()
        try:
            collector.check_outcome(self._handlers)
            if not collector.is_done():
                async for _ in self:
                    collector.check_outcome(self._handlers)
                    if collector.is_done():
                        break
            return self._collection.result()
        except (AgentTurnResultError, AgentOutputParseError):
            raise
        except Exception as error:
            self._collection.record_error(error)
            raise collector.error("observation_failed") from error
        finally:
            await self.close()

    async def close(self) -> None:
        """Close the event connection without cancelling the backend turn."""
        self._closed = True
        if self._stream is not None:
            await self._stream.close()

    async def _iterate(self) -> AsyncIterator[AgentSessionEvent]:
        assert self._stream is not None
        try:
            async for event in self._stream:
                if not self._state.accept(event):
                    continue
                self._collection.accept(event)
                terminal = self._state.terminal(event)
                if terminal:
                    await self.close()
                pending = self._dispatcher.prepare(event)
                yield event
                if terminal or self._closed:
                    return
                if pending is not None:
                    await self._dispatcher.dispatch(pending)
            raise RuntimeError("Session event stream ended before the turn reached idle or failed")
        except Exception as error:
            self._collection.record_error(error)
            raise
        finally:
            await self.close()
