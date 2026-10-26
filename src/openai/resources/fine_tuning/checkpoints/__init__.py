# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

import typing as _t

if _t.TYPE_CHECKING:
    from .checkpoints import (
        Checkpoints as Checkpoints,
        AsyncCheckpoints as AsyncCheckpoints,
        CheckpointsWithRawResponse as CheckpointsWithRawResponse,
        AsyncCheckpointsWithRawResponse as AsyncCheckpointsWithRawResponse,
        CheckpointsWithStreamingResponse as CheckpointsWithStreamingResponse,
        AsyncCheckpointsWithStreamingResponse as AsyncCheckpointsWithStreamingResponse,
    )
    from .permissions import (
        Permissions as Permissions,
        AsyncPermissions as AsyncPermissions,
        PermissionsWithRawResponse as PermissionsWithRawResponse,
        AsyncPermissionsWithRawResponse as AsyncPermissionsWithRawResponse,
        PermissionsWithStreamingResponse as PermissionsWithStreamingResponse,
        AsyncPermissionsWithStreamingResponse as AsyncPermissionsWithStreamingResponse,
    )

else:
    _EXPORTS = {
        "Permissions": (".permissions", "Permissions"),
        "AsyncPermissions": (".permissions", "AsyncPermissions"),
        "PermissionsWithRawResponse": (".permissions", "PermissionsWithRawResponse"),
        "AsyncPermissionsWithRawResponse": (".permissions", "AsyncPermissionsWithRawResponse"),
        "PermissionsWithStreamingResponse": (".permissions", "PermissionsWithStreamingResponse"),
        "AsyncPermissionsWithStreamingResponse": (".permissions", "AsyncPermissionsWithStreamingResponse"),
        "Checkpoints": (".checkpoints", "Checkpoints"),
        "AsyncCheckpoints": (".checkpoints", "AsyncCheckpoints"),
        "CheckpointsWithRawResponse": (".checkpoints", "CheckpointsWithRawResponse"),
        "AsyncCheckpointsWithRawResponse": (".checkpoints", "AsyncCheckpointsWithRawResponse"),
        "CheckpointsWithStreamingResponse": (".checkpoints", "CheckpointsWithStreamingResponse"),
        "AsyncCheckpointsWithStreamingResponse": (".checkpoints", "AsyncCheckpointsWithStreamingResponse"),
    }
    _SUBMODULES = {
        "checkpoints",
        "permissions",
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
    "Permissions",
    "AsyncPermissions",
    "PermissionsWithRawResponse",
    "AsyncPermissionsWithRawResponse",
    "PermissionsWithStreamingResponse",
    "AsyncPermissionsWithStreamingResponse",
    "Checkpoints",
    "AsyncCheckpoints",
    "CheckpointsWithRawResponse",
    "AsyncCheckpointsWithRawResponse",
    "CheckpointsWithStreamingResponse",
    "AsyncCheckpointsWithStreamingResponse",
]
