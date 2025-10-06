# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .._types import FileTypes
from .video_size import VideoSize
from .video_model import VideoModel
from .video_seconds import VideoSeconds

__all__ = ["VideoCreateParams"]


class VideoCreateParams(TypedDict, total=False):
    prompt: Required[str]
    """Text prompt that describes the video to generate."""

    input_reference: FileTypes
    """Optional image reference that guides generation."""

    model: VideoModel
    """The video generation model to use. Defaults to `sora-2`."""

    seconds: VideoSeconds
    """Clip duration in seconds. Defaults to 4 seconds."""

    size: VideoSize
    """Output resolution formatted as width x height. Defaults to 720x1280."""
