from __future__ import annotations

from typing import Any, Generic, TypeVar, Iterator, Optional, AsyncIterator, cast
from typing_extensions import override

from ...._utils import is_mapping
from ...._streaming import Stream, AsyncStream
from ...._models import FinalRequestOptions

_T = TypeVar("_T")


def _conversation_id_from_options(options: Optional[FinalRequestOptions]) -> str | None:
    if options is None or not is_mapping(options.json_data):
        return None
    conversation = options.json_data.get("conversation")
    if isinstance(conversation, str) and conversation:
        return conversation
    if is_mapping(conversation):
        conv_id = conversation.get("id")
        if isinstance(conv_id, str) and conv_id:
            return conv_id
    return None


def _function_call_item_to_param(item: object) -> dict[str, Any] | None:
    """Convert a streamed function_call output item into a conversations.items payload."""
    if is_mapping(item):
        data = dict(item)
    elif hasattr(item, "model_dump"):
        data = cast(Any, item).model_dump(exclude_unset=True)
    else:
        return None

    if data.get("type") != "function_call":
        return None

    call_id = data.get("call_id")
    name = data.get("name")
    if not isinstance(call_id, str) or not call_id:
        return None
    if not isinstance(name, str) or not name:
        return None

    param: dict[str, Any] = {
        "type": "function_call",
        "call_id": call_id,
        "name": name,
        "arguments": data.get("arguments") if isinstance(data.get("arguments"), str) else "",
    }
    item_id = data.get("id")
    if isinstance(item_id, str) and item_id:
        param["id"] = item_id
    status = data.get("status")
    if status in ("in_progress", "completed", "incomplete"):
        param["status"] = status
    return param


def _track_response_event(
    *,
    event: object,
    pending: dict[str, dict[str, Any]],
) -> bool:
    """Update pending function_call buffer from a Responses SSE event.

    Returns True if a `response.completed` event was seen.
    """
    event_type = getattr(event, "type", None)
    if event_type is None and is_mapping(event):
        event_type = event.get("type")

    if event_type == "response.completed":
        pending.clear()
        return True

    if event_type in ("response.output_item.added", "response.output_item.done"):
        item = getattr(event, "item", None)
        if item is None and is_mapping(event):
            item = event.get("item")

        item_type = item.get("type") if is_mapping(item) else getattr(item, "type", None)
        if item_type == "function_call_output":
            call_id = item.get("call_id") if is_mapping(item) else getattr(item, "call_id", None)
            if isinstance(call_id, str):
                pending.pop(call_id, None)
            return False

        param = _function_call_item_to_param(item)
        if param is not None:
            pending[param["call_id"]] = param
        return False

    return False


class ResponsesSSEStream(Stream[_T], Generic[_T]):
    """Responses `create(..., stream=True)` stream that preserves aborted function_calls.

    When a Responses stream is closed after a `function_call` item was observed but
    before `response.completed`, the Conversations API may discard that item. Closing
    this stream commits any still-pending function_call items into the conversation so
    a subsequent `function_call_output` does not 400.
    """

    def __init__(self, **kwargs: Any) -> None:
        self._pending_function_calls: dict[str, dict[str, Any]] = {}
        self._response_completed = False
        self._committed_pending = False
        super().__init__(**kwargs)

    @override
    def __stream__(self) -> Iterator[_T]:
        for event in super().__stream__():
            if _track_response_event(event=event, pending=self._pending_function_calls):
                self._response_completed = True
            yield event

    def commit_pending_function_calls(self) -> None:
        """Persist buffered function_call items into the conversation after an abort."""
        if self._response_completed or self._committed_pending or not self._pending_function_calls:
            return

        conversation_id = _conversation_id_from_options(self._options)
        if conversation_id is None:
            return

        items = list(self._pending_function_calls.values())
        self._client.conversations.items.create(conversation_id=conversation_id, items=items)
        self._committed_pending = True
        self._pending_function_calls.clear()

    @override
    def close(self) -> None:
        try:
            self.commit_pending_function_calls()
        finally:
            super().close()


class AsyncResponsesSSEStream(AsyncStream[_T], Generic[_T]):
    """Async variant of :class:`ResponsesSSEStream`."""

    def __init__(self, **kwargs: Any) -> None:
        self._pending_function_calls: dict[str, dict[str, Any]] = {}
        self._response_completed = False
        self._committed_pending = False
        super().__init__(**kwargs)

    @override
    async def __stream__(self) -> AsyncIterator[_T]:
        async for event in super().__stream__():
            if _track_response_event(event=event, pending=self._pending_function_calls):
                self._response_completed = True
            yield event

    async def commit_pending_function_calls(self) -> None:
        """Persist buffered function_call items into the conversation after an abort."""
        if self._response_completed or self._committed_pending or not self._pending_function_calls:
            return

        conversation_id = _conversation_id_from_options(self._options)
        if conversation_id is None:
            return

        items = list(self._pending_function_calls.values())
        await self._client.conversations.items.create(conversation_id=conversation_id, items=items)
        self._committed_pending = True
        self._pending_function_calls.clear()

    @override
    async def close(self) -> None:
        try:
            await self.commit_pending_function_calls()
        finally:
            await super().close()
