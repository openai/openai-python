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
        "Items": (".items", "Items"),
        "AsyncItems": (".items", "AsyncItems"),
        "ItemsWithRawResponse": (".items", "ItemsWithRawResponse"),
        "AsyncItemsWithRawResponse": (".items", "AsyncItemsWithRawResponse"),
        "ItemsWithStreamingResponse": (".items", "ItemsWithStreamingResponse"),
        "AsyncItemsWithStreamingResponse": (".items", "AsyncItemsWithStreamingResponse"),
        "Turns": (".turns", "Turns"),
        "AsyncTurns": (".turns", "AsyncTurns"),
        "TurnsWithRawResponse": (".turns", "TurnsWithRawResponse"),
        "AsyncTurnsWithRawResponse": (".turns", "AsyncTurnsWithRawResponse"),
        "TurnsWithStreamingResponse": (".turns", "TurnsWithStreamingResponse"),
        "AsyncTurnsWithStreamingResponse": (".turns", "AsyncTurnsWithStreamingResponse"),
        "Subagents": (".subagents", "Subagents"),
        "AsyncSubagents": (".subagents", "AsyncSubagents"),
        "SubagentsWithRawResponse": (".subagents", "SubagentsWithRawResponse"),
        "AsyncSubagentsWithRawResponse": (".subagents", "AsyncSubagentsWithRawResponse"),
        "SubagentsWithStreamingResponse": (".subagents", "SubagentsWithStreamingResponse"),
        "AsyncSubagentsWithStreamingResponse": (".subagents", "AsyncSubagentsWithStreamingResponse"),
    }
    _SUBMODULES = {
        "items",
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
    "Items",
    "AsyncItems",
    "ItemsWithRawResponse",
    "AsyncItemsWithRawResponse",
    "ItemsWithStreamingResponse",
    "AsyncItemsWithStreamingResponse",
    "Turns",
    "AsyncTurns",
    "TurnsWithRawResponse",
    "AsyncTurnsWithRawResponse",
    "TurnsWithStreamingResponse",
    "AsyncTurnsWithStreamingResponse",
    "Subagents",
    "AsyncSubagents",
    "SubagentsWithRawResponse",
    "AsyncSubagentsWithRawResponse",
    "SubagentsWithStreamingResponse",
    "AsyncSubagentsWithStreamingResponse",
]
