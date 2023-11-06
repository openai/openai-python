# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["ImageGenerateParams"]


class ImageGenerateParams(TypedDict, total=False):
    prompt: Required[str]
    """A text description of the desired image(s).

    The maximum length is 1000 characters.
    """

    n: Optional[int]
    """The number of images to generate. Must be between 1 and 10."""

    response_format: Optional[Literal["url", "b64_json"]]
    """The format in which the generated images are returned.

    Must be one of `url` or `b64_json`.
    """

    size: Optional[Literal["256x256", "512x512", "1024x1024"]]
    """The size of the generated images.

    Must be one of `256x256`, `512x512`, or `1024x1024`.
    """

    user: str
    """
    A unique identifier representing your end-user, which can help OpenAI to monitor
    and detect abuse.
    [Learn more](https://platform.openai.com/docs/guides/safety-best-practices/end-user-ids).
    """
