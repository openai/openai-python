# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["VideoGetCharacterResponse"]


class VideoGetCharacterResponse(BaseModel):
    id: Optional[str] = None
    """Identifier for the character creation cameo."""

    created_at: int
    """Unix timestamp (in seconds) when the character was created."""

    name: Optional[str] = None
    """Display name for the character."""
