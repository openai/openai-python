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
    from .file_batches import (
        FileBatches as FileBatches,
        AsyncFileBatches as AsyncFileBatches,
        FileBatchesWithRawResponse as FileBatchesWithRawResponse,
        AsyncFileBatchesWithRawResponse as AsyncFileBatchesWithRawResponse,
        FileBatchesWithStreamingResponse as FileBatchesWithStreamingResponse,
        AsyncFileBatchesWithStreamingResponse as AsyncFileBatchesWithStreamingResponse,
    )
    from .vector_stores import (
        VectorStores as VectorStores,
        AsyncVectorStores as AsyncVectorStores,
        VectorStoresWithRawResponse as VectorStoresWithRawResponse,
        AsyncVectorStoresWithRawResponse as AsyncVectorStoresWithRawResponse,
        VectorStoresWithStreamingResponse as VectorStoresWithStreamingResponse,
        AsyncVectorStoresWithStreamingResponse as AsyncVectorStoresWithStreamingResponse,
    )

else:
    _EXPORTS = {
        "Files": (".files", "Files"),
        "AsyncFiles": (".files", "AsyncFiles"),
        "FilesWithRawResponse": (".files", "FilesWithRawResponse"),
        "AsyncFilesWithRawResponse": (".files", "AsyncFilesWithRawResponse"),
        "FilesWithStreamingResponse": (".files", "FilesWithStreamingResponse"),
        "AsyncFilesWithStreamingResponse": (".files", "AsyncFilesWithStreamingResponse"),
        "FileBatches": (".file_batches", "FileBatches"),
        "AsyncFileBatches": (".file_batches", "AsyncFileBatches"),
        "FileBatchesWithRawResponse": (".file_batches", "FileBatchesWithRawResponse"),
        "AsyncFileBatchesWithRawResponse": (".file_batches", "AsyncFileBatchesWithRawResponse"),
        "FileBatchesWithStreamingResponse": (".file_batches", "FileBatchesWithStreamingResponse"),
        "AsyncFileBatchesWithStreamingResponse": (".file_batches", "AsyncFileBatchesWithStreamingResponse"),
        "VectorStores": (".vector_stores", "VectorStores"),
        "AsyncVectorStores": (".vector_stores", "AsyncVectorStores"),
        "VectorStoresWithRawResponse": (".vector_stores", "VectorStoresWithRawResponse"),
        "AsyncVectorStoresWithRawResponse": (".vector_stores", "AsyncVectorStoresWithRawResponse"),
        "VectorStoresWithStreamingResponse": (".vector_stores", "VectorStoresWithStreamingResponse"),
        "AsyncVectorStoresWithStreamingResponse": (".vector_stores", "AsyncVectorStoresWithStreamingResponse"),
    }
    _SUBMODULES = {
        "file_batches",
        "files",
        "vector_stores",
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
    "FileBatches",
    "AsyncFileBatches",
    "FileBatchesWithRawResponse",
    "AsyncFileBatchesWithRawResponse",
    "FileBatchesWithStreamingResponse",
    "AsyncFileBatchesWithStreamingResponse",
    "VectorStores",
    "AsyncVectorStores",
    "VectorStoresWithRawResponse",
    "AsyncVectorStoresWithRawResponse",
    "VectorStoresWithStreamingResponse",
    "AsyncVectorStoresWithStreamingResponse",
]
