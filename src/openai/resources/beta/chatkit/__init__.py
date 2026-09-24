# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

import typing as _t

if _t.TYPE_CHECKING:
    from .chatkit import (
        ChatKit as ChatKit,
        AsyncChatKit as AsyncChatKit,
        ChatKitWithRawResponse as ChatKitWithRawResponse,
        AsyncChatKitWithRawResponse as AsyncChatKitWithRawResponse,
        ChatKitWithStreamingResponse as ChatKitWithStreamingResponse,
        AsyncChatKitWithStreamingResponse as AsyncChatKitWithStreamingResponse,
    )
    from .threads import (
        Threads as Threads,
        AsyncThreads as AsyncThreads,
        ThreadsWithRawResponse as ThreadsWithRawResponse,
        AsyncThreadsWithRawResponse as AsyncThreadsWithRawResponse,
        ThreadsWithStreamingResponse as ThreadsWithStreamingResponse,
        AsyncThreadsWithStreamingResponse as AsyncThreadsWithStreamingResponse,
    )
    from .sessions import (
        Sessions as Sessions,
        AsyncSessions as AsyncSessions,
        SessionsWithRawResponse as SessionsWithRawResponse,
        AsyncSessionsWithRawResponse as AsyncSessionsWithRawResponse,
        SessionsWithStreamingResponse as SessionsWithStreamingResponse,
        AsyncSessionsWithStreamingResponse as AsyncSessionsWithStreamingResponse,
    )

else:
    _EXPORTS = {
        "Sessions": (".sessions", "Sessions"),
        "AsyncSessions": (".sessions", "AsyncSessions"),
        "SessionsWithRawResponse": (".sessions", "SessionsWithRawResponse"),
        "AsyncSessionsWithRawResponse": (".sessions", "AsyncSessionsWithRawResponse"),
        "SessionsWithStreamingResponse": (".sessions", "SessionsWithStreamingResponse"),
        "AsyncSessionsWithStreamingResponse": (".sessions", "AsyncSessionsWithStreamingResponse"),
        "Threads": (".threads", "Threads"),
        "AsyncThreads": (".threads", "AsyncThreads"),
        "ThreadsWithRawResponse": (".threads", "ThreadsWithRawResponse"),
        "AsyncThreadsWithRawResponse": (".threads", "AsyncThreadsWithRawResponse"),
        "ThreadsWithStreamingResponse": (".threads", "ThreadsWithStreamingResponse"),
        "AsyncThreadsWithStreamingResponse": (".threads", "AsyncThreadsWithStreamingResponse"),
        "ChatKit": (".chatkit", "ChatKit"),
        "AsyncChatKit": (".chatkit", "AsyncChatKit"),
        "ChatKitWithRawResponse": (".chatkit", "ChatKitWithRawResponse"),
        "AsyncChatKitWithRawResponse": (".chatkit", "AsyncChatKitWithRawResponse"),
        "ChatKitWithStreamingResponse": (".chatkit", "ChatKitWithStreamingResponse"),
        "AsyncChatKitWithStreamingResponse": (".chatkit", "AsyncChatKitWithStreamingResponse"),
    }
    _SUBMODULES = {
        "chatkit",
        "sessions",
        "threads",
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
    "Sessions",
    "AsyncSessions",
    "SessionsWithRawResponse",
    "AsyncSessionsWithRawResponse",
    "SessionsWithStreamingResponse",
    "AsyncSessionsWithStreamingResponse",
    "Threads",
    "AsyncThreads",
    "ThreadsWithRawResponse",
    "AsyncThreadsWithRawResponse",
    "ThreadsWithStreamingResponse",
    "AsyncThreadsWithStreamingResponse",
    "ChatKit",
    "AsyncChatKit",
    "ChatKitWithRawResponse",
    "AsyncChatKitWithRawResponse",
    "ChatKitWithStreamingResponse",
    "AsyncChatKitWithStreamingResponse",
]
