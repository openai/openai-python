# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

import typing as _t

if _t.TYPE_CHECKING:
    from .messages import (
        Messages as Messages,
        AsyncMessages as AsyncMessages,
        MessagesWithRawResponse as MessagesWithRawResponse,
        AsyncMessagesWithRawResponse as AsyncMessagesWithRawResponse,
        MessagesWithStreamingResponse as MessagesWithStreamingResponse,
        AsyncMessagesWithStreamingResponse as AsyncMessagesWithStreamingResponse,
    )
    from .completions import (
        Completions as Completions,
        AsyncCompletions as AsyncCompletions,
        CompletionsWithRawResponse as CompletionsWithRawResponse,
        AsyncCompletionsWithRawResponse as AsyncCompletionsWithRawResponse,
        CompletionsWithStreamingResponse as CompletionsWithStreamingResponse,
        AsyncCompletionsWithStreamingResponse as AsyncCompletionsWithStreamingResponse,
    )

else:
    _EXPORTS = {
        "Messages": (".messages", "Messages"),
        "AsyncMessages": (".messages", "AsyncMessages"),
        "MessagesWithRawResponse": (".messages", "MessagesWithRawResponse"),
        "AsyncMessagesWithRawResponse": (".messages", "AsyncMessagesWithRawResponse"),
        "MessagesWithStreamingResponse": (".messages", "MessagesWithStreamingResponse"),
        "AsyncMessagesWithStreamingResponse": (".messages", "AsyncMessagesWithStreamingResponse"),
        "Completions": (".completions", "Completions"),
        "AsyncCompletions": (".completions", "AsyncCompletions"),
        "CompletionsWithRawResponse": (".completions", "CompletionsWithRawResponse"),
        "AsyncCompletionsWithRawResponse": (".completions", "AsyncCompletionsWithRawResponse"),
        "CompletionsWithStreamingResponse": (".completions", "CompletionsWithStreamingResponse"),
        "AsyncCompletionsWithStreamingResponse": (".completions", "AsyncCompletionsWithStreamingResponse"),
    }
    _SUBMODULES = {
        "completions",
        "messages",
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
    "Messages",
    "AsyncMessages",
    "MessagesWithRawResponse",
    "AsyncMessagesWithRawResponse",
    "MessagesWithStreamingResponse",
    "AsyncMessagesWithStreamingResponse",
    "Completions",
    "AsyncCompletions",
    "CompletionsWithRawResponse",
    "AsyncCompletionsWithRawResponse",
    "CompletionsWithStreamingResponse",
    "AsyncCompletionsWithStreamingResponse",
]
