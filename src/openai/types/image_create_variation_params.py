# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from typing_extensions import Literal, Required, TypedDict

from .._types import FileTypes
from .image_model import ImageModel

__all__ = ["ImageCreateVariationParams"]


class ImageCreateVariationParams(TypedDict, total=False):
    image: Required[FileTypes]
    """The input image for the legacy variations endpoint.

    The legacy format requires a valid PNG file, less than 4MB, and square.
    """

    model: Union[str, ImageModel, None]
    """
    Legacy model selection for the variations endpoint, which was designed for
    `dall-e-2`. DALL·E 2 was retired from the API on May 12, 2026; see
    [deprecations](https://developers.openai.com/api/docs/deprecations). Use image
    edits with a supported GPT Image model for new integrations.
    """

    n: Optional[int]
    """The number of images requested from the legacy variations endpoint.

    Must be between 1 and 10.
    """

    response_format: Optional[Literal["url", "b64_json"]]
    """The response format for the legacy variations endpoint: `url` or `b64_json`.

    Returned URLs were valid for 60 minutes after image generation.
    """

    size: Optional[Literal["256x256", "512x512", "1024x1024"]]
    """The requested image size for the legacy variations endpoint.

    Must be one of `256x256`, `512x512`, or `1024x1024`.
    """

    user: str
    """
    A unique identifier representing your end-user, which can help OpenAI to monitor
    and detect abuse.
    [Learn more](https://developers.openai.com/api/docs/guides/safety-best-practices#implement-safety-identifiers).
    """
