# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = ["EvalJSONLFileContentSourceParam", "Content"]


class Content(TypedDict, total=False):
    item: Required[Dict[str, object]]

    sample: Dict[str, object]


class EvalJSONLFileContentSourceParam(TypedDict, total=False):
    content: Required[Iterable[Content]]
    """The content of the jsonl file."""

    type: Required[Literal["file_content"]]
    """The type of jsonl source. Always `file_content`."""
