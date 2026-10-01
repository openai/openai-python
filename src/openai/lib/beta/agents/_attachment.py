from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Iterable, Iterator, AsyncIterator

from ._result import AgentTurnResultCollector
from ...._streaming import Stream, AsyncStream
from ....types.beta.agent_session import AgentSession
from ....types.beta.agent_session_event import AgentSessionEvent
from ....types.beta.agents.sessions.turn import Turn
from ....types.beta.agent_session_message import AgentSessionMessage

if TYPE_CHECKING:
    from ...streaming.agents._streams import _RequestOptions
    from ....resources.beta.agents.sessions.sessions import Sessions, AsyncSessions

_TERMINAL = ("completed", "failed", "cancelled")


class AgentSessionAttachment:
    """Turn identity and bounded observation state for a single attachment."""

    def __init__(self, session_id: str, turn: Turn | None = None) -> None:
        self.session_id = session_id
        self.turn = turn
        self.settled = False
        self.failed = False
        self.reconciled = False
        self.last_candidate: str | None = None
        self.observation_interrupted = False

    def select(self, turn: Turn) -> None:
        if self.turn is None and turn.session_id == self.session_id and turn.subagent_id is None:
            self.turn = deepcopy(turn)

    def settle(self, session: AgentSession) -> None:
        terminal = self.turn is not None and self.turn.status in _TERMINAL
        # Session status can already describe a successor turn. Exact selected
        # turn state is authoritative for this attachment's completion boundary.
        self.failed = session.status == "failed" and not terminal
        self.settled = terminal or self.failed or session.status == "idle" and self.turn is None

    def seed(self, collector: AgentTurnResultCollector) -> None:
        if collector.turn is None and self.turn is not None:
            collector.turn = deepcopy(self.turn)
        if self.settled:
            collector.boundary = True
        if self.failed:
            collector.session_failed = True

    def candidate(self, event: AgentSessionEvent) -> str | None:
        if self.turn is not None:
            return None
        if (
            event.type == "agent.session.turn.created"
            or event.type == "agent.session.turn.completed"
            or event.type == "agent.session.turn.failed"
            or event.type == "agent.session.turn.cancelled"
        ):
            self.select(event.turn)
            return None
        turn_id = getattr(event, "turn_id", None)
        if isinstance(turn_id, str) and turn_id != self.last_candidate:
            self.last_candidate = turn_id
            return turn_id
        return None


def _latest_root(turns: Iterable[Turn]) -> Turn | None:
    for turn in turns:
        if turn.subagent_id is None:
            return turn
    return None


def attach(
    sessions: Sessions, session_id: str, options: _RequestOptions
) -> tuple[Stream[AgentSessionEvent], AgentSessionAttachment]:
    baseline = _latest_root(sessions.turns.list(session_id, order="desc", **options))
    turn = baseline if baseline is not None and baseline.status not in _TERMINAL else None
    state = AgentSessionAttachment(session_id, turn)
    stream = sessions.events.stream(session_id, **options)
    try:
        # Subscribe before refreshing state so completion during attachment cannot
        # leave us waiting for a terminal event that predates the subscription.
        session = sessions.retrieve(session_id, **options)
        if state.turn is not None:
            state.turn = sessions.turns.retrieve(state.turn.id, session_id=session_id, **options)
        else:
            latest = _latest_root(sessions.turns.list(session_id, order="desc", **options))
            _select_refreshed(state, latest, baseline)
        state.settle(session)
        return stream, state
    except BaseException:
        stream.close()
        raise


async def async_attach(
    sessions: AsyncSessions, session_id: str, options: _RequestOptions
) -> tuple[AsyncStream[AgentSessionEvent], AgentSessionAttachment]:
    async def latest_root() -> Turn | None:
        async for turn in sessions.turns.list(session_id, order="desc", **options):
            if turn.subagent_id is None:
                return turn
        return None

    baseline = await latest_root()
    turn = baseline if baseline is not None and baseline.status not in _TERMINAL else None
    state = AgentSessionAttachment(session_id, turn)
    stream = await sessions.events.stream(session_id, **options)
    try:
        session = await sessions.retrieve(session_id, **options)
        if state.turn is not None:
            state.turn = await sessions.turns.retrieve(state.turn.id, session_id=session_id, **options)
        else:
            _select_refreshed(state, await latest_root(), baseline)
        state.settle(session)
        return stream, state
    except BaseException:
        await stream.close()
        raise


def _select_refreshed(state: AgentSessionAttachment, latest: Turn | None, baseline: Turn | None) -> None:
    # A newly visible root can have finished during subscription. An unchanged
    # completed root is historical and does not identify the observed work.
    if latest is not None and (latest.status not in _TERMINAL or baseline is None or latest.id != baseline.id):
        state.select(latest)


def reconcile(
    sessions: Sessions, state: AgentSessionAttachment, collector: AgentTurnResultCollector, options: _RequestOptions
) -> bool:
    if state.reconciled:
        return True
    if collector.turn is None:
        return False
    turn = sessions.turns.retrieve(collector.turn.id, session_id=state.session_id, **options)
    collector.turn = turn
    if turn.status not in _TERMINAL:
        return False
    messages = [
        item
        for item in sessions.items.list(state.session_id, order="asc", **options)
        if item.type == "message"
        and item.turn_id == turn.id
        and item.role == "assistant"
        and item.status == "completed"
        and item.phase != "commentary"
    ]
    _reconcile(state, collector, turn, messages)
    return True


async def async_reconcile(
    sessions: AsyncSessions,
    state: AgentSessionAttachment,
    collector: AgentTurnResultCollector,
    options: _RequestOptions,
) -> bool:
    if state.reconciled:
        return True
    if collector.turn is None:
        return False
    turn = await sessions.turns.retrieve(collector.turn.id, session_id=state.session_id, **options)
    collector.turn = turn
    if turn.status not in _TERMINAL:
        return False
    messages = [
        item
        async for item in sessions.items.list(state.session_id, order="asc", **options)
        if item.type == "message"
        and item.turn_id == turn.id
        and item.role == "assistant"
        and item.status == "completed"
        and item.phase != "commentary"
    ]
    _reconcile(state, collector, turn, messages)
    return True


def _reconcile(
    state: AgentSessionAttachment, collector: AgentTurnResultCollector, turn: Turn, messages: list[AgentSessionMessage]
) -> None:
    collector.turn = turn
    collector.cause = None
    collector.required_actions = []
    collector.boundary = True
    collector.replace_messages(messages)
    state.reconciled = True


def observe(stream: Stream[AgentSessionEvent], state: AgentSessionAttachment) -> Iterator[AgentSessionEvent]:
    iterator = iter(stream)
    while True:
        try:
            event = next(iterator)
        except StopIteration:
            state.observation_interrupted = True
            return
        except Exception:
            state.observation_interrupted = True
            raise
        yield event


async def async_observe(
    stream: AsyncStream[AgentSessionEvent], state: AgentSessionAttachment
) -> AsyncIterator[AgentSessionEvent]:
    iterator = stream.__aiter__()
    while True:
        try:
            event = await iterator.__anext__()
        except StopAsyncIteration:
            state.observation_interrupted = True
            return
        except Exception:
            state.observation_interrupted = True
            raise
        yield event
