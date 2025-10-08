# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["FilePart"]


class FilePart(BaseModel):
    id: str
    """Unique identifier for the uploaded file."""

    mime_type: Optional[str] = None
    """MIME type reported for the uploaded file. Defaults to null when unknown."""

    name: Optional[str] = None
    """Original filename supplied by the uploader. Defaults to null when unnamed."""

    type: Literal["file"]
    """Type discriminator that is always `file`."""

    upload_url: Optional[str] = None
    """Signed URL for downloading the uploaded file.

    Defaults to null when no download link is available.
    """
