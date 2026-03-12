# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Required, TypeAlias, TypedDict

from .._types import FileTypes

__all__ = ["VideoEditParams", "Video", "VideoVideoReferenceInputParam"]


class VideoEditParams(TypedDict, total=False):
    prompt: Required[str]
    """Text prompt that describes how to edit the source video."""

    video: Required[Video]
    """Reference to the completed video to edit."""


class VideoVideoReferenceInputParam(TypedDict, total=False):
    """Reference to the completed video."""

    id: Required[str]
    """The identifier of the completed video."""


Video: TypeAlias = Union[FileTypes, VideoVideoReferenceInputParam]
