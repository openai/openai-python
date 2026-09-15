from __future__ import annotations

import runpy
from typing import Callable, cast
from pathlib import Path

import pytest

_render_readme = cast(
    Callable[[str], str],
    runpy.run_path(str(Path(__file__).parents[1] / "scripts" / "hatch_metadata.py"))["render_readme"],
)


@pytest.mark.parametrize(
    "text,expected",
    [
        ("[Guide](CONTRIBUTING.md)", "[Guide](https://github.com/openai/openai-python/tree/main/CONTRIBUTING.md)"),
        (
            "[Example](examples/demo.py#usage)",
            "[Example](https://github.com/openai/openai-python/tree/main/examples/demo.py#usage)",
        ),
        ("[Docs](https://example.com/docs)", "[Docs](https://example.com/docs)"),
        ("[Docs](http://example.com/docs)", "[Docs](http://example.com/docs)"),
        ("Plain text — no links", "Plain text — no links"),
    ],
)
def test_readme_link_rewriting(text: str, expected: str) -> None:
    assert _render_readme(text) == expected
