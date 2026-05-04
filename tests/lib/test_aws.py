"""Unit tests for AwsOpenAI and AsyncAwsOpenAI."""

from __future__ import annotations

from typing import Any, Union
from unittest.mock import MagicMock, patch

import httpx
import pytest

from openai import OpenAI, AsyncOpenAI
from openai.lib.aws import (
    AwsOpenAI,
    AsyncAwsOpenAI,
)
from openai._exceptions import OpenAIError

Client = Union[AwsOpenAI, AsyncAwsOpenAI]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_frozen_creds(
    access_key: str = "AKID",
    secret_key: str = "secret",
    token: str | None = "tok",
) -> MagicMock:
    """Return a mock botocore frozen-credentials object."""
    creds = MagicMock()
    creds.access_key = access_key
    creds.secret_key = secret_key
    creds.token = token
    return creds


def _make_unfrozen_creds(
    access_key: str = "AKID",
    secret_key: str = "secret",
    token: str | None = "tok",
) -> MagicMock:
    """Return a mock unfrozen botocore credentials object with get_frozen_credentials()."""
    frozen = _make_frozen_creds(access_key, secret_key, token)
    creds = MagicMock()
    creds.get_frozen_credentials.return_value = frozen
    creds.access_key = access_key
    creds.secret_key = secret_key
    creds.token = token
    return creds


def _patch_default_creds(unfrozen: MagicMock | None = None) -> Any:
    """Patch _get_default_credentials to return an unfrozen credentials mock."""
    if unfrozen is None:
        unfrozen = _make_unfrozen_creds()
    return patch("openai.lib.aws._get_default_credentials", return_value=unfrozen)


def _patch_ensure_botocore() -> Any:
    """Patch _ensure_botocore so it never raises."""
    return patch("openai.lib.aws._ensure_botocore")


# ---------------------------------------------------------------------------
# Constructor: region-derived base_url (Req 1.1, 2.1)
# ---------------------------------------------------------------------------


class TestConstructorWithRegionDerivedUrl:
    def test_sync_base_url_from_region(self) -> None:
        with _patch_default_creds():
            client = AwsOpenAI(region="us-west-2")
        assert str(client.base_url) == "https://bedrock-mantle.us-west-2.api.aws/v1/"

    def test_async_base_url_from_region(self) -> None:
        with _patch_default_creds():
            client = AsyncAwsOpenAI(region="us-east-1")
        assert str(client.base_url) == "https://bedrock-mantle.us-east-1.api.aws/v1/"


# ---------------------------------------------------------------------------
# Constructor: explicit base_url (Req 1.2, 2.2)
# ---------------------------------------------------------------------------


class TestConstructorWithBaseUrl:
    def test_sync_uses_provided_base_url(self) -> None:
        with _patch_default_creds():
            client = AwsOpenAI(
                base_url="https://custom.example.com/v1",
                region="us-west-2",
            )
        assert str(client.base_url) == "https://custom.example.com/v1/"

    def test_async_uses_provided_base_url(self) -> None:
        with _patch_default_creds():
            client = AsyncAwsOpenAI(
                base_url="https://custom.example.com/v1",
                region="us-west-2",
            )
        assert str(client.base_url) == "https://custom.example.com/v1/"


# ---------------------------------------------------------------------------
# Constructor: api_key mode (Req 5.1, 5.2)
# ---------------------------------------------------------------------------


class TestConstructorWithApiKey:
    def test_sync_api_key_mode(self) -> None:
        client = AwsOpenAI(
            api_key="my-key",
            base_url="https://example.com/v1",
        )
        assert client._use_sigv4 is False
        assert client.api_key == "my-key"

    def test_async_api_key_mode(self) -> None:
        client = AsyncAwsOpenAI(
            api_key="my-key",
            base_url="https://example.com/v1",
        )
        assert client._use_sigv4 is False
        assert client.api_key == "my-key"

    def test_sync_api_key_no_region_required(self) -> None:
        with patch.dict("os.environ", {"AWS_REGION": "", "AWS_DEFAULT_REGION": ""}):
            client = AwsOpenAI(
                api_key="my-key",
                base_url="https://example.com/v1",
            )
            assert client._region == ""

    def test_async_api_key_no_region_required(self) -> None:
        with patch.dict("os.environ", {"AWS_REGION": "", "AWS_DEFAULT_REGION": ""}):
            client = AsyncAwsOpenAI(
                api_key="my-key",
                base_url="https://example.com/v1",
            )
            assert client._region == ""


# ---------------------------------------------------------------------------
# isinstance checks (Req 1.4, 2.4)
# ---------------------------------------------------------------------------


