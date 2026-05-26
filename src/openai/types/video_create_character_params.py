# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .._types import FileTypes

__all__ = ["VideoCreateCharacterParams"]


class VideoCreateCharacterParams(TypedDict, total=False):
    name: Required[str]
    """Display name for this API character."""

    video: Required[FileTypes]
    """Video file used to create a character."""
