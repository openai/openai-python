from __future__ import annotations

from typing import Any

from .unified import StreamEvent


class ResponsesEventAdapter:
    """Map Responses API streaming events into the unified stream shape."""

    @staticmethod
    def adapt(event: Any) -> StreamEvent:
        event_type = getattr(event, "type", None)

        if event_type == "response.output_text.delta":
            return StreamEvent(
                type="output_text.delta",
                delta=getattr(event, "delta", None),
                raw=event,
            )

        if event_type == "response.completed":
            return StreamEvent(type="response.completed", raw=event)

        return StreamEvent(type="response.error", raw=event)


class ChatCompletionsEventAdapter:
    """Map Chat Completions streaming chunks into the unified stream shape."""

    @staticmethod
    def adapt(chunk: Any) -> StreamEvent:
        try:
            choice = chunk.choices[0]
            delta = getattr(getattr(choice, "delta", None), "content", None)
            if delta:
                return StreamEvent(type="output_text.delta", delta=delta, raw=chunk)
        except Exception:  # pragma: no cover - defensive adapter guard
            pass

        return StreamEvent(type="response.completed", raw=chunk)


__all__ = [
    "ChatCompletionsEventAdapter",
    "ResponsesEventAdapter",
]
