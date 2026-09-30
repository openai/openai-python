# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

import typing as _t

if _t.TYPE_CHECKING:
    from .items import (
        Items as Items,
        AsyncItems as AsyncItems,
        ItemsWithRawResponse as ItemsWithRawResponse,
        AsyncItemsWithRawResponse as AsyncItemsWithRawResponse,
        ItemsWithStreamingResponse as ItemsWithStreamingResponse,
        AsyncItemsWithStreamingResponse as AsyncItemsWithStreamingResponse,
    )
    from .turns import (
        Turns as Turns,
        AsyncTurns as AsyncTurns,
        TurnsWithRawResponse as TurnsWithRawResponse,
        AsyncTurnsWithRawResponse as AsyncTurnsWithRawResponse,
        TurnsWithStreamingResponse as TurnsWithStreamingResponse,
        AsyncTurnsWithStreamingResponse as AsyncTurnsWithStreamingResponse,
    )
    from .events import (
        Events as Events,
        AsyncEvents as AsyncEvents,
        EventsWithRawResponse as EventsWithRawResponse,
        AsyncEventsWithRawResponse as AsyncEventsWithRawResponse,
        EventsWithStreamingResponse as EventsWithStreamingResponse,
        AsyncEventsWithStreamingResponse as AsyncEventsWithStreamingResponse,
    )
    from .sessions import (
        Sessions as Sessions,
        AsyncSessions as AsyncSessions,
        SessionsWithRawResponse as SessionsWithRawResponse,
        AsyncSessionsWithRawResponse as AsyncSessionsWithRawResponse,
        SessionsWithStreamingResponse as SessionsWithStreamingResponse,
        AsyncSessionsWithStreamingResponse as AsyncSessionsWithStreamingResponse,
    )
    from .artifacts import (
        Artifacts as Artifacts,
        AsyncArtifacts as AsyncArtifacts,
        ArtifactsWithRawResponse as ArtifactsWithRawResponse,
        AsyncArtifactsWithRawResponse as AsyncArtifactsWithRawResponse,
        ArtifactsWithStreamingResponse as ArtifactsWithStreamingResponse,
        AsyncArtifactsWithStreamingResponse as AsyncArtifactsWithStreamingResponse,
    )
    from .subagents import (
        Subagents as Subagents,
        AsyncSubagents as AsyncSubagents,
        SubagentsWithRawResponse as SubagentsWithRawResponse,
        AsyncSubagentsWithRawResponse as AsyncSubagentsWithRawResponse,
        SubagentsWithStreamingResponse as SubagentsWithStreamingResponse,
        AsyncSubagentsWithStreamingResponse as AsyncSubagentsWithStreamingResponse,
    )

