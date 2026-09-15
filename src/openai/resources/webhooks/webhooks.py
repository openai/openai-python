# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import json
from typing import cast

from ..._types import HeadersLike
from ..._models import construct_type
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._exceptions import InvalidWebhookSignatureError
from ...lib._webhooks import webhook_signature_matches as _webhook_signature_matches
from ...types.webhooks.unwrap_webhook_event import UnwrapWebhookEvent

__all__ = ["Webhooks", "AsyncWebhooks"]


class Webhooks(SyncAPIResource):
    def unwrap(
        self,
        payload: str | bytes,
        headers: HeadersLike,
        *,
        secret: str | None = None,
    ) -> UnwrapWebhookEvent:
        """Validates that the given payload was sent by OpenAI and parses the payload."""
        if secret is None:
            secret = self._client.webhook_secret

        self.verify_signature(payload=payload, headers=headers, secret=secret)

        return cast(
            UnwrapWebhookEvent,
            construct_type(
                type_=UnwrapWebhookEvent,
                value=json.loads(payload),
            ),
        )

    def verify_signature(
        self,
        payload: str | bytes,
        headers: HeadersLike,
        *,
        secret: str | None = None,
        tolerance: int = 300,
    ) -> None:
        """Validates whether or not the webhook payload was sent by OpenAI.

        Args:
            payload: The webhook payload
            headers: The webhook headers
            secret: The webhook secret (optional, will use client secret if not provided)
            tolerance: Maximum age of the webhook in seconds (default: 300 = 5 minutes)
        """
        if secret is None:
            secret = self._client.webhook_secret

        if secret is None:
            raise ValueError(
                "The webhook secret must either be set using the env var, OPENAI_WEBHOOK_SECRET, "
                "on the client class, OpenAI(webhook_secret='123'), or passed to this function"
            )

        if not _webhook_signature_matches(payload, headers, secret=secret, tolerance=tolerance):
            raise InvalidWebhookSignatureError(
                "The given webhook signature does not match the expected signature"
            ) from None


class AsyncWebhooks(AsyncAPIResource):
    def unwrap(
        self,
        payload: str | bytes,
        headers: HeadersLike,
        *,
        secret: str | None = None,
    ) -> UnwrapWebhookEvent:
        """Validates that the given payload was sent by OpenAI and parses the payload."""
        if secret is None:
            secret = self._client.webhook_secret

        self.verify_signature(payload=payload, headers=headers, secret=secret)

        body = payload.decode("utf-8") if isinstance(payload, bytes) else payload
        return cast(
            UnwrapWebhookEvent,
            construct_type(
                type_=UnwrapWebhookEvent,
                value=json.loads(body),
            ),
        )

    def verify_signature(
        self,
        payload: str | bytes,
        headers: HeadersLike,
        *,
        secret: str | None = None,
        tolerance: int = 300,
    ) -> None:
        """Validates whether or not the webhook payload was sent by OpenAI.

        Args:
            payload: The webhook payload
            headers: The webhook headers
            secret: The webhook secret (optional, will use client secret if not provided)
            tolerance: Maximum age of the webhook in seconds (default: 300 = 5 minutes)
        """
        if secret is None:
            secret = self._client.webhook_secret

        if secret is None:
            raise ValueError(
                "The webhook secret must either be set using the env var, OPENAI_WEBHOOK_SECRET, "
                "on the client class, OpenAI(webhook_secret='123'), or passed to this function"
            ) from None

        if not _webhook_signature_matches(payload, headers, secret=secret, tolerance=tolerance):
            raise InvalidWebhookSignatureError("The given webhook signature does not match the expected signature")
