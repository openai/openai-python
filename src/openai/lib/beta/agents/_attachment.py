from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Iterable

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
    session = sessions.retrieve(session_id, **options)
    observed_active = session.status not in ("idle", "failed")
    baseline = _latest_root(sessions.turns.list(session_id, order="desc", **options)) if observed_active else None
    turn = baseline if baseline is not None and baseline.status not in _TERMINAL else None
    state = AgentSessionAttachment(session_id, turn)
    stream = sessions.events.stream(session_id, **options)
    try:
        # Subscribe before refreshing state so completion during attachment cannot
        # leave us waiting for a terminal event that predates the subscription.
        session = sessions.retrieve(session_id, **options)
        if state.turn is not None:
            state.turn = sessions.turns.retrieve(state.turn.id, session_id=session_id, **options)
        elif observed_active or session.status not in ("idle", "failed"):
            latest = _latest_root(sessions.turns.list(session_id, order="desc", **options))
            _select_refreshed(state, latest, baseline, observed_active)
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

    session = await sessions.retrieve(session_id, **options)
    observed_active = session.status not in ("idle", "failed")
    baseline = await latest_root() if observed_active else None
    turn = baseline if baseline is not None and baseline.status not in _TERMINAL else None
    state = AgentSessionAttachment(session_id, turn)
    stream = await sessions.events.stream(session_id, **options)
    try:
        session = await sessions.retrieve(session_id, **options)
        if state.turn is not None:
            state.turn = await sessions.turns.retrieve(state.turn.id, session_id=session_id, **options)
        elif observed_active or session.status not in ("idle", "failed"):
            _select_refreshed(state, await latest_root(), baseline, observed_active)
        state.settle(session)
        return stream, state
    except BaseException:
        await stream.close()
        raise


def _select_refreshed(
    state: AgentSessionAttachment, latest: Turn | None, baseline: Turn | None, observed_active: bool
) -> None:
    # A newly visible root can have finished during subscription. An unchanged
    # completed root is historical and does not identify the observed work.
    if latest is not None and (
        latest.status not in _TERMINAL or observed_active and (baseline is None or latest.id != baseline.id)
    ):
        state.select(latest)


def reconcile(
    sessions: Sessions, state: AgentSessionAttachment, collector: AgentTurnResultCollector, options: _RequestOptions
) -> None:
    if state.reconciled or collector.turn is None or collector.turn.status != "completed":
        return
    turn = sessions.turns.retrieve(collector.turn.id, session_id=state.session_id, **options)
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


async def async_reconcile(
    sessions: AsyncSessions,
    state: AgentSessionAttachment,
    collector: AgentTurnResultCollector,
    options: _RequestOptions,
) -> None:
    if state.reconciled or collector.turn is None or collector.turn.status != "completed":
        return
    turn = await sessions.turns.retrieve(collector.turn.id, session_id=state.session_id, **options)
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


def _reconcile(
    state: AgentSessionAttachment, collector: AgentTurnResultCollector, turn: Turn, messages: list[AgentSessionMessage]
) -> None:
    collector.turn = turn
    collector.replace_messages(messages)
    state.reconciled = True
