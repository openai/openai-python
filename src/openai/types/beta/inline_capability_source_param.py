# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["InlineCapabilitySourceParam"]


class InlineCapabilitySourceParam(TypedDict, total=False):
    """Provides ZIP bytes encoded with standard base64."""

    data: Required[str]
    """Standard-base64 encoded ZIP archive bytes."""

    media_type: Required[Literal["application/zip"]]
    """The archive media type, always `application/zip`.

    - `application/zip` - A ZIP archive.
    """

    type: Required[Literal["base64"]]
    """The type of the object. Always `base64`."""
