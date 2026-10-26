# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from ..._models import BaseModel
from .realtime_translation_session import RealtimeTranslationSession

__all__ = ["RealtimeTranslationClientSecretCreateResponse"]


class RealtimeTranslationClientSecretCreateResponse(BaseModel):
    """
    Response from creating a translation session and client secret for the Realtime API.
    """

    expires_at: int
    """Expiration timestamp for the client secret, in seconds since epoch."""

    session: RealtimeTranslationSession
    """A Realtime translation session.

    Translation sessions continuously translate input audio into the configured
    output language.
    """

    value: str
    """The generated client secret value."""
