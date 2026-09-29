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
    from .containers import (
        Containers as Containers,
        AsyncContainers as AsyncContainers,
        ContainersWithRawResponse as ContainersWithRawResponse,
        AsyncContainersWithRawResponse as AsyncContainersWithRawResponse,
        ContainersWithStreamingResponse as ContainersWithStreamingResponse,
        AsyncContainersWithStreamingResponse as AsyncContainersWithStreamingResponse,
    )

else:
    _EXPORTS = {
        "Files": (".files", "Files"),
        "AsyncFiles": (".files", "AsyncFiles"),
        "FilesWithRawResponse": (".files", "FilesWithRawResponse"),
        "AsyncFilesWithRawResponse": (".files", "AsyncFilesWithRawResponse"),
        "FilesWithStreamingResponse": (".files", "FilesWithStreamingResponse"),
        "AsyncFilesWithStreamingResponse": (".files", "AsyncFilesWithStreamingResponse"),
        "Containers": (".containers", "Containers"),
        "AsyncContainers": (".containers", "AsyncContainers"),
        "ContainersWithRawResponse": (".containers", "ContainersWithRawResponse"),
        "AsyncContainersWithRawResponse": (".containers", "AsyncContainersWithRawResponse"),
        "ContainersWithStreamingResponse": (".containers", "ContainersWithStreamingResponse"),
        "AsyncContainersWithStreamingResponse": (".containers", "AsyncContainersWithStreamingResponse"),
    }
    _SUBMODULES = {
        "containers",
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
    "Files",
    "AsyncFiles",
    "FilesWithRawResponse",
    "AsyncFilesWithRawResponse",
    "FilesWithStreamingResponse",
    "AsyncFilesWithStreamingResponse",
    "Containers",
    "AsyncContainers",
    "ContainersWithRawResponse",
    "AsyncContainersWithRawResponse",
    "ContainersWithStreamingResponse",
    "AsyncContainersWithStreamingResponse",
]