class TestInheritance:
    def test_sync_is_instance_of_openai(self) -> None:
        with _patch_default_creds():
            client = AwsOpenAI(region="us-west-2")
        assert isinstance(client, OpenAI)

    def test_async_is_instance_of_async_openai(self) -> None:
        with _patch_default_creds():
            client = AsyncAwsOpenAI(region="us-west-2")
        assert isinstance(client, AsyncOpenAI)


# ---------------------------------------------------------------------------
# copy() / with_options() preserves Bedrock Mantle fields (Req 1.4, 2.4)
# ---------------------------------------------------------------------------


class TestCopyPreservesFields:
    def test_sync_copy_preserves_region_and_sigv4(self) -> None:
        with _patch_default_creds():
            client = AwsOpenAI(region="us-west-2")
            copied = client.copy()
        assert copied._region == "us-west-2"
        assert copied._use_sigv4 is True

    def test_sync_with_options_preserves_region(self) -> None:
        with _patch_default_creds():
            client = AwsOpenAI(region="us-west-2")
            copied = client.with_options()
        assert copied._region == "us-west-2"

    def test_async_copy_preserves_region_and_sigv4(self) -> None:
        with _patch_default_creds():
            client = AsyncAwsOpenAI(region="us-west-2")
            copied = client.copy()
        assert copied._region == "us-west-2"
        assert copied._use_sigv4 is True

    def test_async_with_options_preserves_region(self) -> None:
        with _patch_default_creds():
            client = AsyncAwsOpenAI(region="us-west-2")
            copied = client.with_options()
        assert copied._region == "us-west-2"

    def test_sync_copy_preserves_credential_provider(self) -> None:
        provider = lambda: _make_frozen_creds()
        with _patch_ensure_botocore():
            client = AwsOpenAI(region="us-west-2", credential_provider=provider)
            copied = client.copy()
        assert copied._credential_provider is provider

    def test_async_copy_preserves_credential_provider(self) -> None:
        provider = lambda: _make_frozen_creds()
        with _patch_ensure_botocore():
            client = AsyncAwsOpenAI(region="us-west-2", credential_provider=provider)
            copied = client.copy()
        assert copied._credential_provider is provider

    def test_sync_copy_overrides_region(self) -> None:
        with _patch_default_creds():
            client = AwsOpenAI(region="us-west-2")
            copied = client.copy(region="eu-west-1")
        assert copied._region == "eu-west-1"

    def test_async_copy_overrides_region(self) -> None:
        with _patch_default_creds():
            client = AsyncAwsOpenAI(region="us-west-2")
            copied = client.copy(region="eu-west-1")
        assert copied._region == "eu-west-1"

    def test_sync_copy_returns_same_type(self) -> None:
        with _patch_default_creds():
            client = AwsOpenAI(region="us-west-2")
            copied = client.copy()
        assert type(copied) is AwsOpenAI

    def test_async_copy_returns_same_type(self) -> None:
        with _patch_default_creds():
            client = AsyncAwsOpenAI(region="us-west-2")
            copied = client.copy()
        assert type(copied) is AsyncAwsOpenAI


# ---------------------------------------------------------------------------
# Default botocore credential chain fallback (Req 4.4, 4.5)
# ---------------------------------------------------------------------------


class TestDefaultBotocoreCredentials:
    def test_sync_uses_botocore_default_chain(self) -> None:
        unfrozen = _make_unfrozen_creds("AKID_DEFAULT", "secret_default", "tok_default")
        with _patch_default_creds(unfrozen):
            client = AwsOpenAI(region="us-west-2")
        assert client._botocore_credentials is unfrozen
        assert client._credential_provider is None

    def test_async_uses_botocore_default_chain(self) -> None:
        unfrozen = _make_unfrozen_creds("AKID_DEFAULT", "secret_default", "tok_default")
        with _patch_default_creds(unfrozen):
            client = AsyncAwsOpenAI(region="us-west-2")
        assert client._botocore_credentials is unfrozen
        assert client._credential_provider is None

    def test_sync_raises_when_botocore_missing(self) -> None:
        with patch(
            "openai.lib.aws._get_default_credentials",
            side_effect=OpenAIError("botocore must be installed"),
        ):
            with pytest.raises(OpenAIError, match="botocore must be installed"):
                AwsOpenAI(region="us-west-2")

    def test_async_raises_when_botocore_missing(self) -> None:
        with patch(
            "openai.lib.aws._get_default_credentials",
            side_effect=OpenAIError("botocore must be installed"),
        ):
            with pytest.raises(OpenAIError, match="botocore must be installed"):
                AsyncAwsOpenAI(region="us-west-2")

    def test_sync_raises_when_no_creds_resolved(self) -> None:
        with patch(
            "openai.lib.aws._get_default_credentials",
            side_effect=OpenAIError("Could not resolve AWS credentials"),
        ):
            with pytest.raises(OpenAIError, match="Could not resolve AWS credentials"):
                AwsOpenAI(region="us-west-2")


