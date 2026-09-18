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
    from .templates import (
        Templates as Templates,
        AsyncTemplates as AsyncTemplates,
        TemplatesWithRawResponse as TemplatesWithRawResponse,
        AsyncTemplatesWithRawResponse as AsyncTemplatesWithRawResponse,
        TemplatesWithStreamingResponse as TemplatesWithStreamingResponse,
        AsyncTemplatesWithStreamingResponse as AsyncTemplatesWithStreamingResponse,
    )
    from .environments import (
        Environments as Environments,
        AsyncEnvironments as AsyncEnvironments,
        EnvironmentsWithRawResponse as EnvironmentsWithRawResponse,
        AsyncEnvironmentsWithRawResponse as AsyncEnvironmentsWithRawResponse,
        EnvironmentsWithStreamingResponse as EnvironmentsWithStreamingResponse,
        AsyncEnvironmentsWithStreamingResponse as AsyncEnvironmentsWithStreamingResponse,
    )

else:
    _EXPORTS = {
        "Files": (".files", "Files"),
        "AsyncFiles": (".files", "AsyncFiles"),
        "FilesWithRawResponse": (".files", "FilesWithRawResponse"),
        "AsyncFilesWithRawResponse": (".files", "AsyncFilesWithRawResponse"),
        "FilesWithStreamingResponse": (".files", "FilesWithStreamingResponse"),
        "AsyncFilesWithStreamingResponse": (".files", "AsyncFilesWithStreamingResponse"),
        "Templates": (".templates", "Templates"),
        "AsyncTemplates": (".templates", "AsyncTemplates"),
        "TemplatesWithRawResponse": (".templates", "TemplatesWithRawResponse"),
        "AsyncTemplatesWithRawResponse": (".templates", "AsyncTemplatesWithRawResponse"),
        "TemplatesWithStreamingResponse": (".templates", "TemplatesWithStreamingResponse"),
        "AsyncTemplatesWithStreamingResponse": (".templates", "AsyncTemplatesWithStreamingResponse"),
        "Environments": (".environments", "Environments"),
        "AsyncEnvironments": (".environments", "AsyncEnvironments"),
        "EnvironmentsWithRawResponse": (".environments", "EnvironmentsWithRawResponse"),
        "AsyncEnvironmentsWithRawResponse": (".environments", "AsyncEnvironmentsWithRawResponse"),
        "EnvironmentsWithStreamingResponse": (".environments", "EnvironmentsWithStreamingResponse"),
        "AsyncEnvironmentsWithStreamingResponse": (".environments", "AsyncEnvironmentsWithStreamingResponse"),
    }
    _SUBMODULES = {
        "environments",
        "files",
        "templates",
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
    "Templates",
    "AsyncTemplates",
    "TemplatesWithRawResponse",
    "AsyncTemplatesWithRawResponse",
    "TemplatesWithStreamingResponse",
    "AsyncTemplatesWithStreamingResponse",
    "Environments",
    "AsyncEnvironments",
    "EnvironmentsWithRawResponse",
    "AsyncEnvironmentsWithRawResponse",
    "EnvironmentsWithStreamingResponse",
    "AsyncEnvironmentsWithStreamingResponse",
]
