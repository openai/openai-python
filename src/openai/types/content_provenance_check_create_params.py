# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .._types import FileTypes

__all__ = ["ContentProvenanceCheckCreateParams"]


class ContentProvenanceCheckCreateParams(TypedDict, total=False):
    file: Required[FileTypes]
    """The image or audio file to check for supported OpenAI provenance signals."""
