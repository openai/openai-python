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
    from .evals import (
        Evals as Evals,
        AsyncEvals as AsyncEvals,
        EvalsWithRawResponse as EvalsWithRawResponse,
        AsyncEvalsWithRawResponse as AsyncEvalsWithRawResponse,
        EvalsWithStreamingResponse as EvalsWithStreamingResponse,
        AsyncEvalsWithStreamingResponse as AsyncEvalsWithStreamingResponse,
    )

else:
    _EXPORTS = {
        "Runs": (".runs", "Runs"),
        "AsyncRuns": (".runs", "AsyncRuns"),
        "RunsWithRawResponse": (".runs", "RunsWithRawResponse"),
        "AsyncRunsWithRawResponse": (".runs", "AsyncRunsWithRawResponse"),
        "RunsWithStreamingResponse": (".runs", "RunsWithStreamingResponse"),
        "AsyncRunsWithStreamingResponse": (".runs", "AsyncRunsWithStreamingResponse"),
        "Evals": (".evals", "Evals"),
        "AsyncEvals": (".evals", "AsyncEvals"),
        "EvalsWithRawResponse": (".evals", "EvalsWithRawResponse"),
        "AsyncEvalsWithRawResponse": (".evals", "AsyncEvalsWithRawResponse"),
        "EvalsWithStreamingResponse": (".evals", "EvalsWithStreamingResponse"),
        "AsyncEvalsWithStreamingResponse": (".evals", "AsyncEvalsWithStreamingResponse"),
    }
    _SUBMODULES = {
        "evals",
        "runs",
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
    "Evals",
    "AsyncEvals",
    "EvalsWithRawResponse",
    "AsyncEvalsWithRawResponse",
    "EvalsWithStreamingResponse",
    "AsyncEvalsWithStreamingResponse",
]
