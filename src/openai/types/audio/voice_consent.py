# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["VoiceConsent"]


class VoiceConsent(BaseModel):
    """A consent recording used to authorize creation of a custom voice."""

    id: str
    """The consent recording identifier."""

    created_at: int
    """The Unix timestamp (in seconds) for when the consent recording was created."""

    language: str
    """The BCP 47 language tag for the consent phrase (for example, `en-US`)."""

    name: str
    """The label provided when the consent recording was uploaded."""

    object: Literal["audio.voice_consent"]
    """The object type, which is always `audio.voice_consent`."""
