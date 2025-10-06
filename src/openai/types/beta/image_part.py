# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ImagePart"]


class ImagePart(BaseModel):
    id: str
    """Unique identifier for the uploaded image."""

    mime_type: str
    """MIME type of the uploaded image."""

    name: Optional[str] = None
    """Original filename for the uploaded image. Defaults to null when unnamed."""

    preview_url: str
    """Preview URL that can be rendered inline for the image."""

    type: Literal["image"]
    """Type discriminator that is always `image`."""

    upload_url: Optional[str] = None
    """Signed URL for downloading the uploaded image.

    Defaults to null when no download link is available.
    """
