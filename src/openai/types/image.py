# File generated from our OpenAPI spec by Stainless.

from typing import Optional

from .._models import BaseModel

__all__ = ["Image"]


class Image(BaseModel):
    b64_json: Optional[str] = None
    """
    The base64-encoded JSON of the generated image, if `response_format` is
    `b64_json`.
    """

    url: Optional[str] = None
    """The URL of the generated image, if `response_format` is `url` (default)."""
