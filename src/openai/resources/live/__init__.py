# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

import typing as _t

if _t.TYPE_CHECKING:
    from .live import (
        Live as Live,
        AsyncLive as AsyncLive,
        LiveWithRawResponse as LiveWithRawResponse,
        AsyncLiveWithRawResponse as AsyncLiveWithRawResponse,
        LiveWithStreamingResponse as LiveWithStreamingResponse,
        AsyncLiveWithStreamingResponse as AsyncLiveWithStreamingResponse,
    )
    from .forks import (
        Forks as Forks,
        AsyncForks as AsyncForks,
    )
    from .sessions import (
        Sessions as Sessions,
        AsyncSessions as AsyncSessions,
        SessionsWithRawResponse as SessionsWithRawResponse,
        AsyncSessionsWithRawResponse as AsyncSessionsWithRawResponse,
        SessionsWithStreamingResponse as SessionsWithStreamingResponse,
        AsyncSessionsWithStreamingResponse as AsyncSessionsWithStreamingResponse,
    )
    from .sideband import (
        Sideband as Sideband,
        AsyncSideband as AsyncSideband,
    )

else:
    _EXPORTS = {
        "Sideband": (".sideband", "Sideband"),
        "AsyncSideband": (".sideband", "AsyncSideband"),
        "Forks": (".forks", "Forks"),
        "AsyncForks": (".forks", "AsyncForks"),
        "Sessions": (".sessions", "Sessions"),
        "AsyncSessions": (".sessions", "AsyncSessions"),
        "SessionsWithRawResponse": (".sessions", "SessionsWithRawResponse"),
        "AsyncSessionsWithRawResponse": (".sessions", "AsyncSessionsWithRawResponse"),
        "SessionsWithStreamingResponse": (".sessions", "SessionsWithStreamingResponse"),
        "AsyncSessionsWithStreamingResponse": (".sessions", "AsyncSessionsWithStreamingResponse"),
        "Live": (".live", "Live"),
        "AsyncLive": (".live", "AsyncLive"),
        "LiveWithRawResponse": (".live", "LiveWithRawResponse"),
        "AsyncLiveWithRawResponse": (".live", "AsyncLiveWithRawResponse"),
        "LiveWithStreamingResponse": (".live", "LiveWithStreamingResponse"),
        "AsyncLiveWithStreamingResponse": (".live", "AsyncLiveWithStreamingResponse"),
    }
    _SUBMODULES = {
        "forks",
        "live",
        "sessions",
        "sideband",
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
    "Sideband",
    "AsyncSideband",
    "Forks",
    "AsyncForks",
    "Sessions",
    "AsyncSessions",
    "SessionsWithRawResponse",
    "AsyncSessionsWithRawResponse",
    "SessionsWithStreamingResponse",
    "AsyncSessionsWithStreamingResponse",
    "Live",
    "AsyncLive",
    "LiveWithRawResponse",
    "AsyncLiveWithRawResponse",
    "LiveWithStreamingResponse",
    "AsyncLiveWithStreamingResponse",
]
