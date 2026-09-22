# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

import typing as _t

if _t.TYPE_CHECKING:
    from .jobs import (
        Jobs as Jobs,
        AsyncJobs as AsyncJobs,
        JobsWithRawResponse as JobsWithRawResponse,
        AsyncJobsWithRawResponse as AsyncJobsWithRawResponse,
        JobsWithStreamingResponse as JobsWithStreamingResponse,
        AsyncJobsWithStreamingResponse as AsyncJobsWithStreamingResponse,
    )
    from .checkpoints import (
        Checkpoints as Checkpoints,
        AsyncCheckpoints as AsyncCheckpoints,
        CheckpointsWithRawResponse as CheckpointsWithRawResponse,
        AsyncCheckpointsWithRawResponse as AsyncCheckpointsWithRawResponse,
        CheckpointsWithStreamingResponse as CheckpointsWithStreamingResponse,
        AsyncCheckpointsWithStreamingResponse as AsyncCheckpointsWithStreamingResponse,
    )

else:
    _EXPORTS = {
        "Checkpoints": (".checkpoints", "Checkpoints"),
        "AsyncCheckpoints": (".checkpoints", "AsyncCheckpoints"),
        "CheckpointsWithRawResponse": (".checkpoints", "CheckpointsWithRawResponse"),
        "AsyncCheckpointsWithRawResponse": (".checkpoints", "AsyncCheckpointsWithRawResponse"),
        "CheckpointsWithStreamingResponse": (".checkpoints", "CheckpointsWithStreamingResponse"),
        "AsyncCheckpointsWithStreamingResponse": (".checkpoints", "AsyncCheckpointsWithStreamingResponse"),
        "Jobs": (".jobs", "Jobs"),
        "AsyncJobs": (".jobs", "AsyncJobs"),
        "JobsWithRawResponse": (".jobs", "JobsWithRawResponse"),
        "AsyncJobsWithRawResponse": (".jobs", "AsyncJobsWithRawResponse"),
        "JobsWithStreamingResponse": (".jobs", "JobsWithStreamingResponse"),
        "AsyncJobsWithStreamingResponse": (".jobs", "AsyncJobsWithStreamingResponse"),
    }
    _SUBMODULES = {
        "checkpoints",
        "jobs",
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
    "Checkpoints",
    "AsyncCheckpoints",
    "CheckpointsWithRawResponse",
    "AsyncCheckpointsWithRawResponse",
    "CheckpointsWithStreamingResponse",
    "AsyncCheckpointsWithStreamingResponse",
    "Jobs",
    "AsyncJobs",
    "JobsWithRawResponse",
    "AsyncJobsWithRawResponse",
    "JobsWithStreamingResponse",
    "AsyncJobsWithStreamingResponse",
]
