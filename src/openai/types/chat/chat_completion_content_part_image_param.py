# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["ChatCompletionContentPartImageParam", "ImageURL"]


class ImageURL(TypedDict, total=False):
    detail: Literal["auto", "low", "high"]
    """Specifies the detail level of the image."""

    url: str
    """Either a URL of the image or the base64 encoded image data."""


class ChatCompletionContentPartImageParam(TypedDict, total=False):
    image_url: Required[ImageURL]

    type: Required[Literal["image_url"]]
    """The type of the content part."""
