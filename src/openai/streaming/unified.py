from dataclasses import dataclass
from typing import Optional, Literal, Any

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

def extract_text(ev: "StreamEvent") -> str:
    return ev.delta or ""
