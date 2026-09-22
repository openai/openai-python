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
    from .alpha import (
        Alpha as Alpha,
        AsyncAlpha as AsyncAlpha,
        AlphaWithRawResponse as AlphaWithRawResponse,
        AsyncAlphaWithRawResponse as AsyncAlphaWithRawResponse,
        AlphaWithStreamingResponse as AlphaWithStreamingResponse,
        AsyncAlphaWithStreamingResponse as AsyncAlphaWithStreamingResponse,
    )
    from .checkpoints import (
        Checkpoints as Checkpoints,
        AsyncCheckpoints as AsyncCheckpoints,
        CheckpointsWithRawResponse as CheckpointsWithRawResponse,
        AsyncCheckpointsWithRawResponse as AsyncCheckpointsWithRawResponse,
        CheckpointsWithStreamingResponse as CheckpointsWithStreamingResponse,
        AsyncCheckpointsWithStreamingResponse as AsyncCheckpointsWithStreamingResponse,
    )
    from .fine_tuning import (
        FineTuning as FineTuning,
        AsyncFineTuning as AsyncFineTuning,
        FineTuningWithRawResponse as FineTuningWithRawResponse,
        AsyncFineTuningWithRawResponse as AsyncFineTuningWithRawResponse,
        FineTuningWithStreamingResponse as FineTuningWithStreamingResponse,
        AsyncFineTuningWithStreamingResponse as AsyncFineTuningWithStreamingResponse,
    )

else:
    _EXPORTS = {
        "Jobs": (".jobs", "Jobs"),
        "AsyncJobs": (".jobs", "AsyncJobs"),
        "JobsWithRawResponse": (".jobs", "JobsWithRawResponse"),
        "AsyncJobsWithRawResponse": (".jobs", "AsyncJobsWithRawResponse"),
        "JobsWithStreamingResponse": (".jobs", "JobsWithStreamingResponse"),
        "AsyncJobsWithStreamingResponse": (".jobs", "AsyncJobsWithStreamingResponse"),
        "Checkpoints": (".checkpoints", "Checkpoints"),
        "AsyncCheckpoints": (".checkpoints", "AsyncCheckpoints"),
        "CheckpointsWithRawResponse": (".checkpoints", "CheckpointsWithRawResponse"),
        "AsyncCheckpointsWithRawResponse": (".checkpoints", "AsyncCheckpointsWithRawResponse"),
        "CheckpointsWithStreamingResponse": (".checkpoints", "CheckpointsWithStreamingResponse"),
        "AsyncCheckpointsWithStreamingResponse": (".checkpoints", "AsyncCheckpointsWithStreamingResponse"),
        "Alpha": (".alpha", "Alpha"),
        "AsyncAlpha": (".alpha", "AsyncAlpha"),
        "AlphaWithRawResponse": (".alpha", "AlphaWithRawResponse"),
        "AsyncAlphaWithRawResponse": (".alpha", "AsyncAlphaWithRawResponse"),
        "AlphaWithStreamingResponse": (".alpha", "AlphaWithStreamingResponse"),
        "AsyncAlphaWithStreamingResponse": (".alpha", "AsyncAlphaWithStreamingResponse"),
        "FineTuning": (".fine_tuning", "FineTuning"),
        "AsyncFineTuning": (".fine_tuning", "AsyncFineTuning"),
        "FineTuningWithRawResponse": (".fine_tuning", "FineTuningWithRawResponse"),
        "AsyncFineTuningWithRawResponse": (".fine_tuning", "AsyncFineTuningWithRawResponse"),
        "FineTuningWithStreamingResponse": (".fine_tuning", "FineTuningWithStreamingResponse"),
        "AsyncFineTuningWithStreamingResponse": (".fine_tuning", "AsyncFineTuningWithStreamingResponse"),
    }
    _SUBMODULES = {
        "alpha",
        "checkpoints",
        "fine_tuning",
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
    "Jobs",
    "AsyncJobs",
    "JobsWithRawResponse",
    "AsyncJobsWithRawResponse",
    "JobsWithStreamingResponse",
    "AsyncJobsWithStreamingResponse",
    "Checkpoints",
    "AsyncCheckpoints",
    "CheckpointsWithRawResponse",
    "AsyncCheckpointsWithRawResponse",
    "CheckpointsWithStreamingResponse",
    "AsyncCheckpointsWithStreamingResponse",
    "Alpha",
    "AsyncAlpha",
    "AlphaWithRawResponse",
    "AsyncAlphaWithRawResponse",
    "AlphaWithStreamingResponse",
    "AsyncAlphaWithStreamingResponse",
    "FineTuning",
    "AsyncFineTuning",
    "FineTuningWithRawResponse",
    "AsyncFineTuningWithRawResponse",
    "FineTuningWithStreamingResponse",
    "AsyncFineTuningWithStreamingResponse",
]
