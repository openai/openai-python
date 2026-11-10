# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["VoiceDeleted"]


class VoiceDeleted(BaseModel):
    id: str
    """The voice identifier."""

    deleted: bool
    """Whether the voice was deleted."""

    object: Literal["audio.voice.deleted"]
    """The object type, which is always `audio.voice.deleted`."""
