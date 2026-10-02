# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["ModelDeleted"]


class ModelDeleted(BaseModel):
    id: str

    deleted: bool

    object: str
