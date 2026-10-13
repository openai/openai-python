"""Content-free local tool-runner diagnostics."""

from __future__ import annotations

import asyncio
from time import monotonic
from typing import Callable, cast
from inspect import isawaitable, iscoroutine
from typing_extensions import Literal, TypeAlias, TypedDict

__all__ = ["ToolDiagnostic", "ToolDiagnosticUsage", "ToolDiagnosticObserver"]


class ToolDiagnosticUsage(TypedDict):
    input_tokens: int
    output_tokens: int
    total_tokens: int


class ToolDiagnostic(TypedDict):
    api: Literal["responses", "decisions", "browser", "computer"]
    stage: Literal["run", "request", "arguments", "approval", "action", "output", "selection", "verification"]
    reason: Literal[
        "started",
        "completed",
        "refused",
        "cancelled",
        "invalid_input",
        "invalid_output",
        "api_failed",
        "driver_failed",
        "policy_failed",
        "step_limit",
        "busy",
        "closed",
    ]
    call_id: str | None
    member: str | None
    duration_ms: float
    usage: ToolDiagnosticUsage | None


ToolDiagnosticObserver: TypeAlias = Callable[[ToolDiagnostic], None]


def emit_tool_diagnostic(
    observer: ToolDiagnosticObserver | None,
    api: Literal["responses", "decisions", "browser", "computer"],
    stage: Literal["run", "request", "arguments", "approval", "action", "output", "selection", "verification"],
    reason: Literal[
        "started",
        "completed",
        "refused",
        "cancelled",
        "invalid_input",
        "invalid_output",
        "api_failed",
        "driver_failed",
        "policy_failed",
        "step_limit",
        "busy",
        "closed",
    ],
    started: float,
    *,
    call_id: str | None = None,
    member: str | None = None,
    usage: object = None,
) -> None:
    if observer is None:
        return
    try:
        numeric: ToolDiagnosticUsage | None = None
        if usage is not None:
            tokens = {name: getattr(usage, name, None) for name in ("input_tokens", "output_tokens", "total_tokens")}
            if all(type(value) is int and value >= 0 for value in tokens.values()):
                numeric = cast(ToolDiagnosticUsage, tokens)
        result = cast(Callable[[ToolDiagnostic], object], observer)(
            {
                "api": api,
                "stage": stage,
                "reason": reason,
                "call_id": call_id,
                "member": member,
                "duration_ms": max(0.0, (monotonic() - started) * 1000),
                "usage": numeric,
            }
        )
        if isawaitable(result):
            if iscoroutine(result):
                result.close()
            elif isinstance(result, asyncio.Future):
                result.add_done_callback(_consume_result)
    except (Exception, asyncio.CancelledError):
        pass


def _consume_result(result: asyncio.Future[object]) -> None:
    if not result.cancelled():
        result.exception()
