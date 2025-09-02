# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, TypeAlias, TypedDict

from .realtime_session_create_request_param import RealtimeSessionCreateRequestParam
from .realtime_transcription_session_create_request_param import RealtimeTranscriptionSessionCreateRequestParam

__all__ = ["ClientSecretCreateParams", "ExpiresAfter", "Session"]


class ClientSecretCreateParams(TypedDict, total=False):
    expires_after: ExpiresAfter
    """Configuration for the ephemeral token expiration."""

    session: Session
    """Session configuration to use for the client secret.

    Choose either a realtime session or a transcription session.
    """


class ExpiresAfter(TypedDict, total=False):
    anchor: Literal["created_at"]
    """The anchor point for the ephemeral token expiration.

    Only `created_at` is currently supported.
    """

    seconds: int
    """The number of seconds from the anchor point to the expiration.

    Select a value between `10` and `7200`.
    """


Session: TypeAlias = Union[RealtimeSessionCreateRequestParam, RealtimeTranscriptionSessionCreateRequestParam]
