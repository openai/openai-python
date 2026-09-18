# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

import typing as _t

if _t.TYPE_CHECKING:
    from .runs import (
        Runs as Runs,
        AsyncRuns as AsyncRuns,
        RunsWithRawResponse as RunsWithRawResponse,
        AsyncRunsWithRawResponse as AsyncRunsWithRawResponse,
        RunsWithStreamingResponse as RunsWithStreamingResponse,
        AsyncRunsWithStreamingResponse as AsyncRunsWithStreamingResponse,
    )
    from .threads import (
        Threads as Threads,
        AsyncThreads as AsyncThreads,
        ThreadsWithRawResponse as ThreadsWithRawResponse,
        AsyncThreadsWithRawResponse as AsyncThreadsWithRawResponse,
        ThreadsWithStreamingResponse as ThreadsWithStreamingResponse,
        AsyncThreadsWithStreamingResponse as AsyncThreadsWithStreamingResponse,
    )
    from .messages import (
        Messages as Messages,
        AsyncMessages as AsyncMessages,
        MessagesWithRawResponse as MessagesWithRawResponse,
        AsyncMessagesWithRawResponse as AsyncMessagesWithRawResponse,
        MessagesWithStreamingResponse as MessagesWithStreamingResponse,
        AsyncMessagesWithStreamingResponse as AsyncMessagesWithStreamingResponse,
    )

else:
    _EXPORTS = {
        "Runs": (".runs", "Runs"),
        "AsyncRuns": (".runs", "AsyncRuns"),
        "RunsWithRawResponse": (".runs", "RunsWithRawResponse"),
        "AsyncRunsWithRawResponse": (".runs", "AsyncRunsWithRawResponse"),
        "RunsWithStreamingResponse": (".runs", "RunsWithStreamingResponse"),
        "AsyncRunsWithStreamingResponse": (".runs", "AsyncRunsWithStreamingResponse"),
        "Messages": (".messages", "Messages"),
        "AsyncMessages": (".messages", "AsyncMessages"),
        "MessagesWithRawResponse": (".messages", "MessagesWithRawResponse"),
        "AsyncMessagesWithRawResponse": (".messages", "AsyncMessagesWithRawResponse"),
        "MessagesWithStreamingResponse": (".messages", "MessagesWithStreamingResponse"),
        "AsyncMessagesWithStreamingResponse": (".messages", "AsyncMessagesWithStreamingResponse"),
        "Threads": (".threads", "Threads"),
        "AsyncThreads": (".threads", "AsyncThreads"),
        "ThreadsWithRawResponse": (".threads", "ThreadsWithRawResponse"),
        "AsyncThreadsWithRawResponse": (".threads", "AsyncThreadsWithRawResponse"),
        "ThreadsWithStreamingResponse": (".threads", "ThreadsWithStreamingResponse"),
        "AsyncThreadsWithStreamingResponse": (".threads", "AsyncThreadsWithStreamingResponse"),
    }
    _SUBMODULES = {
        "messages",
        "runs",
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
    "Runs",
    "AsyncRuns",
    "RunsWithRawResponse",
    "AsyncRunsWithRawResponse",
    "RunsWithStreamingResponse",
    "AsyncRunsWithStreamingResponse",
    "Messages",
    "AsyncMessages",
    "MessagesWithRawResponse",
    "AsyncMessagesWithRawResponse",
    "MessagesWithStreamingResponse",
    "AsyncMessagesWithStreamingResponse",
    "Threads",
    "AsyncThreads",
    "ThreadsWithRawResponse",
    "AsyncThreadsWithRawResponse",
    "ThreadsWithStreamingResponse",
    "AsyncThreadsWithStreamingResponse",
]
