from __future__ import annotations

from copy import deepcopy
from typing import Iterable
from dataclasses import dataclass
from typing_extensions import Literal

from ...._exceptions import OpenAIError
from ....types.beta.agent_session import RequiredAction
from ....types.beta.agent_session_event import AgentSessionEvent
from ....types.beta.agents.sessions.turn import Turn
from ....types.beta.agent_session_message import AgentSessionMessage


@dataclass(frozen=True)
class AgentTurnResult:
    """Beta: the completed final assistant messages from one successful root turn."""

    turn: Turn
    messages: list[AgentSessionMessage]

    @property
    def session_id(self) -> str:
        return self.turn.session_id

    @property
    def turn_id(self) -> str:
        return self.turn.id

    @property
    def output_text(self) -> str:
        """Join final output text without adding separators or performing I/O."""
        return "".join(message.output_text for message in self.messages)


ResultErrorReason = Literal[
    "failed", "cancelled", "requires_action", "incomplete", "ambiguous_output", "observation_failed"
]


class AgentTurnResultError(OpenAIError):
    """Beta: collection did not establish a successful, complete turn result.

    ``turn`` and ``messages`` preserve available partial state. An observation
    error does not mean the hosted turn failed. Transport errors are chained.
    """

    def __init__(
        self,
        reason: ResultErrorReason,
        *,
        turn: Turn | None,
        session_id: str | None,
        messages: list[AgentSessionMessage],
        required_actions: list[RequiredAction],
    ) -> None:
        super().__init__(f"Could not collect the agent turn result: {reason}")
        self.reason = reason
        self.turn = turn
        self.session_id = session_id
        self.turn_id = turn.id if turn is not None else None
        self.messages = messages
        self.required_actions = required_actions


class AgentTurnResultCollector:
    def __init__(self, session_id: str | None = None) -> None:
        self.session_id = session_id
        self.turn: Turn | None = None
        self.boundary = False
        self.session_failed = False
        self.cause: Exception | None = None
        self.required_actions: list[RequiredAction] = []
        self._messages: dict[str, tuple[int, AgentSessionMessage]] = {}
        self._pending: set[str] = set()
        self._unclassified: set[str] = set()
        self._excluded: set[str] = set()
        self._unidentified_message = False
        self._error: AgentTurnResultError | None = None
        self._result: AgentTurnResult | None = None

    def accept(self, event: AgentSessionEvent) -> None:
        if self.boundary:
            return
        if event.type == "agent.session.created":
            self.session_id = event.session.id
        elif event.type == "agent.session.turn.created":
            if self.turn is None and event.turn.subagent_id is None:
                self.turn = deepcopy(event.turn)
                self.session_id = event.session_id
        elif (
            event.type == "agent.session.turn.completed"
            or event.type == "agent.session.turn.failed"
            or event.type == "agent.session.turn.cancelled"
        ):
            if self.turn is not None and event.turn_id == self.turn.id:
                self.turn = deepcopy(event.turn)
        elif (
            event.type == "agent.session.turn.output_text.delta" or event.type == "agent.session.turn.output_text.done"
        ):
            if self.turn is not None and (event.turn_id is None or event.turn_id == self.turn.id):
                if event.item_id not in self._messages and event.item_id not in self._excluded:
                    self._pending.add(event.item_id)
        elif event.type == "agent.session.turn.item.added" or event.type == "agent.session.turn.item.done":
            item = event.item
            if self.turn is None or item.type != "message" or item.role != "assistant":
                return
            if item.id is None:
                if item.turn_id == self.turn.id and item.phase != "commentary":
                    self._unidentified_message = True
                return
            if event.type == "agent.session.turn.item.added" and item.id in self._messages:
                return
            if item.turn_id != self.turn.id or item.phase == "commentary":
                self._excluded.add(item.id)
                self._pending.discard(item.id)
                self._unclassified.discard(item.id)
                self._messages.pop(item.id, None)
                return
            self._excluded.discard(item.id)
            if item.phase is None:
                self._unclassified.add(item.id)
            else:
                self._unclassified.discard(item.id)
            if event.type == "agent.session.turn.item.done" and item.status == "completed":
                message = AgentSessionMessage.construct(_fields_set=None, **deepcopy(item.to_dict()))
                self._messages[item.id] = (event.output_index, message)
                self._pending.discard(item.id)
            elif item.id not in self._messages:
                self._pending.add(item.id)
        elif event.type == "agent.session.requires_action":
            self.session_id = event.session.id
            self.required_actions = deepcopy(event.session.required_actions)
        elif event.type == "agent.session.failed":
            self.session_id = event.session.id
            self.session_failed = True
            self.boundary = True
        elif event.type == "agent.session.idle":
            if self.turn is not None and self.turn.status in ("completed", "failed", "cancelled"):
                self.required_actions = []
                self.boundary = True

    def is_done(self) -> bool:
        return self.boundary

    def messages(self) -> list[AgentSessionMessage]:
        return [
            message
            for _, message in sorted(self._messages.values(), key=lambda pair: pair[0])
            if message.phase == "final_answer"
        ]

    def error(self, reason: ResultErrorReason) -> AgentTurnResultError:
        if self._error is None:
            self._error = AgentTurnResultError(
                reason,
                turn=self.turn,
                session_id=self.session_id,
                messages=self.messages(),
                required_actions=self.required_actions,
            )
            self.turn = None
            self.required_actions = []
            self._messages.clear()
            self._pending.clear()
            self._unclassified.clear()
            self._excluded.clear()
            self.boundary = True
        return self._error

    def check_outcome(self, handled_tools: Iterable[str] = ()) -> None:
        if self._error is not None:
            raise self._error
        if self.session_failed or self.turn is not None and self.turn.status == "failed":
            raise self.error("failed")
        if self.turn is not None and self.turn.status == "cancelled":
            raise self.error("cancelled")
        if any(action.type != "function_call" or action.name not in handled_tools for action in self.required_actions):
            raise self.error("requires_action")
        if self.cause is not None:
            raise self.error("observation_failed") from self.cause

    def result(self) -> AgentTurnResult:
        if self._result is not None:
            return self._result
        self.check_outcome()
        if (
            not self.boundary
            or self.turn is None
            or self.turn.status != "completed"
            or self._pending
            or self._unidentified_message
        ):
            raise self.error("incomplete")
        if self._unclassified:
            raise self.error("ambiguous_output")
        self._result = AgentTurnResult(turn=deepcopy(self.turn), messages=self.messages())
        self._messages.clear()
        self._excluded.clear()
        return self._result
