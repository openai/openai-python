from __future__ import annotations

import hmac
import base64
import hashlib
import binascii
from typing import Iterator, cast
from unittest import mock

import pytest

import openai
from openai._exceptions import InvalidWebhookSignatureError
from openai.lib._webhooks import webhook_signature_matches
from openai.resources.webhooks.webhooks import Webhooks, AsyncWebhooks

NOW = 1_750_000_000
PAYLOAD = '{"synthetic": "café"}'
WEBHOOK_ID = "evt_synthetic"
RAW_SECRET = "synthetic-webhook-secret"
PREFIXED_SECRET = "whsec_" + base64.b64encode(RAW_SECRET.encode()).decode()


def signed_headers(
    payload: str | bytes = PAYLOAD,
    *,
    timestamp: str = str(NOW),
    secret: bytes = RAW_SECRET.encode(),
) -> dict[str, str]:
    body = payload.encode() if isinstance(payload, str) else payload
    signed = f"{WEBHOOK_ID}.{timestamp}.".encode() + body
    signature = base64.b64encode(hmac.new(secret, signed, hashlib.sha256).digest()).decode()
    return {
        "webhook-id": WEBHOOK_ID,
        "webhook-timestamp": timestamp,
        "webhook-signature": f"v1,{signature}",
    }


@pytest.fixture(autouse=True)
def frozen_time() -> Iterator[None]:
    with mock.patch("time.time", return_value=NOW):
        yield


@pytest.fixture(params=["sync", "async"])
def webhook_resource(request: pytest.FixtureRequest) -> Webhooks | AsyncWebhooks:
    client = mock.Mock()
    client.webhook_secret = None
    if request.param == "sync":
        return Webhooks(cast(openai.OpenAI, client))
    return AsyncWebhooks(cast(openai.AsyncOpenAI, client))


@pytest.mark.parametrize(
    ("secret", "key"),
    [(RAW_SECRET, RAW_SECRET.encode()), (PREFIXED_SECRET, RAW_SECRET.encode()), ("", b"")],
    ids=["raw", "prefixed", "empty"],
)
@pytest.mark.parametrize("payload", [PAYLOAD, PAYLOAD.encode()], ids=["text", "bytes"])
@pytest.mark.parametrize("signature_form", ["prefixed", "bare", "multiple"])
def test_signature_forms_and_secret_encodings(
    webhook_resource: Webhooks | AsyncWebhooks,
    secret: str,
    key: bytes,
    payload: str | bytes,
    signature_form: str,
) -> None:
    headers = signed_headers(payload, secret=key)
    signature = headers["webhook-signature"][3:]
    if signature_form == "bare":
        headers["webhook-signature"] = signature
    elif signature_form == "multiple":
        headers["webhook-signature"] = f"v1,invalid\t{signature} v1,also-invalid"
    headers = {name.upper(): value for name, value in headers.items()}

    assert webhook_signature_matches(payload, headers, secret=secret, tolerance=300)
    assert webhook_resource.verify_signature(payload, headers, secret=secret) is None


@pytest.mark.parametrize(
    ("delta", "tolerance", "error"),
    [
        (0, 0, None),
        (-300, 300, None),
        (300, 300, None),
        (-301, 300, "Webhook timestamp is too old"),
        (301, 300, "Webhook timestamp is too new"),
        (-1, 0, "Webhook timestamp is too old"),
        (1, 0, "Webhook timestamp is too new"),
        (0, -1, "Webhook timestamp is too old"),
    ],
)
def test_replay_window_boundaries(
    webhook_resource: Webhooks | AsyncWebhooks,
    delta: int,
    tolerance: int,
    error: str | None,
) -> None:
    headers = signed_headers(timestamp=str(NOW + delta))
    if error is None:
        webhook_resource.verify_signature(PAYLOAD, headers, secret=RAW_SECRET, tolerance=tolerance)
    else:
        with pytest.raises(InvalidWebhookSignatureError, match=error) as caught:
            webhook_resource.verify_signature(PAYLOAD, headers, secret=RAW_SECRET, tolerance=tolerance)
        assert caught.value.__cause__ is None
        assert caught.value.__suppress_context__


@pytest.mark.parametrize("timestamp", [f"0{NOW}", f"+{NOW}", f" {NOW} "])
def test_signature_uses_original_timestamp_text(webhook_resource: Webhooks | AsyncWebhooks, timestamp: str) -> None:
    webhook_resource.verify_signature(PAYLOAD, signed_headers(timestamp=timestamp), secret=RAW_SECRET)


