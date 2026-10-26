# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

from ..realtime_translation_session_create_request_param import RealtimeTranslationSessionCreateRequestParam

__all__ = ["ClientSecretCreateParams", "ExpiresAfter"]


class ClientSecretCreateParams(TypedDict, total=False):
    session: Required[RealtimeTranslationSessionCreateRequestParam]
    """Realtime translation session configuration.

    Translation sessions stream source audio in and translated audio plus transcript
    deltas out continuously.
    """

    expires_after: ExpiresAfter
    """Configuration for the client secret expiration.

    Expiration refers to the time after which a client secret will no longer be
    valid for creating sessions. The session itself may continue after that time
    once started. A secret can be used to create multiple sessions until it expires.
    """


class ExpiresAfter(TypedDict, total=False):
    """Configuration for the client secret expiration.

    Expiration refers to the time after which
    a client secret will no longer be valid for creating sessions. The session itself may
    continue after that time once started. A secret can be used to create multiple sessions
    until it expires.
    """

    anchor: Literal["created_at"]
    """
    The anchor point for the client secret expiration, meaning that `seconds` will
    be added to the `created_at` time of the client secret to produce an expiration
    timestamp. Only `created_at` is currently supported.
    """

    seconds: int
    """The number of seconds from the anchor point to the expiration.

    Select a value between `10` and `7200` (2 hours). This default to 600 seconds
    (10 minutes) if not specified.
    """
