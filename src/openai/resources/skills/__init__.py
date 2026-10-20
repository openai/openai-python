# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

import typing as _t

if _t.TYPE_CHECKING:
    from .skills import (
        Skills as Skills,
        AsyncSkills as AsyncSkills,
        SkillsWithRawResponse as SkillsWithRawResponse,
        AsyncSkillsWithRawResponse as AsyncSkillsWithRawResponse,
        SkillsWithStreamingResponse as SkillsWithStreamingResponse,
        AsyncSkillsWithStreamingResponse as AsyncSkillsWithStreamingResponse,
    )
    from .content import (
        Content as Content,
        AsyncContent as AsyncContent,
        ContentWithRawResponse as ContentWithRawResponse,
        AsyncContentWithRawResponse as AsyncContentWithRawResponse,
        ContentWithStreamingResponse as ContentWithStreamingResponse,
        AsyncContentWithStreamingResponse as AsyncContentWithStreamingResponse,
    )
    from .versions import (
        Versions as Versions,
        AsyncVersions as AsyncVersions,
        VersionsWithRawResponse as VersionsWithRawResponse,
        AsyncVersionsWithRawResponse as AsyncVersionsWithRawResponse,
        VersionsWithStreamingResponse as VersionsWithStreamingResponse,
        AsyncVersionsWithStreamingResponse as AsyncVersionsWithStreamingResponse,
    )

else:
    _EXPORTS = {
        "Content": (".content", "Content"),
        "AsyncContent": (".content", "AsyncContent"),
        "ContentWithRawResponse": (".content", "ContentWithRawResponse"),
        "AsyncContentWithRawResponse": (".content", "AsyncContentWithRawResponse"),
        "ContentWithStreamingResponse": (".content", "ContentWithStreamingResponse"),
        "AsyncContentWithStreamingResponse": (".content", "AsyncContentWithStreamingResponse"),
        "Versions": (".versions", "Versions"),
        "AsyncVersions": (".versions", "AsyncVersions"),
        "VersionsWithRawResponse": (".versions", "VersionsWithRawResponse"),
        "AsyncVersionsWithRawResponse": (".versions", "AsyncVersionsWithRawResponse"),
        "VersionsWithStreamingResponse": (".versions", "VersionsWithStreamingResponse"),
        "AsyncVersionsWithStreamingResponse": (".versions", "AsyncVersionsWithStreamingResponse"),
        "Skills": (".skills", "Skills"),
        "AsyncSkills": (".skills", "AsyncSkills"),
        "SkillsWithRawResponse": (".skills", "SkillsWithRawResponse"),
        "AsyncSkillsWithRawResponse": (".skills", "AsyncSkillsWithRawResponse"),
        "SkillsWithStreamingResponse": (".skills", "SkillsWithStreamingResponse"),
        "AsyncSkillsWithStreamingResponse": (".skills", "AsyncSkillsWithStreamingResponse"),
    }
    _SUBMODULES = {
        "content",
        "skills",
        "versions",
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
    "Versions",
    "AsyncVersions",
    "VersionsWithRawResponse",
    "AsyncVersionsWithRawResponse",
    "VersionsWithStreamingResponse",
    "AsyncVersionsWithStreamingResponse",
    "Skills",
    "AsyncSkills",
    "SkillsWithRawResponse",
    "AsyncSkillsWithRawResponse",
    "SkillsWithStreamingResponse",
    "AsyncSkillsWithStreamingResponse",
]
