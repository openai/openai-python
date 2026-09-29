# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

import typing as _t

if _t.TYPE_CHECKING:
    from .alpha import (
        Alpha as Alpha,
        AsyncAlpha as AsyncAlpha,
        AlphaWithRawResponse as AlphaWithRawResponse,
        AsyncAlphaWithRawResponse as AsyncAlphaWithRawResponse,
        AlphaWithStreamingResponse as AlphaWithStreamingResponse,
        AsyncAlphaWithStreamingResponse as AsyncAlphaWithStreamingResponse,
    )
    from .graders import (
        Graders as Graders,
        AsyncGraders as AsyncGraders,
        GradersWithRawResponse as GradersWithRawResponse,
        AsyncGradersWithRawResponse as AsyncGradersWithRawResponse,
        GradersWithStreamingResponse as GradersWithStreamingResponse,
        AsyncGradersWithStreamingResponse as AsyncGradersWithStreamingResponse,
    )

else:
    _EXPORTS = {
        "Graders": (".graders", "Graders"),
        "AsyncGraders": (".graders", "AsyncGraders"),
        "GradersWithRawResponse": (".graders", "GradersWithRawResponse"),
        "AsyncGradersWithRawResponse": (".graders", "AsyncGradersWithRawResponse"),
        "GradersWithStreamingResponse": (".graders", "GradersWithStreamingResponse"),
        "AsyncGradersWithStreamingResponse": (".graders", "AsyncGradersWithStreamingResponse"),
        "Alpha": (".alpha", "Alpha"),
        "AsyncAlpha": (".alpha", "AsyncAlpha"),
        "AlphaWithRawResponse": (".alpha", "AlphaWithRawResponse"),
        "AsyncAlphaWithRawResponse": (".alpha", "AsyncAlphaWithRawResponse"),
        "AlphaWithStreamingResponse": (".alpha", "AlphaWithStreamingResponse"),
        "AsyncAlphaWithStreamingResponse": (".alpha", "AsyncAlphaWithStreamingResponse"),
    }
    _SUBMODULES = {
        "alpha",
        "graders",
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
    "Graders",
    "AsyncGraders",
    "GradersWithRawResponse",
    "AsyncGradersWithRawResponse",
    "GradersWithStreamingResponse",
    "AsyncGradersWithStreamingResponse",
    "Alpha",
    "AsyncAlpha",
    "AlphaWithRawResponse",
    "AsyncAlphaWithRawResponse",
    "AlphaWithStreamingResponse",
    "AsyncAlphaWithStreamingResponse",
]
