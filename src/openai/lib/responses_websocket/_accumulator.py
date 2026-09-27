from __future__ import annotations

from typing import cast
from dataclasses import field, dataclass

from ._session import ResponsesWebSocketError, _field
from ..._compat import model_copy
from ...types.responses import Response
from ...types.responses.responses_server_event import ResponsesServerEvent


@dataclass(frozen=True)
class ResponsesWebSocketOutput:
    """Selected fields of one output item. Text pairs contain (content_index, text)."""

    output_index: int
    item_id: str | None
    type: str | None
    name: str | None
    call_id: str | None
    arguments: str
    input: str
    text: tuple[tuple[int, str], ...]


@dataclass(frozen=True)
class ResponsesWebSocketSnapshot:
    """Immutable partial projection; terminal_type is None until a valid terminal arrives."""

    stream_id: str | None
    response_id: str | None
    terminal_type: str | None
    output: tuple[ResponsesWebSocketOutput, ...]

    @property
    def output_text(self) -> str:
        return "".join(text for item in self.output for _, text in item.text)


@dataclass
class _Output:
    item_id: str | None
    type: str | None = None
    name: str | None = None
    call_id: str | None = None
    arguments: list[str] = field(default_factory=list[str])
    input: list[str] = field(default_factory=list[str])
    text: dict[int, list[str]] = field(default_factory=dict[int, list[str]])


