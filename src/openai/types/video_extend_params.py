# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Required, TypeAlias, TypedDict

from .._types import FileTypes
from .video_seconds import VideoSeconds

__all__ = ["VideoExtendParams", "Video", "VideoVideoReferenceInputParam"]


class VideoExtendParams(TypedDict, total=False):
    prompt: Required[str]
    """Updated text prompt that directs the extension generation."""

    seconds: Required[VideoSeconds]
    """
    Length of the newly generated extension segment in seconds (allowed values: 4,
    8, 12, 16, 20).
    """

    video: Required[Video]
    """Reference to the completed video to extend."""


class VideoVideoReferenceInputParam(TypedDict, total=False):
    """Reference to the completed video."""

    id: Required[str]
    """The identifier of the completed video."""


Video: TypeAlias = Union[FileTypes, VideoVideoReferenceInputParam]
