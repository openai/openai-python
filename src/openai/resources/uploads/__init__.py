# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

import typing as _t

if _t.TYPE_CHECKING:
    from .parts import (
        Parts as Parts,
        AsyncParts as AsyncParts,
        PartsWithRawResponse as PartsWithRawResponse,
        AsyncPartsWithRawResponse as AsyncPartsWithRawResponse,
        PartsWithStreamingResponse as PartsWithStreamingResponse,
        AsyncPartsWithStreamingResponse as AsyncPartsWithStreamingResponse,
    )
    from .uploads import (
        Uploads as Uploads,
        AsyncUploads as AsyncUploads,
        UploadsWithRawResponse as UploadsWithRawResponse,
        AsyncUploadsWithRawResponse as AsyncUploadsWithRawResponse,
        UploadsWithStreamingResponse as UploadsWithStreamingResponse,
        AsyncUploadsWithStreamingResponse as AsyncUploadsWithStreamingResponse,
    )

else:
    _EXPORTS = {
        "Parts": (".parts", "Parts"),
        "AsyncParts": (".parts", "AsyncParts"),
        "PartsWithRawResponse": (".parts", "PartsWithRawResponse"),
        "AsyncPartsWithRawResponse": (".parts", "AsyncPartsWithRawResponse"),
        "PartsWithStreamingResponse": (".parts", "PartsWithStreamingResponse"),
        "AsyncPartsWithStreamingResponse": (".parts", "AsyncPartsWithStreamingResponse"),
        "Uploads": (".uploads", "Uploads"),
        "AsyncUploads": (".uploads", "AsyncUploads"),
        "UploadsWithRawResponse": (".uploads", "UploadsWithRawResponse"),
        "AsyncUploadsWithRawResponse": (".uploads", "AsyncUploadsWithRawResponse"),
        "UploadsWithStreamingResponse": (".uploads", "UploadsWithStreamingResponse"),
        "AsyncUploadsWithStreamingResponse": (".uploads", "AsyncUploadsWithStreamingResponse"),
    }
    _SUBMODULES = {
        "parts",
        "uploads",
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
    "Parts",
    "AsyncParts",
    "PartsWithRawResponse",
    "AsyncPartsWithRawResponse",
    "PartsWithStreamingResponse",
    "AsyncPartsWithStreamingResponse",
    "Uploads",
    "AsyncUploads",
    "UploadsWithRawResponse",
    "AsyncUploadsWithRawResponse",
    "UploadsWithStreamingResponse",
    "AsyncUploadsWithStreamingResponse",
]