# ---------------------------------------------------------------------------
# Credential refresh failure wrapping (Req 6.3)
# ---------------------------------------------------------------------------


class TestCredentialRefreshFailure:
    def test_sync_wraps_provider_error_in_openai_error(self) -> None:
        def bad_provider() -> None:
            raise RuntimeError("token expired")

        with _patch_ensure_botocore():
            client = AwsOpenAI(region="us-west-2", credential_provider=bad_provider)

        request = httpx.Request("POST", "https://example.com/v1/chat/completions", content=b'{"model":"x"}')
        with pytest.raises(OpenAIError, match="Failed to refresh AWS credentials: token expired"):
            client._prepare_request(request)

    async def test_async_wraps_provider_error_in_openai_error(self) -> None:
        def bad_provider() -> None:
            raise RuntimeError("token expired")

        with _patch_ensure_botocore():
            client = AsyncAwsOpenAI(region="us-west-2", credential_provider=bad_provider)

        request = httpx.Request("POST", "https://example.com/v1/chat/completions", content=b'{"model":"x"}')
        with pytest.raises(OpenAIError, match="Failed to refresh AWS credentials: token expired"):
            await client._prepare_request(request)

    async def test_async_wraps_async_provider_error(self) -> None:
        async def bad_async_provider() -> None:
            raise ValueError("async refresh failed")

        with _patch_ensure_botocore():
            client = AsyncAwsOpenAI(region="us-west-2", credential_provider=bad_async_provider)

        request = httpx.Request("POST", "https://example.com/v1/chat/completions", content=b'{"model":"x"}')
        with pytest.raises(OpenAIError, match="Failed to refresh AWS credentials: async refresh failed"):
            await client._prepare_request(request)

    def test_sync_openai_error_not_double_wrapped(self) -> None:
        """If the provider raises OpenAIError directly, it should propagate as-is."""

        def provider_raises_openai_error() -> None:
            raise OpenAIError("custom auth failure")

        with _patch_ensure_botocore():
            client = AwsOpenAI(region="us-west-2", credential_provider=provider_raises_openai_error)

        request = httpx.Request("POST", "https://example.com/v1/chat/completions", content=b'{"model":"x"}')
        with pytest.raises(OpenAIError, match="custom auth failure"):
            client._prepare_request(request)


# ---------------------------------------------------------------------------
# Mutual exclusivity validations (Req 1.3, 2.3, 5.3)
# ---------------------------------------------------------------------------


class TestMutualExclusivity:
    def test_sync_api_key_and_credential_provider_raises(self) -> None:
        with pytest.raises(OpenAIError, match="api_key and credential_provider are mutually exclusive"):
            AwsOpenAI(
                api_key="my-key",
                credential_provider=lambda: _make_frozen_creds(),
                base_url="https://example.com/v1",
                region="us-west-2",
            )

    def test_async_api_key_and_credential_provider_raises(self) -> None:
        with pytest.raises(OpenAIError, match="api_key and credential_provider are mutually exclusive"):
            AsyncAwsOpenAI(
                api_key="my-key",
                credential_provider=lambda: _make_frozen_creds(),
                base_url="https://example.com/v1",
                region="us-west-2",
            )

    def test_sync_no_base_url_no_region_raises(self) -> None:
        with patch.dict("os.environ", {"AWS_REGION": "", "AWS_DEFAULT_REGION": ""}):
            with pytest.raises(ValueError, match="Must provide region"):
                AwsOpenAI()

    def test_async_no_base_url_no_region_raises(self) -> None:
        with patch.dict("os.environ", {"AWS_REGION": "", "AWS_DEFAULT_REGION": ""}):
            with pytest.raises(ValueError, match="Must provide region"):
                AsyncAwsOpenAI()


# ---------------------------------------------------------------------------
# Region resolution from env vars (Req 7.2)
# ---------------------------------------------------------------------------


class TestRegionFromEnv:
    def test_sync_aws_region_env(self) -> None:
        with patch.dict("os.environ", {"AWS_REGION": "ap-southeast-1", "AWS_DEFAULT_REGION": ""}):
            with _patch_default_creds():
                client = AwsOpenAI()
        assert client._region == "ap-southeast-1"

    def test_sync_aws_default_region_env(self) -> None:
        with patch.dict("os.environ", {"AWS_DEFAULT_REGION": "eu-central-1"}, clear=False):
            import os

            orig = os.environ.pop("AWS_REGION", None)
            try:
                with _patch_default_creds():
                    client = AwsOpenAI()
                assert client._region == "eu-central-1"
            finally:
                if orig is not None:
                    os.environ["AWS_REGION"] = orig

    def test_sync_aws_region_takes_precedence(self) -> None:
        with patch.dict("os.environ", {"AWS_REGION": "us-west-2", "AWS_DEFAULT_REGION": "eu-west-1"}):
            with _patch_default_creds():
                client = AwsOpenAI()
        assert client._region == "us-west-2"

    def test_async_aws_region_env(self) -> None:
        with patch.dict("os.environ", {"AWS_REGION": "ap-southeast-1", "AWS_DEFAULT_REGION": ""}):
            with _patch_default_creds():
                client = AsyncAwsOpenAI()
        assert client._region == "ap-southeast-1"


