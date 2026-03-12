# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["VideoEditParams", "Video"]


class VideoEditParams(TypedDict, total=False):
    prompt: Required[str]
    """Text prompt that describes how to edit the source video."""

    video: Required[Video]
    """Reference to the completed video to edit."""


class Video(TypedDict, total=False):
    """Reference to the completed video to edit."""

    id: Required[str]
    """The identifier of the completed video."""
