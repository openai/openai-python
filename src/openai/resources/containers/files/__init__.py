# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

import typing as _t

if _t.TYPE_CHECKING:
    from .files import (
        Files as Files,
        AsyncFiles as AsyncFiles,
        FilesWithRawResponse as FilesWithRawResponse,
        AsyncFilesWithRawResponse as AsyncFilesWithRawResponse,
        FilesWithStreamingResponse as FilesWithStreamingResponse,
        AsyncFilesWithStreamingResponse as AsyncFilesWithStreamingResponse,
    )
    from .content import (
        Content as Content,
        AsyncContent as AsyncContent,
        ContentWithRawResponse as ContentWithRawResponse,
        AsyncContentWithRawResponse as AsyncContentWithRawResponse,
        ContentWithStreamingResponse as ContentWithStreamingResponse,
        AsyncContentWithStreamingResponse as AsyncContentWithStreamingResponse,
    )

else:
    _EXPORTS = {
        "Content": (".content", "Content"),
        "AsyncContent": (".content", "AsyncContent"),
        "ContentWithRawResponse": (".content", "ContentWithRawResponse"),
        "AsyncContentWithRawResponse": (".content", "AsyncContentWithRawResponse"),
        "ContentWithStreamingResponse": (".content", "ContentWithStreamingResponse"),
        "AsyncContentWithStreamingResponse": (".content", "AsyncContentWithStreamingResponse"),
        "Files": (".files", "Files"),
        "AsyncFiles": (".files", "AsyncFiles"),
        "FilesWithRawResponse": (".files", "FilesWithRawResponse"),
        "AsyncFilesWithRawResponse": (".files", "AsyncFilesWithRawResponse"),
        "FilesWithStreamingResponse": (".files", "FilesWithStreamingResponse"),
        "AsyncFilesWithStreamingResponse": (".files", "AsyncFilesWithStreamingResponse"),
    }
    _SUBMODULES = {
        "content",
        "files",
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
    "Content",
    "AsyncContent",
    "ContentWithRawResponse",
    "AsyncContentWithRawResponse",
    "ContentWithStreamingResponse",
    "AsyncContentWithStreamingResponse",
    "Files",
    "AsyncFiles",
    "FilesWithRawResponse",
    "AsyncFilesWithRawResponse",
    "FilesWithStreamingResponse",
    "AsyncFilesWithStreamingResponse",
]