# ---------------------------------------------------------------------------
# Responses API: SigV4 headers injected for responses.create (sync + async)
# ---------------------------------------------------------------------------

_MOCK_RESPONSE_JSON: dict[str, object] = {
    "id": "resp_test",
    "object": "response",
    "created_at": 1700000000,
    "status": "completed",
    "model": "gpt-4o-mini",
    "output": [
        {
            "type": "message",
            "id": "msg_test",
            "status": "completed",
            "role": "assistant",
            "content": [{"type": "output_text", "text": "Hello!", "annotations": []}],
        }
    ],
    "parallel_tool_calls": True,
    "tool_choice": "auto",
    "text": {"format": {"type": "text"}},
    "tools": [],
}


def _fake_sign(request: httpx.Request, creds: object, region: str) -> None:
    """Inject fake SigV4 headers for testing."""
    ak = getattr(creds, "access_key", "UNKNOWN")
    tok = getattr(creds, "token", None)
    request.headers["authorization"] = f"AWS4-HMAC-SHA256 Credential={ak}/{region}/bedrock/aws4_request"
    request.headers["x-amz-date"] = "20240101T000000Z"
    if tok:
        request.headers["x-amz-security-token"] = tok


class TestResponsesApiSigV4:
    """Verify that SigV4 headers are injected when calling the Responses API."""

    def test_sync_responses_create_has_sigv4_headers(self) -> None:
        captured: dict[str, str] = {}

        def capture_handler(request: httpx.Request) -> httpx.Response:
            captured.update(dict(request.headers))
            return httpx.Response(200, json=_MOCK_RESPONSE_JSON)

        transport = httpx.MockTransport(capture_handler)
        provider = lambda: _make_frozen_creds("AKID_TEST", "secret_test", "session_tok")
        with _patch_ensure_botocore(), patch("openai.lib.aws._sign_httpx_request", side_effect=_fake_sign):
            client = AwsOpenAI(
                region="us-west-2",
                credential_provider=provider,
                http_client=httpx.Client(transport=transport),
            )
            client.responses.create(model="gpt-4o-mini", input="Hello")

        assert "AWS4-HMAC-SHA256" in captured.get("authorization", "")
        assert captured.get("x-amz-date") == "20240101T000000Z"
        assert captured.get("x-amz-security-token") == "session_tok"

    async def test_async_responses_create_has_sigv4_headers(self) -> None:
        captured: dict[str, str] = {}

        async def capture_handler(request: httpx.Request) -> httpx.Response:
            captured.update(dict(request.headers))
            return httpx.Response(200, json=_MOCK_RESPONSE_JSON)

        transport = httpx.MockTransport(capture_handler)
        provider = lambda: _make_frozen_creds("AKID_ASYNC", "secret_async", "async_tok")
        with _patch_ensure_botocore(), patch("openai.lib.aws._sign_httpx_request", side_effect=_fake_sign):
            client = AsyncAwsOpenAI(
                region="us-west-2",
                credential_provider=provider,
                http_client=httpx.AsyncClient(transport=transport),
            )
            await client.responses.create(model="gpt-4o-mini", input="Hello")

        assert "AWS4-HMAC-SHA256" in captured.get("authorization", "")
        assert captured.get("x-amz-date") == "20240101T000000Z"
        assert captured.get("x-amz-security-token") == "async_tok"

    def test_sync_responses_create_api_key_no_sigv4(self) -> None:
        """In API key mode, responses.create should use Bearer auth, no SigV4 headers."""
        captured: dict[str, str] = {}

        def capture_handler(request: httpx.Request) -> httpx.Response:
            captured.update(dict(request.headers))
            return httpx.Response(200, json=_MOCK_RESPONSE_JSON)

        transport = httpx.MockTransport(capture_handler)
        client = AwsOpenAI(
            api_key="my-api-key",
            base_url="https://example.com/v1",
            http_client=httpx.Client(transport=transport),
        )
        client.responses.create(model="gpt-4o-mini", input="Hello")

        assert captured.get("authorization") == "Bearer my-api-key"
        assert "x-amz-date" not in captured
        assert "x-amz-security-token" not in captured
