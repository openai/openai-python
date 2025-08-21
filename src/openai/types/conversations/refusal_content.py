# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["RefusalContent"]


class RefusalContent(BaseModel):
    refusal: str
    """The refusal explanation from the model."""

    type: Literal["refusal"]
    """The type of the refusal. Always `refusal`."""