class ResponsesWebSocketAccumulator:
    """Opt-in, caller-fed collection of text, function arguments and custom tool input.

    Feed typed events from a connection or lane's recv(). Use one accumulator per
    lane and call reset() before another turn. The helper never reads, sends,
    closes the connection, or executes tools. It is not safe for concurrent use.
    Snapshot fields are projections; get_final_response() retains the exact
    server response, including failed/incomplete and missing/null/empty output.
    """

    def __init__(self) -> None:
        self._stream_id: str | None = None
        self._response_id: str | None = None
        self._terminal_type: str | None = None
        self._bound = False
        self._output: dict[int, _Output] = {}
        self._final: Response | None = None
        self._error: Exception | None = None

    def reset(self) -> None:
        """Release this helper's state only; prior snapshots and the socket remain usable."""
        self._stream_id = self._response_id = self._terminal_type = None
        self._bound = False
        self._output.clear()
        self._final = self._error = None

    def snapshot(self) -> ResponsesWebSocketSnapshot:
        """Materialize the entire current immutable projection.

        This joins retained fragments. Use original events for per-delta progress
        and request snapshots intentionally (for example, on output_item.done).
        """
        return ResponsesWebSocketSnapshot(
            stream_id=self._stream_id,
            response_id=self._response_id,
            terminal_type=self._terminal_type,
            output=tuple(
                ResponsesWebSocketOutput(
                    output_index=index,
                    item_id=item.item_id,
                    type=item.type,
                    name=item.name,
                    call_id=item.call_id,
                    arguments="".join(item.arguments),
                    input="".join(item.input),
                    text=tuple((pos, "".join(parts)) for pos, parts in sorted(item.text.items())),
                )
                for index, item in sorted(self._output.items())
            ),
        )

    def get_final_response(self) -> Response:
        """Return an independent copy of the received terminal response, never a partial success."""
        error = self._error
        if error is not None:
            raise error
        if self._final is None:
            raise RuntimeError("No terminal response has been received")
        return model_copy(self._final, deep=True)

    def add_event(self, event: ResponsesServerEvent) -> None:
        """Observe an event without consuming or changing it; unknown events are ignored.

        Final fields replace deltas. A supplied output list, even [], replaces
        the projection; null or omitted output retains prior projected fields.
        Original event fields remain accessible to the caller.
        """
        kind = _field(event, "type")
        if kind not in {
            "response.created",
            "response.in_progress",
            "response.completed",
            "response.failed",
            "response.incomplete",
            "response.output_item.added",
            "response.output_item.done",
            "response.content_part.added",
            "response.content_part.done",
            "response.output_text.delta",
            "response.output_text.done",
            "response.function_call_arguments.delta",
            "response.function_call_arguments.done",
            "response.custom_tool_call_input.delta",
            "response.custom_tool_call_input.done",
            "error",
        }:
            return
        stream_id = _field(event, "stream_id")
        if self._bound and self._stream_id != stream_id:
            raise ValueError("Event belongs to another WebSocket lane")
        if self._terminal_type is not None or self._error is not None:
            raise RuntimeError("Reset the accumulator before adding another turn")
        if kind == "error":
            protocol_error = ResponsesWebSocketError(event)
            self._error = protocol_error
            raise protocol_error
        terminal = kind in {"response.completed", "response.failed", "response.incomplete"}
        if kind in {"response.created", "response.in_progress"} or terminal:
            response = _field(event, "response")
            if not isinstance(response, Response):
                error = ValueError("WebSocket event is missing a valid response")
                if terminal:
                    self._error = error
                raise error
            response_id = _field(response, "id")
            if self._response_id is not None and response_id is not None and self._response_id != response_id:
                raise ValueError("Event belongs to another response")
            self._response_id = response_id or self._response_id
            self._bound, self._stream_id = True, stream_id
            output = _field(response, "output")
            if isinstance(output, list):
                self._output.clear()
                for index, item in enumerate(cast("list[object]", output)):
                    self._add_item(index, item)
            if terminal:
                self._final = model_copy(response, deep=True)
                self._terminal_type = kind
            return
        index = _field(event, "output_index")
        if not isinstance(index, int):
            raise ValueError("WebSocket output event is missing output_index")
        if kind in {"response.output_item.added", "response.output_item.done"}:
            self._add_item(index, _field(event, "item"))
            self._bound, self._stream_id = True, stream_id
            return
        # Validate consumed values before replacing an item's retained state.
        # The wire decoder preserves known events even when fields are malformed.
        value = ""
        if kind in {
            "response.output_text.delta",
            "response.function_call_arguments.delta",
            "response.custom_tool_call_input.delta",
        }:
            value = _text_field(event, "delta")
        elif kind == "response.output_text.done":
            value = _text_field(event, "text")
        elif kind == "response.function_call_arguments.done":
            value = _text_field(event, "arguments")
        elif kind == "response.custom_tool_call_input.done":
            value = _text_field(event, "input")
        elif kind in {"response.content_part.added", "response.content_part.done"}:
            part = _field(event, "part")
            if _field(part, "type") == "output_text":
                value = _text_field(part, "text")
        pos = _field(event, "content_index")
        if kind in {
            "response.content_part.added",
            "response.content_part.done",
            "response.output_text.delta",
            "response.output_text.done",
        } and not isinstance(pos, int):
            raise ValueError("WebSocket text event is missing content_index")
        self._bound, self._stream_id = True, stream_id
        item_id = _field(event, "item_id")
        item = self._output.get(index)
        if item is None or (item_id and item.item_id and item_id != item.item_id):
            item = _Output(item_id=item_id)
            self._output[index] = item
        if item_id:
            item.item_id = item_id
        if kind in {
            "response.content_part.added",
            "response.content_part.done",
            "response.output_text.delta",
            "response.output_text.done",
        }:
            if kind == "response.output_text.delta":
                item.text.setdefault(pos, []).append(value)
            elif kind == "response.output_text.done":
                item.text[pos] = [value]
            else:
                part = _field(event, "part")
                if _field(part, "type") == "output_text":
                    item.text[pos] = [value]
        elif kind == "response.function_call_arguments.delta":
            item.arguments.append(value)
        elif kind == "response.function_call_arguments.done":
            item.arguments = [value]
        elif kind == "response.custom_tool_call_input.delta":
            item.input.append(value)
        elif kind == "response.custom_tool_call_input.done":
            item.input = [value]

    def _add_item(self, index: int, source: object) -> None:
        if source is None:
            return
        item = _Output(
            item_id=_field(source, "id"),
            type=_field(source, "type"),
            name=_field(source, "name"),
            call_id=_field(source, "call_id"),
        )
        if item.type == "message":
            for pos, part in enumerate(_field(source, "content") or []):
                if _field(part, "type") == "output_text" and _field(part, "text") is not None:
                    item.text[pos] = [_text_field(part, "text")]
        elif item.type == "function_call":
            value = _field(source, "arguments")
            item.arguments = ["" if value is None else _text_field(source, "arguments")]
        elif item.type == "custom_tool_call":
            value = _field(source, "input")
            item.input = ["" if value is None else _text_field(source, "input")]
        self._output[index] = item


def _text_field(value: object, name: str) -> str:
    text = _field(value, name)
    if not isinstance(text, str):
        raise ValueError(f"WebSocket output {name} must be a string")
    return text
