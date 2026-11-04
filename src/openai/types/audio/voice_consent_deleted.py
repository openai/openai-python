# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["VoiceConsentDeleted"]


class VoiceConsentDeleted(BaseModel):
    id: str
    """The consent recording identifier."""

    deleted: bool

    object: Literal["audio.voice_consent"]
