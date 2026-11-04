from __future__ import annotations

from typing import Callable, Awaitable
from dataclasses import dataclass
from typing_extensions import Literal, TypeAlias

ToolErrorStage: TypeAlias = Literal["arguments", "execution", "output"]


@dataclass(frozen=True)
class AgentToolError:
    """Local diagnostic passed to ``sessions.stream(on_tool_error=...)``.

    Use alongside ``tool_handlers`` to log or monitor argument validation,
    execution, and output serialization failures. ``error`` is the original
    local exception; it is never sent to the model. API and stream errors
    propagate normally without invoking the callback.
    """

    error: Exception
    tool_name: str
    session_id: str
    turn_id: str
    call_id: str
    stage: ToolErrorStage


ToolErrorHandler: TypeAlias = Callable[[AgentToolError], None]
AsyncToolErrorHandler: TypeAlias = Callable[[AgentToolError], None | Awaitable[None]]
