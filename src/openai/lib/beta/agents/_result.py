from __future__ import annotations

from copy import deepcopy
from typing import Any, Generic, Iterable
from dataclasses import dataclass
from typing_extensions import Literal, TypeVar

from ._output import validate_output_type
from ...._exceptions import OpenAIError
from ..._parsing._completions import _parse_content
from ....types.beta.agent_session import RequiredAction
from ....types.beta.agent_session_event import AgentSessionEvent
from ....types.beta.agents.sessions.turn import Turn
from ....types.beta.agent_session_message import AgentSessionMessage

OutputT = TypeVar("OutputT", default=Any)
ParseT = TypeVar("ParseT")


@dataclass(frozen=True)
class AgentTurnResult(Generic[OutputT]):
    """Beta: the completed final assistant messages from one successful root turn."""

    turn: Turn
    messages: list[AgentSessionMessage]
    output_parsed: OutputT | None = None

    def parse(self, output_type: type[ParseT]) -> AgentTurnResult[ParseT]:
        """Beta: parse a completed answer without changing its session configuration."""
        try:
            validate_output_type(output_type)
            parsed: ParseT | None = None
            found = False
            for message in self.messages:
                for content in message.content:
                    if content.type != "output_text":
                        continue
                    value = _parse_content(output_type, content.text)
                    if not found:
                        parsed = value
                        found = True
            if not found:
                raise ValueError("No final output text to parse")
        except Exception:
            # Pydantic errors may include response text in their rendered message.
            raise AgentOutputParseError(self) from None
        return AgentTurnResult(turn=self.turn, messages=self.messages, output_parsed=parsed)

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


class AgentOutputParseError(OpenAIError):
    """Beta: output parsing failed after a successful hosted turn."""

    def __init__(self, result: AgentTurnResult) -> None:
        super().__init__("Could not parse the completed agent output")
        self.result = result


ResultErrorReason = Literal["failed", "cancelled", "requires_action", "incomplete", "observation_failed"]


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
                self.required_actions = []
        elif event.type == "agent.session.turn.item.done":
            # Completed items are authoritative on these ordered, uninterrupted streams.
            item = event.item
            if (
                self.turn is not None
                and item.turn_id == self.turn.id
                and item.type == "message"
                and item.phase != "commentary"
                and item.status == "completed"
            ):
                message = AgentSessionMessage.construct(_fields_set=None, **deepcopy(item.to_dict()))
                self._messages[item.id] = (event.output_index, message)
        elif event.type == "agent.session.in_progress":
            self.required_actions = []
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
        return [message for _, message in sorted(self._messages.values(), key=lambda pair: pair[0])]

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
        if not self.boundary or self.turn is None or self.turn.status != "completed":
            raise self.error("incomplete")
        self._result = AgentTurnResult(turn=deepcopy(self.turn), messages=self.messages())
        self._messages.clear()
        return self._result


class AgentTurnResultCollection(Generic[OutputT]):
    """Keep ordinary event iteration incremental until collection is requested."""

    def __init__(self, session_id: str | None = None, output_type: type[OutputT] | None = None) -> None:
        if output_type is not None:
            validate_output_type(output_type)
        self.output_type = output_type
        self._parsed_result: AgentTurnResult[OutputT] | None = None
        self.collector: AgentTurnResultCollector | None = None
        self._session_id = session_id
        self._started = False

    def enable(self) -> AgentTurnResultCollector:
        if self.collector is None:
            if self._started:
                raise RuntimeError(
                    "Call with_result_collection() before consuming events, or call get_final_result() on a fresh stream"
                )
            self.collector = AgentTurnResultCollector(self._session_id)
        return self.collector

    def accept(self, event: AgentSessionEvent) -> None:
        self._started = True
        if self.collector is not None:
            self.collector.accept(event)

    def record_error(self, error: Exception) -> None:
        if self.collector is not None and not self.collector.is_done():
            self.collector.cause = error

    def result(self) -> AgentTurnResult[OutputT]:
        result = self.enable().result()
        if self.output_type is None:
            return result
        if self._parsed_result is None:
            self._parsed_result = result.parse(self.output_type)
        return self._parsed_result
