# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Required, TypeAlias, TypedDict

from .._types import FileTypes
from .video_size import VideoSize
from .video_seconds import VideoSeconds
from .video_model_param import VideoModelParam

__all__ = ["VideoCreateParams", "InputReference", "InputReferenceImageRefParam2"]


class VideoCreateParams(TypedDict, total=False):
    prompt: Required[str]
    """Text prompt that describes the video to generate."""

    input_reference: InputReference
    """Optional reference asset upload or reference object that guides generation."""

    model: VideoModelParam
    """The video generation model to use (allowed values: sora-2, sora-2-pro).

    Defaults to `sora-2`.
    """

    seconds: VideoSeconds
    """Clip duration in seconds (allowed values: 4, 8, 12). Defaults to 4 seconds."""

    size: VideoSize
    """
    Output resolution formatted as width x height (allowed values: 720x1280,
    1280x720, 1024x1792, 1792x1024). Defaults to 720x1280.
    """


class InputReferenceImageRefParam2(TypedDict, total=False):
    file_id: str

    image_url: str
    """A fully qualified URL or base64-encoded data URL."""


InputReference: TypeAlias = Union[FileTypes, InputReferenceImageRefParam2]
