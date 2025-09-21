from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Optional

EventType = Literal[
    "message_start",
    "output_text.delta",
    "output_text.done",
    "tool_call.delta",
    "tool_call.done",
    "response.completed",
    "response.error",
]


@dataclass
class StreamEvent:
    type: EventType
    model: Optional[str] = None
    delta: Optional[str] = None
    full_text: Optional[str] = None
    tool_call_id: Optional[str] = None
    raw: Optional[Any] = None


def extract_text(event: StreamEvent) -> str:
    """Return the text delta from a stream event."""

    return event.delta or ""


__all__ = [
    "EventType",
    "StreamEvent",
    "extract_text",
]
