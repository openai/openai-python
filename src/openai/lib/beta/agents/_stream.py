from __future__ import annotations

from typing import Iterator, AsyncIterator
from typing_extensions import Self, override

from ._result import AgentTurnResult, AgentTurnResultError, AgentTurnResultCollection
from ...._compat import cached_property
from ...._streaming import Stream, AsyncStream
from ....types.beta.agent_session_event import AgentSessionEvent


class AgentSessionEventStream(Stream[AgentSessionEvent]):
    """Beta: a creation event stream that can collect its initial turn's result.

    Event iteration and response access behave like ``Stream``. Collection does
    not execute local tools; required actions are available on the result error.
    Supply initial input when creating a session to collect its turn result.
    """

    @cached_property
    def _collection(self) -> AgentTurnResultCollection:
        return AgentTurnResultCollection()

    @override
    def __stream__(self) -> Iterator[AgentSessionEvent]:
        try:
            for event in super().__stream__():
                self._collection.accept(event)
                yield event
        except Exception as error:
            self._collection.record_error(error)
            raise

    def with_result_collection(self) -> Self:
        """Beta: retain final messages for a result; call before consuming events."""
        self._collection.enable()
        return self

    def get_final_result(self) -> AgentTurnResult:
        """Consume remaining events and return the successful initial turn result.

        Raises AgentTurnResultError for an unsuccessful or unobserved outcome.
        Collection starts automatically on a fresh stream. To iterate first, call
        with_result_collection() before consuming events. Repeated calls return
        the cached result without consuming more events.
        """
        collector = self._collection.enable()
        try:
            collector.check_outcome()
            if not collector.is_done():
                for _ in self:
                    collector.check_outcome()
                    if collector.is_done():
                        break
            return collector.result()
        except AgentTurnResultError:
            raise
        except Exception as error:
            collector.cause = error
            raise collector.error("observation_failed") from error
        finally:
            self.close()


class AsyncAgentSessionEventStream(AsyncStream[AgentSessionEvent]):
    """Beta: asynchronous counterpart of AgentSessionEventStream."""

    @cached_property
    def _collection(self) -> AgentTurnResultCollection:
        return AgentTurnResultCollection()

    @override
    async def __stream__(self) -> AsyncIterator[AgentSessionEvent]:
        try:
            async for event in super().__stream__():
                self._collection.accept(event)
                yield event
        except Exception as error:
            self._collection.record_error(error)
            raise

    def with_result_collection(self) -> Self:
        """Beta: retain final messages for a result; call before consuming events."""
        self._collection.enable()
        return self

    async def get_final_result(self) -> AgentTurnResult:
        """Consume remaining events and return the successful initial turn result.

        Enables collection on a fresh stream. To iterate first, call
        with_result_collection() before consuming events.
        """
        collector = self._collection.enable()
        try:
            collector.check_outcome()
            if not collector.is_done():
                async for _ in self:
                    collector.check_outcome()
                    if collector.is_done():
                        break
            return collector.result()
        except AgentTurnResultError:
            raise
        except Exception as error:
            collector.cause = error
            raise collector.error("observation_failed") from error
        finally:
            await self.close()