@pytest.mark.parametrize("timestamp", ["", "not-a-timestamp", "1.5"])
def test_invalid_timestamp_exception(webhook_resource: Webhooks | AsyncWebhooks, timestamp: str) -> None:
    with pytest.raises(InvalidWebhookSignatureError, match="Invalid webhook timestamp format") as caught:
        webhook_resource.verify_signature(PAYLOAD, signed_headers(timestamp=timestamp), secret=RAW_SECRET)
    assert caught.value.__cause__ is None
    assert caught.value.__suppress_context__


@pytest.mark.parametrize(
    ("headers", "missing"),
    [
        ({}, "webhook-signature"),
        ({"webhook-signature": "invalid"}, "webhook-timestamp"),
        ({"webhook-signature": "invalid", "webhook-timestamp": str(NOW)}, "webhook-id"),
    ],
)
def test_required_header_order(
    webhook_resource: Webhooks | AsyncWebhooks, headers: dict[str, str], missing: str
) -> None:
    with pytest.raises(ValueError, match=f"Could not find {missing} header"):
        webhook_resource.verify_signature(PAYLOAD, headers, secret=RAW_SECRET)


def test_client_secret_fallback_preserves_explicit_empty_secret(
    webhook_resource: Webhooks | AsyncWebhooks,
) -> None:
    webhook_resource._client.webhook_secret = PREFIXED_SECRET
    webhook_resource.verify_signature(PAYLOAD, signed_headers())
    webhook_resource.verify_signature(PAYLOAD, signed_headers(secret=b""), secret="")


def test_missing_secret_preserves_wrapper_exception_chaining(
    webhook_resource: Webhooks | AsyncWebhooks,
) -> None:
    previous = RuntimeError("synthetic prior failure")
    try:
        raise previous
    except RuntimeError:
        with pytest.raises(ValueError, match="The webhook secret must either be set") as caught:
            webhook_resource.verify_signature(PAYLOAD, {})

    assert caught.value.__context__ is previous
    assert caught.value.__cause__ is None
    assert caught.value.__suppress_context__ is isinstance(webhook_resource, AsyncWebhooks)


def test_mismatch_preserves_wrapper_exception_chaining(
    webhook_resource: Webhooks | AsyncWebhooks,
) -> None:
    headers = signed_headers()
    headers["webhook-signature"] = "v1,synthetic-invalid-signature"
    previous = RuntimeError("synthetic prior failure")
    try:
        raise previous
    except RuntimeError:
        with pytest.raises(InvalidWebhookSignatureError, match="does not match the expected signature") as caught:
            webhook_resource.verify_signature(PAYLOAD, headers, secret=RAW_SECRET)

    assert caught.value.__context__ is previous
    assert caught.value.__cause__ is None
    assert caught.value.__suppress_context__ is (not isinstance(webhook_resource, AsyncWebhooks))
    assert RAW_SECRET not in str(caught.value)
    assert PAYLOAD not in str(caught.value)
    assert headers["webhook-signature"] not in str(caught.value)


def test_malformed_secret_keeps_base64_error(webhook_resource: Webhooks | AsyncWebhooks) -> None:
    with pytest.raises(binascii.Error):
        webhook_resource.verify_signature(PAYLOAD, signed_headers(), secret="whsec_a")


def test_invalid_utf8_payload_keeps_decode_error(webhook_resource: Webhooks | AsyncWebhooks) -> None:
    with pytest.raises(UnicodeDecodeError):
        webhook_resource.verify_signature(b"\xff", signed_headers(), secret=RAW_SECRET)


def test_non_ascii_signature_keeps_compare_error(webhook_resource: Webhooks | AsyncWebhooks) -> None:
    headers = signed_headers()
    headers["webhook-signature"] = "v1,é"
    with pytest.raises(TypeError, match="non-ASCII"):
        webhook_resource.verify_signature(PAYLOAD, headers, secret=RAW_SECRET)


def test_constant_time_comparison_order(webhook_resource: Webhooks | AsyncWebhooks) -> None:
    headers = signed_headers()
    expected = headers["webhook-signature"][3:]
    headers["webhook-signature"] = f"v1,invalid v1,{expected} v1,unused"
    with mock.patch("openai.lib._webhooks.hmac.compare_digest", wraps=hmac.compare_digest) as compare:
        webhook_resource.verify_signature(PAYLOAD, headers, secret=RAW_SECRET)
    assert compare.call_args_list == [mock.call(expected, "invalid"), mock.call(expected, expected)]


@pytest.mark.parametrize("signature", ["", "v1,invalid", "invalid v1,also-invalid"])
def test_helper_returns_false_for_mismatch(signature: str) -> None:
    headers = signed_headers()
    headers["webhook-signature"] = signature
    assert not webhook_signature_matches(PAYLOAD, headers, secret=RAW_SECRET, tolerance=300)
