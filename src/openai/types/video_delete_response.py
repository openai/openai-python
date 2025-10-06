# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["VideoDeleteResponse"]


class VideoDeleteResponse(BaseModel):
    id: str
    """Identifier of the deleted video."""

    deleted: bool
    """Indicates that the video resource was deleted."""

    object: Literal["video.deleted"]
    """The object type that signals the deletion response."""
