# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["WebhookRotateSecretParams"]


class WebhookRotateSecretParams(TypedDict, total=False):
    keep_old_secret_active_for_24_hours: bool
    """Whether to keep the previous signing secret valid for 24 hours after rotation.

    Defaults to false, which invalidates the previous secret immediately.
    """
