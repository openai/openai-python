# File generated from our OpenAPI spec by Stainless.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["AsssitantDeleted"]


class AsssitantDeleted(BaseModel):
    id: str

    deleted: bool

    object: Literal["assistant.deleted"]
