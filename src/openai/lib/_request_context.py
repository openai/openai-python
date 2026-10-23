from __future__ import annotations

from dataclasses import dataclass

from .._types import PostParser


@dataclass(frozen=True)
class PreparedRequestContext:
    """Runtime preparation consumed by a generated HTTP request facade."""

    body: object
    post_parser: PostParser
