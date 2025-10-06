# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from ..._types import FileTypes

__all__ = ["ChatKitUploadFileParams"]


class ChatKitUploadFileParams(TypedDict, total=False):
    file: Required[FileTypes]
    """Binary file contents to store with the ChatKit session.

    Supports PDFs and PNG, JPG, JPEG, GIF, or WEBP images.
    """
