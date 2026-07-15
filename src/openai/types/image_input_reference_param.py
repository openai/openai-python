# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ImageInputReferenceParam"]


class ImageInputReferenceParam(TypedDict, total=False):
    file_id: str

    image_url: str
    """A fully qualified URL or base64-encoded data URL."""
