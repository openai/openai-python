# File generated from our OpenAPI spec by Stainless.

from .._models import BaseModel

__all__ = ["Model"]


class Model(BaseModel):
    id: str
    """The model identifier, which can be referenced in the API endpoints."""

    created: int
    """The Unix timestamp (in seconds) when the model was created."""

    object: str
    """The object type, which is always "model"."""

    owned_by: str
    """The organization that owns the model."""