else:
    _EXPORTS = {
        "Subagents": (".subagents", "Subagents"),
        "AsyncSubagents": (".subagents", "AsyncSubagents"),
        "SubagentsWithRawResponse": (".subagents", "SubagentsWithRawResponse"),
        "AsyncSubagentsWithRawResponse": (".subagents", "AsyncSubagentsWithRawResponse"),
        "SubagentsWithStreamingResponse": (".subagents", "SubagentsWithStreamingResponse"),
        "AsyncSubagentsWithStreamingResponse": (".subagents", "AsyncSubagentsWithStreamingResponse"),
        "Artifacts": (".artifacts", "Artifacts"),
        "AsyncArtifacts": (".artifacts", "AsyncArtifacts"),
        "ArtifactsWithRawResponse": (".artifacts", "ArtifactsWithRawResponse"),
        "AsyncArtifactsWithRawResponse": (".artifacts", "AsyncArtifactsWithRawResponse"),
        "ArtifactsWithStreamingResponse": (".artifacts", "ArtifactsWithStreamingResponse"),
        "AsyncArtifactsWithStreamingResponse": (".artifacts", "AsyncArtifactsWithStreamingResponse"),
        "Items": (".items", "Items"),
        "AsyncItems": (".items", "AsyncItems"),
        "ItemsWithRawResponse": (".items", "ItemsWithRawResponse"),
        "AsyncItemsWithRawResponse": (".items", "AsyncItemsWithRawResponse"),
        "ItemsWithStreamingResponse": (".items", "ItemsWithStreamingResponse"),
        "AsyncItemsWithStreamingResponse": (".items", "AsyncItemsWithStreamingResponse"),
        "Events": (".events", "Events"),
        "AsyncEvents": (".events", "AsyncEvents"),
        "EventsWithRawResponse": (".events", "EventsWithRawResponse"),
        "AsyncEventsWithRawResponse": (".events", "AsyncEventsWithRawResponse"),
        "EventsWithStreamingResponse": (".events", "EventsWithStreamingResponse"),
        "AsyncEventsWithStreamingResponse": (".events", "AsyncEventsWithStreamingResponse"),
        "Turns": (".turns", "Turns"),
        "AsyncTurns": (".turns", "AsyncTurns"),
        "TurnsWithRawResponse": (".turns", "TurnsWithRawResponse"),
        "AsyncTurnsWithRawResponse": (".turns", "AsyncTurnsWithRawResponse"),
        "TurnsWithStreamingResponse": (".turns", "TurnsWithStreamingResponse"),
        "AsyncTurnsWithStreamingResponse": (".turns", "AsyncTurnsWithStreamingResponse"),
        "Sessions": (".sessions", "Sessions"),
        "AsyncSessions": (".sessions", "AsyncSessions"),
        "SessionsWithRawResponse": (".sessions", "SessionsWithRawResponse"),
        "AsyncSessionsWithRawResponse": (".sessions", "AsyncSessionsWithRawResponse"),
        "SessionsWithStreamingResponse": (".sessions", "SessionsWithStreamingResponse"),
        "AsyncSessionsWithStreamingResponse": (".sessions", "AsyncSessionsWithStreamingResponse"),
    }
    _SUBMODULES = {
        "artifacts",
        "events",
        "items",
        "sessions",
        "subagents",
        "turns",
    }

    def __getattr__(name: str) -> _t.Any:
        import importlib

        if name in _EXPORTS:
            module_name, symbol_name = _EXPORTS[name]
            value = getattr(importlib.import_module(module_name, __name__), symbol_name)
        elif name in _SUBMODULES:
            value = importlib.import_module(f".{name}", __name__)
        else:
            raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
        globals()[name] = value
        return value

    def __dir__() -> list[str]:
        return sorted(set(globals()) | set(_EXPORTS) | _SUBMODULES)


__all__ = [
    "Subagents",
    "AsyncSubagents",
    "SubagentsWithRawResponse",
    "AsyncSubagentsWithRawResponse",
    "SubagentsWithStreamingResponse",
    "AsyncSubagentsWithStreamingResponse",
    "Artifacts",
    "AsyncArtifacts",
    "ArtifactsWithRawResponse",
    "AsyncArtifactsWithRawResponse",
    "ArtifactsWithStreamingResponse",
    "AsyncArtifactsWithStreamingResponse",
    "Items",
    "AsyncItems",
    "ItemsWithRawResponse",
    "AsyncItemsWithRawResponse",
    "ItemsWithStreamingResponse",
    "AsyncItemsWithStreamingResponse",
    "Events",
    "AsyncEvents",
    "EventsWithRawResponse",
    "AsyncEventsWithRawResponse",
    "EventsWithStreamingResponse",
    "AsyncEventsWithStreamingResponse",
    "Turns",
    "AsyncTurns",
    "TurnsWithRawResponse",
    "AsyncTurnsWithRawResponse",
    "TurnsWithStreamingResponse",
    "AsyncTurnsWithStreamingResponse",
    "Sessions",
    "AsyncSessions",
    "SessionsWithRawResponse",
    "AsyncSessionsWithRawResponse",
    "SessionsWithStreamingResponse",
    "AsyncSessionsWithStreamingResponse",
]
