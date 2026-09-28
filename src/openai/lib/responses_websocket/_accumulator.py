from __future__ import annotations

from copy import deepcopy
from typing import Any, cast
from dataclasses import field, dataclass

from ._session import ResponsesWebSocketError, _field
from ..._compat import PYDANTIC_V1, model_copy
from ..._models import BaseModel
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
    retired_ids: set[str] = field(default_factory=set[str])
    type: str | None = None
    name: str | None = None
    call_id: str | None = None
    arguments: list[str] = field(default_factory=list[str])
    input: list[str] = field(default_factory=list[str])
    text: dict[str, list[str]] = field(default_factory=dict[str, list[str]])
    data: dict[str, object] = field(default_factory=dict[str, object])
    content: dict[str, dict[str, object]] = field(default_factory=dict[str, dict[str, object]])
    annotations: dict[str, dict[str, object]] = field(default_factory=dict[str, dict[str, object]])


class ResponsesWebSocketAccumulator:
    """Opt-in, caller-fed collection of text, function/MCP arguments and custom tool input.

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
        # String keys get Python's randomized hash. Hex preserves arbitrary-size
        # non-negative indices without decimal string conversion limits.
        self._output: dict[str, _Output] = {}
        self._response: dict[str, object] | None = None
        self._final: Response | None = None
        self._error: Exception | None = None

    def reset(self) -> None:
        """Release this helper's state only; prior snapshots and the socket remain usable."""
        self._stream_id = self._response_id = self._terminal_type = None
        self._bound = False
        self._output.clear()
        self._response = None
        self._final = self._error = None

    def snapshot(self) -> ResponsesWebSocketSnapshot:
        """Materialize the entire current immutable projection.

        This joins retained fragments. Use original events for delta and item
        progress; read a full snapshot at a terminal or on explicit user demand.
        """
        return ResponsesWebSocketSnapshot(
            stream_id=self._stream_id,
            response_id=self._response_id,
            terminal_type=self._terminal_type,
            output=tuple(
                ResponsesWebSocketOutput(
                    output_index=int(index, 16),
                    item_id=item.item_id,
                    type=item.type,
                    name=item.name,
                    call_id=item.call_id,
                    arguments="".join(item.arguments),
                    input="".join(item.input),
                    text=tuple(
                        (int(pos, 16), "".join(parts))
                        for pos, parts in sorted(item.text.items(), key=lambda pair: int(pair[0], 16))
                    ),
                )
                for index, item in sorted(self._output.items(), key=lambda pair: int(pair[0], 16))
            ),
        )

    def detailed_snapshot(self) -> dict[str, Any]:
        """Return an independent mutable projection of observed response, item and part data.

        Output and content are lists of indexed rows, even when wire indices are
        sparse. Part annotations use the same indexed-row form. Unset and null
        fields stay distinct; missing scaffolding never invents a Response or
        an item/part type. Cost is proportional to the full accumulated data.
        """
        output: list[dict[str, object]] = []
        for index, item in sorted(self._output.items(), key=lambda pair: int(pair[0], 16)):
            data = deepcopy(item.data)
            if item.item_id:
                data["id"] = item.item_id
            if item.arguments:
                data["arguments"] = "".join(item.arguments)
            if item.input:
                data["input"] = "".join(item.input)
            content: list[dict[str, object]] = []
            for pos in sorted(
                item.content.keys() | item.text.keys() | item.annotations.keys(), key=lambda k: int(k, 16)
            ):
                part = deepcopy(item.content.get(pos, {}))
                if pos in item.text:
                    part["text"] = "".join(item.text[pos])
                original = part.get("annotations")
                if isinstance(original, list) or pos in item.annotations:
                    annotations = (
                        {hex(i): value for i, value in enumerate(cast("list[object]", original))}
                        if isinstance(original, list)
                        else {}
                    )
                    annotations.update(deepcopy(item.annotations.get(pos, {})))
                    part["annotations"] = [
                        {"annotation_index": int(i, 16), "annotation": annotation}
                        for i, annotation in sorted(annotations.items(), key=lambda pair: int(pair[0], 16))
                    ]
                content.append({"content_index": int(pos, 16), "part": part})
            row: dict[str, object] = {"output_index": int(index, 16), "item": data}
            if item.type == "message":
                # Message content is extracted into indexed rows. Retain the
                # presence marker until a part/delta supplies projected content.
                if "content" in data or content:
                    original_content = data.pop("content", None)
                    row["content"] = content if content or isinstance(original_content, list) else None
            else:
                row["content"] = content
            output.append(row)
        return {
            "stream_id": self._stream_id,
            "response_id": self._response_id,
            "terminal_type": self._terminal_type,
            "response": deepcopy(self._response),
            "output": output,
        }

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
        if not isinstance(kind, str) or kind not in {
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
            "response.output_text.annotation.added",
            "response.function_call_arguments.delta",
            "response.function_call_arguments.done",
            "response.mcp_call_arguments.delta",
            "response.mcp_call_arguments.done",
            "response.custom_tool_call_input.delta",
            "response.custom_tool_call_input.done",
            "error",
        }:
            return
        stream_id = _field(event, "stream_id")
        # Annotations were historically ignored. They may enrich the matching
        # known item, but never bind a lane/turn, replace or retire an item, or
        # change the errors observed by existing accumulator callers.
        if kind == "response.output_text.annotation.added":
            output_pos = _field(event, "output_index")
            content_pos = _field(event, "content_index")
            annotation_pos = _field(event, "annotation_index")
            if (
                self._bound
                and self._stream_id == stream_id
                and self._terminal_type is None
                and self._error is None
                and all(
                    isinstance(value, int) and not isinstance(value, bool) and value >= 0
                    for value in (output_pos, content_pos, annotation_pos)
                )
            ):
                existing = self._output.get(hex(output_pos))
                if existing is not None and existing.item_id == _field(event, "item_id"):
                    value_data = _data(event, include={"annotation"})
                    if "annotation" in value_data:
                        existing.annotations.setdefault(hex(content_pos), {})[hex(annotation_pos)] = value_data[
                            "annotation"
                        ]
            return
        if stream_id is not None and not isinstance(stream_id, str):
            raise ValueError("WebSocket stream_id must be a string or null")
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
            if response_id is not None and not isinstance(response_id, str):
                error = ValueError("WebSocket response id must be a string or null")
                if terminal:
                    self._error = error
                raise error
            if self._response_id is not None and response_id is not None and self._response_id != response_id:
                raise ValueError("Event belongs to another response")
            output = _field(response, "output")
            if output is not None and not isinstance(output, list):
                error = ValueError("WebSocket response output must be a list or null")
                if terminal:
                    self._error = error
                raise error
            if isinstance(output, list):
                replacement: dict[str, _Output] = {}
                try:
                    for index, item in enumerate(cast("list[object]", output)):
                        self._add_item(replacement, index, item)
                except ValueError as error:
                    if terminal:
                        self._error = error
                    raise
                self._output = replacement
            self._response = _data(response, exclude={"output"})
            self._response_id = response_id or self._response_id
            self._bound, self._stream_id = True, stream_id
            if terminal:
                self._final = model_copy(response, deep=True)
                self._terminal_type = kind
            return
        index = _field(event, "output_index")
        if not isinstance(index, int) or isinstance(index, bool) or index < 0:
            raise ValueError("WebSocket output_index must be a non-negative integer")
        if kind in {"response.output_item.added", "response.output_item.done"}:
            self._add_item(self._output, index, _field(event, "item"))
            self._bound, self._stream_id = True, stream_id
            return
        # Validate consumed values before replacing an item's retained state.
        # The wire decoder preserves known events even when fields are malformed.
        value = ""
        if kind in {
            "response.output_text.delta",
            "response.function_call_arguments.delta",
            "response.mcp_call_arguments.delta",
            "response.custom_tool_call_input.delta",
        }:
            value = _text_field(event, "delta")
        elif kind == "response.output_text.done":
            value = _text_field(event, "text")
        elif kind in {"response.function_call_arguments.done", "response.mcp_call_arguments.done"}:
            value = _text_field(event, "arguments")
        elif kind == "response.custom_tool_call_input.done":
            value = _text_field(event, "input")
        elif kind in {"response.content_part.added", "response.content_part.done"}:
            part = _field(event, "part")
            if _text_field(part, "type") == "output_text":
                value = _text_field(part, "text")
        pos = _field(event, "content_index")
        if kind in {
            "response.content_part.added",
            "response.content_part.done",
            "response.output_text.delta",
            "response.output_text.done",
        } and (not isinstance(pos, int) or isinstance(pos, bool) or pos < 0):
            raise ValueError("WebSocket content_index must be a non-negative integer")
        item_id = _text_field(event, "item_id")
        self._bound, self._stream_id = True, stream_id
        key = hex(index)
        item = self._output.get(key)
        if item is not None and item_id in item.retired_ids:
            return
        if item is None:
            item = _Output(item_id=item_id)
            self._output[key] = item
        elif item_id and item.item_id and item_id != item.item_id:
            item.retired_ids.add(item.item_id)
            item = _Output(item_id=item_id, retired_ids=item.retired_ids)
            self._output[key] = item
        if item_id:
            item.item_id = item_id
        if kind in {
            "response.content_part.added",
            "response.content_part.done",
            "response.output_text.delta",
            "response.output_text.done",
        }:
            position = hex(pos)
            if kind == "response.output_text.delta":
                item.text.setdefault(position, []).append(value)
                data = item.content.setdefault(position, {})
                prob_data = _data(event, include={"logprobs"})
                previous = data.get("logprobs")
                incoming = prob_data.get("logprobs")
                if isinstance(previous, list) and isinstance(incoming, list):
                    cast("list[object]", previous).extend(cast("list[object]", incoming))
                else:
                    data.update(prob_data)
            elif kind == "response.output_text.done":
                item.text[position] = [value]
                item.content.setdefault(position, {}).update(_data(event, include={"logprobs"}))
            else:
                part = _field(event, "part")
                item.content[position] = _data(part)
                item.annotations.pop(position, None)
                if _field(part, "type") == "output_text":
                    item.text[position] = [value]
                else:
                    item.text.pop(position, None)
        elif kind in {"response.function_call_arguments.delta", "response.mcp_call_arguments.delta"}:
            item.arguments.append(value)
        elif kind in {"response.function_call_arguments.done", "response.mcp_call_arguments.done"}:
            item.arguments = [value]
        elif kind == "response.custom_tool_call_input.delta":
            item.input.append(value)
        elif kind == "response.custom_tool_call_input.done":
            item.input = [value]

    @staticmethod
    def _add_item(output: dict[str, _Output], index: int, source: object) -> None:
        if source is None:
            return
        item = _Output(
            item_id=_optional_text_field(source, "id"),
            type=_text_field(source, "type"),
            name=_optional_text_field(source, "name"),
            call_id=_optional_text_field(source, "call_id"),
            data=_data(source, exclude={"content"} if _field(source, "type") == "message" else None),
        )
        if item.type == "message":
            content = _field(source, "content")
            if content is not None:
                if not isinstance(content, list):
                    raise ValueError("WebSocket message content must be a list or null")
                # Marker only; keep actual parts indexed once, never copied twice.
                item.data["content"] = []
                for pos, part in enumerate(cast("list[object]", content)):
                    if part is not None:
                        item.content[hex(pos)] = _data(part)
                    if part is not None and _text_field(part, "type") == "output_text":
                        text = _optional_text_field(part, "text")
                        if text is not None:
                            item.text[hex(pos)] = [text]
            else:
                item.data.update(_data(source, include={"content"}))
        elif item.type in {"function_call", "mcp_call", "mcp_approval_request"}:
            arguments = _optional_text_field(source, "arguments")
            if arguments is not None:
                item.arguments = [arguments]
        elif item.type == "custom_tool_call":
            input_text = _optional_text_field(source, "input")
            if input_text is not None:
                item.input = [input_text]
        key = hex(index)
        previous = output.get(key)
        if previous is not None:
            if item.item_id and item.item_id in previous.retired_ids:
                return
            item.retired_ids = previous.retired_ids
            if previous.item_id and item.item_id and previous.item_id != item.item_id:
                item.retired_ids.add(previous.item_id)
        output[key] = item


def _data(source: object, *, include: set[str] | None = None, exclude: set[str] | None = None) -> dict[str, object]:
    if isinstance(source, BaseModel):
        return deepcopy(
            source.model_dump(
                mode="python", by_alias=True, exclude_unset=True, include=include, exclude=exclude, warnings=PYDANTIC_V1
            )
        )
    if isinstance(source, dict):
        return deepcopy(
            {
                key: value
                for key, value in cast("dict[str, object]", source).items()
                if (include is None or key in include) and (exclude is None or key not in exclude)
            }
        )
    return {}


def _text_field(value: object, name: str) -> str:
    text = _field(value, name)
    if not isinstance(text, str):
        raise ValueError(f"WebSocket output {name} must be a string")
    return text


def _optional_text_field(value: object, name: str) -> str | None:
    if _field(value, name) is None:
        return None
    return _text_field(value, name)
