"""Prepare the package README without importing the SDK or extra build plugins."""

from __future__ import annotations

import re
from typing import Any
from pathlib import Path


def render_readme(text: str) -> str:
    # Preserve the relative-link rewrite previously configured in pyproject.toml.
    return re.sub(
        r"\[(.+?)\]\(((?!https?://)\S+?)\)",
        r"[\1](https://github.com/openai/openai-python/tree/main/\g<2>)",
        text,
    )


def get_metadata_hook() -> type[Any]:
    # Hatchling is available in the isolated build environment, not at runtime.
    from hatchling.metadata.plugin.interface import MetadataHookInterface

    class ReadmeMetadataHook(MetadataHookInterface):
        def update(self, metadata: dict[str, Any]) -> None:
            text = Path(self.root, "README.md").read_text(encoding="utf-8")
            metadata["readme"] = {"content-type": "text/markdown", "text": render_readme(text)}

    return ReadmeMetadataHook
