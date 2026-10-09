# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["DecisionInputImageParam"]


class DecisionInputImageParam(TypedDict, total=False):
    """An inline image. External URLs and file IDs are not supported."""

    image_url: Required[str]
    """A base64-encoded image in a data URL."""

    type: Required[Literal["input_image"]]

    detail: Optional[Literal["low", "high", "auto", "original"]]
    """The image detail level, using the selected model's image profile.

    Defaults to auto.
    """
