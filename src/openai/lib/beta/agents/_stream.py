from __future__ import annotations

from typing import Iterator, AsyncIterator
from typing_extensions import override

from ._result import AgentTurnResult, AgentTurnResultError, AgentTurnResultCollector
from ...._compat import cached_property
from ...._streaming import Stream, AsyncStream
from ....types.beta.agent_session_event import AgentSessionEvent


class AgentSessionEventStream(Stream[AgentSessionEvent]):
    """Beta: a creation event stream that can collect its initial turn's result.

    Event iteration and response access behave like ``Stream``. Collection does
    not execute local tools; required actions are available on the result error.
    """

    @cached_property
    def _collector(self) -> AgentTurnResultCollector:
        return AgentTurnResultCollector()

    @override
    def __stream__(self) -> Iterator[AgentSessionEvent]:
        try:
            for event in super().__stream__():
                self._collector.accept(event)
                yield event
        except Exception as error:
            if not self._collector.is_done():
                self._collector.cause = error
            raise

    def get_final_result(self) -> AgentTurnResult:
        """Consume remaining events and return the successful initial turn result.

        Raises AgentTurnResultError for an unsuccessful or unobserved outcome.
        Repeated calls return the cached result without consuming more events.
        """
        try:
            self._collector.check_outcome()
            if not self._collector.is_done():
                for _ in self:
                    self._collector.check_outcome()
                    if self._collector.is_done():
                        break
            return self._collector.result()
        except AgentTurnResultError:
            raise
        except Exception as error:
            self._collector.cause = error
            raise self._collector.error("observation_failed") from error
        finally:
            self.close()


class AsyncAgentSessionEventStream(AsyncStream[AgentSessionEvent]):
    """Beta: asynchronous counterpart of AgentSessionEventStream."""

    @cached_property
    def _collector(self) -> AgentTurnResultCollector:
        return AgentTurnResultCollector()

    @override
    async def __stream__(self) -> AsyncIterator[AgentSessionEvent]:
        try:
            async for event in super().__stream__():
                self._collector.accept(event)
                yield event
        except Exception as error:
            if not self._collector.is_done():
                self._collector.cause = error
            raise

    async def get_final_result(self) -> AgentTurnResult:
        """Consume remaining events and return the successful initial turn result."""
        try:
            self._collector.check_outcome()
            if not self._collector.is_done():
                async for _ in self:
                    self._collector.check_outcome()
                    if self._collector.is_done():
                        break
            return self._collector.result()
        except AgentTurnResultError:
            raise
        except Exception as error:
            self._collector.cause = error
            raise self._collector.error("observation_failed") from error
        finally:
            await self.close()
