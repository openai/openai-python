# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

import typing as _t

if _t.TYPE_CHECKING:
    from .chat import (
        Chat as Chat,
        AsyncChat as AsyncChat,
        ChatWithRawResponse as ChatWithRawResponse,
        AsyncChatWithRawResponse as AsyncChatWithRawResponse,
        ChatWithStreamingResponse as ChatWithStreamingResponse,
        AsyncChatWithStreamingResponse as AsyncChatWithStreamingResponse,
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
        "Completions": (".completions", "Completions"),
        "AsyncCompletions": (".completions", "AsyncCompletions"),
        "CompletionsWithRawResponse": (".completions", "CompletionsWithRawResponse"),
        "AsyncCompletionsWithRawResponse": (".completions", "AsyncCompletionsWithRawResponse"),
        "CompletionsWithStreamingResponse": (".completions", "CompletionsWithStreamingResponse"),
        "AsyncCompletionsWithStreamingResponse": (".completions", "AsyncCompletionsWithStreamingResponse"),
        "Chat": (".chat", "Chat"),
        "AsyncChat": (".chat", "AsyncChat"),
        "ChatWithRawResponse": (".chat", "ChatWithRawResponse"),
        "AsyncChatWithRawResponse": (".chat", "AsyncChatWithRawResponse"),
        "ChatWithStreamingResponse": (".chat", "ChatWithStreamingResponse"),
        "AsyncChatWithStreamingResponse": (".chat", "AsyncChatWithStreamingResponse"),
    }
    _SUBMODULES = {
        "chat",
        "completions",
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
    "Completions",
    "AsyncCompletions",
    "CompletionsWithRawResponse",
    "AsyncCompletionsWithRawResponse",
    "CompletionsWithStreamingResponse",
    "AsyncCompletionsWithStreamingResponse",
    "Chat",
    "AsyncChat",
    "ChatWithRawResponse",
    "AsyncChatWithRawResponse",
    "ChatWithStreamingResponse",
    "AsyncChatWithStreamingResponse",
]
