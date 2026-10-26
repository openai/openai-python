from __future__ import annotations

from typing import Generic, Iterator, AsyncIterator
from typing_extensions import Self, override

from ._result import OutputT, AgentTurnResult, AgentTurnResultError, AgentOutputParseError, AgentTurnResultCollection
from ...._compat import cached_property
from ...._streaming import Stream, AsyncStream
from ...streaming.agents._dispatch import ToolDispatcher, AsyncToolDispatcher
from ....types.beta.agent_session_event import AgentSessionEvent


class AgentSessionEventStream(Stream[AgentSessionEvent], Generic[OutputT]):
    """Beta: a creation event stream that can collect its initial turn's result.

    Event iteration and response access behave like ``Stream``. Registered tool
    handlers execute during iteration, after their call event is yielded.
    Supply initial input when creating a session to collect its turn result.
    """

    _dispatcher: ToolDispatcher | None = None

    @cached_property
    def _collection(self) -> AgentTurnResultCollection[OutputT]:
        return AgentTurnResultCollection()

    @override
    def __stream__(self) -> Iterator[AgentSessionEvent]:
        try:
            for event in super().__stream__():
                self._collection.accept(event)
                pending = self._dispatcher.prepare(event) if self._dispatcher is not None else None
                yield event
                if pending is not None and self._dispatcher is not None and not self.response.is_closed:
                    self._dispatcher.dispatch(pending)
        except Exception as error:
            self._collection.record_error(error)
            raise
        finally:
            self.close()

    def with_result_collection(self) -> Self:
        """Beta: retain final messages for a result; call before consuming events."""
        self._collection.enable()
        return self

    def get_final_result(self) -> AgentTurnResult[OutputT]:
        """Consume remaining events and return the successful initial turn result.

        Raises AgentTurnResultError for an unsuccessful or unobserved outcome.
        Collection starts automatically on a fresh stream. To iterate first, call
        with_result_collection() before consuming events. Repeated calls return
        the cached result without consuming more events.
        """
        collector = self._collection.enable()
        try:
            collector.check_outcome(self._dispatcher.handlers if self._dispatcher is not None else ())
            if not collector.is_done():
                for _ in self:
                    collector.check_outcome(self._dispatcher.handlers if self._dispatcher is not None else ())
                    if collector.is_done():
                        break
            return self._collection.result()
        except (AgentTurnResultError, AgentOutputParseError):
            raise
        except Exception as error:
            collector.cause = error
            raise collector.error("observation_failed") from error
        finally:
            self.close()


class AsyncAgentSessionEventStream(AsyncStream[AgentSessionEvent], Generic[OutputT]):
    """Beta: asynchronous counterpart of AgentSessionEventStream."""

    _dispatcher: AsyncToolDispatcher | None = None

    @cached_property
    def _collection(self) -> AgentTurnResultCollection[OutputT]:
        return AgentTurnResultCollection()

    @override
    async def __stream__(self) -> AsyncIterator[AgentSessionEvent]:
        try:
            async for event in super().__stream__():
                self._collection.accept(event)
                pending = self._dispatcher.prepare(event) if self._dispatcher is not None else None
                yield event
                if pending is not None and self._dispatcher is not None and not self.response.is_closed:
                    await self._dispatcher.dispatch(pending)
        except Exception as error:
            self._collection.record_error(error)
            raise
        finally:
            await self.close()

    def with_result_collection(self) -> Self:
        """Beta: retain final messages for a result; call before consuming events."""
        self._collection.enable()
        return self

    async def get_final_result(self) -> AgentTurnResult[OutputT]:
        """Consume remaining events and return the successful initial turn result.

        Enables collection on a fresh stream. To iterate first, call
        with_result_collection() before consuming events.
        """
        collector = self._collection.enable()
        try:
            collector.check_outcome(self._dispatcher.handlers if self._dispatcher is not None else ())
            if not collector.is_done():
                async for _ in self:
                    collector.check_outcome(self._dispatcher.handlers if self._dispatcher is not None else ())
                    if collector.is_done():
                        break
            return self._collection.result()
        except (AgentTurnResultError, AgentOutputParseError):
            raise
        except Exception as error:
            collector.cause = error
            raise collector.error("observation_failed") from error
        finally:
            await self.close()
