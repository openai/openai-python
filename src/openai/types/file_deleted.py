# File generated from our OpenAPI spec by Stainless.

from .._models import BaseModel

__all__ = ["FileDeleted"]


class FileDeleted(BaseModel):
    id: str

    deleted: bool

    object: str
