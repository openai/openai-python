from __future__ import annotations

import hmac
import time
import base64
import codecs
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

    if not decoded_secret:
        raise ValueError("The webhook secret must not be empty after decoding")

    mac = hmac.new(decoded_secret, f"{webhook_id}.{timestamp}.".encode(), hashlib.sha256)
    chunk_size = 64 * 1024
    if isinstance(payload, bytes):
        # Validate UTF-8 across chunk boundaries while signing the original bytes.
        decoder = codecs.getincrementaldecoder("utf-8")()
        for start in range(0, len(payload), chunk_size):
            chunk = payload[start : start + chunk_size]
            decoder.decode(chunk)
            mac.update(chunk)
        decoder.decode(b"", final=True)
    else:
        for start in range(0, len(payload), chunk_size):
            mac.update(payload[start : start + chunk_size].encode())
    expected_signature = base64.b64encode(mac.digest()).decode()

    # Accept if any signature matches
    return any(hmac.compare_digest(expected_signature, sig) for sig in signatures)
