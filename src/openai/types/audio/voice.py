# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["Voice"]


class Voice(BaseModel):
    """A custom voice that can be used for audio output."""

    id: str
    """The voice identifier, which can be referenced in API endpoints."""

    created_at: int
    """The Unix timestamp (in seconds) for when the voice was created."""

    name: str
    """The name of the voice."""

    object: Literal["audio.voice"]
    """The object type, which is always `audio.voice`."""

    type: Literal["audio_sample"]
    """How the voice was created."""
