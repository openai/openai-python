from __future__ import annotations

import hmac
import time
import base64
import hashlib

from .._types import HeadersLike
from .._utils import get_required_header
from .._exceptions import InvalidWebhookSignatureError


def webhook_signature_matches(
    payload: str | bytes,
    headers: HeadersLike,
    *,
    secret: str,
    tolerance: int,
) -> bool:
    """Validate the replay window and compare the supplied signatures."""
    signature_header = get_required_header(headers, "webhook-signature")
    timestamp = get_required_header(headers, "webhook-timestamp")
    webhook_id = get_required_header(headers, "webhook-id")

    # Validate timestamp to prevent replay attacks
    try:
        timestamp_seconds = int(timestamp)
    except ValueError:
        raise InvalidWebhookSignatureError("Invalid webhook timestamp format") from None

    now = int(time.time())

    if now - timestamp_seconds > tolerance:
        raise InvalidWebhookSignatureError("Webhook timestamp is too old") from None

    if timestamp_seconds > now + tolerance:
        raise InvalidWebhookSignatureError("Webhook timestamp is too new") from None

    # Extract signatures from v1,<base64> format
    # The signature header can have multiple values, separated by spaces.
    # Each value is in the format v1,<base64>. We should accept if any match.
    signatures: list[str] = []
    for part in signature_header.split():
        if part.startswith("v1,"):
            signatures.append(part[3:])
        else:
            signatures.append(part)

    # Decode the secret if it starts with whsec_
    if secret.startswith("whsec_"):
        decoded_secret = base64.b64decode(secret[6:])
    else:
        decoded_secret = secret.encode()

    body = payload.decode("utf-8") if isinstance(payload, bytes) else payload

    # Prepare the signed payload (OpenAI uses webhookId.timestamp.payload format)
    signed_payload = f"{webhook_id}.{timestamp}.{body}"
    expected_signature = base64.b64encode(
        hmac.new(decoded_secret, signed_payload.encode(), hashlib.sha256).digest()
    ).decode()

    # Accept if any signature matches
    return any(hmac.compare_digest(expected_signature, sig) for sig in signatures)
