# File generated from our OpenAPI spec by Stainless.

from .._models import BaseModel

__all__ = ["FineTuneEvent"]


class FineTuneEvent(BaseModel):
    created_at: int

    level: str

    message: str

    object: str
