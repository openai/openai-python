"""Tests for Azure AAD Bearer token auth behavior in ``_auth_headers``.

These tests cover the change introduced in PR #3374, where ``api_key`` is sent
via the ``Authorization: Bearer`` header when ``security["bearer_auth"]`` is
truthy (the Azure AD token scenario), and via the ``api-key`` header otherwise.
"""

from __future__ import annotations

from typing import cast

import httpx
import pytest
from respx import MockRouter
from respx.models import Call as MockRequestCall

from openai._models import FinalRequestOptions
from openai.lib.azure import AzureOpenAI, AsyncAzureOpenAI

API_KEY = "example API key"
AD_TOKEN = "example AD token"
AZURE_ENDPOINT = "https://example-resource.azure.openai.com"
API_VERSION = "2024-02-01"


def _make_sync_client(**overrides: object) -> AzureOpenAI:
    kwargs: dict[str, object] = {
        "api_version": API_VERSION,
        "api_key": API_KEY,
        "azure_endpoint": AZURE_ENDPOINT,
    }
    kwargs.update(overrides)
    return AzureOpenAI(**kwargs)  # type: ignore[arg-type]


def _make_async_client(**overrides: object) -> AsyncAzureOpenAI:
    kwargs: dict[str, object] = {
        "api_version": API_VERSION,
        "api_key": API_KEY,
        "azure_endpoint": AZURE_ENDPOINT,
    }
    kwargs.update(overrides)
    return AsyncAzureOpenAI(**kwargs)  # type: ignore[arg-type]


def test_auth_headers_with_bearer_auth_true_sends_bearer_token() -> None:
    client = _make_sync_client()

    headers = client._auth_headers({"bearer_auth": True})

    assert headers == {"Authorization": f"Bearer {API_KEY}"}, (
        "When bearer_auth is True the api_key must be sent via the "
        f"Authorization: Bearer header, got {headers!r}"
    )
    assert "api-key" not in headers, "api-key header must not be set when using Bearer auth"


def test_auth_headers_with_bearer_auth_false_sends_api_key_header() -> None:
    client = _make_sync_client()

    headers = client._auth_headers({"bearer_auth": False})

    assert headers == {"api-key": API_KEY}, (
        "When bearer_auth is False the api_key must be sent via the api-key "
        f"header, got {headers!r}"
    )
    assert "Authorization" not in headers, "Authorization header must not be set when bearer_auth is False"


def test_auth_headers_azure_ad_token_takes_priority() -> None:
    client = _make_sync_client(api_key=None, azure_ad_token=AD_TOKEN)

    # The AD token must win regardless of the bearer_auth flag.
    headers_bearer_false = client._auth_headers({"bearer_auth": False})
    headers_bearer_true = client._auth_headers({"bearer_auth": True})

    expected = {"Authorization": f"Bearer {AD_TOKEN}"}
    assert headers_bearer_false == expected, (
        "An explicit azure_ad_token must always be sent as a Bearer token, "
        f"even when bearer_auth is False, got {headers_bearer_false!r}"
    )
    assert headers_bearer_true == expected, (
        "An explicit azure_ad_token must always be sent as a Bearer token, "
        f"got {headers_bearer_true!r}"
    )


def test_auth_headers_no_credentials_returns_empty() -> None:
    client = _make_sync_client(api_key=None, _enforce_credentials=False)

    headers = client._auth_headers({"bearer_auth": True})

    assert headers == {}, (
        "With neither api_key nor azure_ad_token set, no auth headers should be "
        f"produced, got {headers!r}"
    )


def test_default_security_options_uses_bearer() -> None:
    options = FinalRequestOptions.construct(method="post", url="/chat/completions")

    assert options.security.get("bearer_auth") is True, (
        "The default FinalRequestOptions.security must enable bearer_auth, "
        f"got {options.security!r}"
    )


def test_async_auth_headers_with_bearer_auth_true() -> None:
    client = _make_async_client()

    headers = client._auth_headers({"bearer_auth": True})

    assert headers == {"Authorization": f"Bearer {API_KEY}"}, (
        "The async client must also send the api_key as a Bearer token when "
        f"bearer_auth is True, got {headers!r}"
    )


def test_async_auth_headers_with_bearer_auth_false() -> None:
    client = _make_async_client()

    headers = client._auth_headers({"bearer_auth": False})

    assert headers == {"api-key": API_KEY}, (
        "The async client must fall back to the api-key header when bearer_auth "
        f"is False, got {headers!r}"
    )


@pytest.mark.respx()
def test_full_request_sends_bearer_header_by_default(respx_mock: MockRouter) -> None:
    respx_mock.post(
        "https://example-resource.azure.openai.com/openai/deployments/gpt-4/chat/completions"
        "?api-version=2024-02-01"
    ).mock(return_value=httpx.Response(200, json={"model": "gpt-4"}))

    client = _make_sync_client()
    client.chat.completions.create(messages=[], model="gpt-4")

    calls = cast("list[MockRequestCall]", respx_mock.calls)
    authorization = calls[0].request.headers.get("Authorization")
    assert authorization == f"Bearer {API_KEY}", (
        "By default (bearer_auth=True) a full request must carry the api_key in "
        f"the Authorization: Bearer header, got {authorization!r}"
    )
    assert "api-key" not in calls[0].request.headers, (
        "The api-key header must not be sent when the default Bearer auth is used"
    )
