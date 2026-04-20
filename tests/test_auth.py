import json
from typing import cast
from pathlib import Path

import httpx
import respx
import pytest
from respx.models import Call
from inline_snapshot import snapshot

from openai import OpenAI, OAuthError
from openai.auth._workload import (
    gcp_id_token_provider,
    k8s_service_account_token_provider,
    azure_managed_identity_token_provider,
)


@respx.mock
def test_basic_auth():
    respx.post("https://auth.openai.com/oauth/token").mock(
        return_value=httpx.Response(
            200,
            json={
                "access_token": "fake_access_token",
                "issued_token_type": "urn:ietf:params:oauth:token-type:access_token",
                "token_type": "Bearer",
                "expires_in": 3600,
            },
        )
    )

    respx.get("https://api.openai.com/v1/models").mock(
        return_value=httpx.Response(200, json={"data": [], "object": "list"})
    )

    client = OpenAI(
        workload_identity={
            "client_id": "client_123",
            "identity_provider_id": "idp_123",
            "service_account_id": "sa_123",
            "provider": {
                "get_token": lambda: "fake_subject_token",
                "token_type": "jwt",
            },
        },
    )

    client.models.list()

    assert len(respx.calls) == 2
    token_call = cast(Call, respx.calls[0])
    api_call = cast(Call, respx.calls[1])

    assert token_call.request.url == "https://auth.openai.com/oauth/token"
    assert api_call.request.headers.get("Authorization") == "Bearer fake_access_token"


@respx.mock
def test_workload_identity_exchange_payload_and_cache() -> None:
    provider_call_count = 0

    def provider() -> str:
        nonlocal provider_call_count
        provider_call_count += 1
        return "fake_subject_token"

    exchange_route = respx.post("https://auth.openai.com/oauth/token").mock(
        return_value=httpx.Response(
            200,
            json={
                "access_token": "fake_access_token",
                "issued_token_type": "urn:ietf:params:oauth:token-type:access_token",
                "token_type": "Bearer",
                "expires_in": 3600,
            },
        )
    )
    api_route = respx.get("https://api.openai.com/v1/models").mock(
        return_value=httpx.Response(200, json={"data": [], "object": "list"})
    )

    client = OpenAI(
        workload_identity={
            "client_id": "client_123",
            "identity_provider_id": "idp_123",
            "service_account_id": "sa_123",
            "provider": {
                "get_token": provider,
                "token_type": "jwt",
            },
        },
    )

    client.models.list()
    client.models.list()

    assert provider_call_count == 1
    assert exchange_route.call_count == 1
    assert api_route.call_count == 2

    exchange_request = cast(respx.models.Call, exchange_route.calls[0]).request
    assert json.loads(exchange_request.content) == snapshot(
        {
            "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
            "client_id": "client_123",
            "subject_token": "fake_subject_token",
            "subject_token_type": "urn:ietf:params:oauth:token-type:jwt",
            "identity_provider_id": "idp_123",
            "service_account_id": "sa_123",
        }
    )

    assert (
        cast(respx.models.Call, api_route.calls[0]).request.headers.get("Authorization") == "Bearer fake_access_token"
    )
    assert (
        cast(respx.models.Call, api_route.calls[1]).request.headers.get("Authorization") == "Bearer fake_access_token"
    )


@respx.mock
def test_workload_identity_exchange_error() -> None:
    exchange_route = respx.post("https://auth.openai.com/oauth/token").mock(
        return_value=httpx.Response(
            401,
            json={
                "error": "invalid_grant",
                "error_description": "No service account mapping found for the provided service_account_id.",
            },
        )
    )
    api_route = respx.get("https://api.openai.com/v1/models").mock(
        return_value=httpx.Response(200, json={"data": [], "object": "list"})
    )

    client = OpenAI(
        workload_identity={
            "client_id": "client_123",
            "identity_provider_id": "idp_123",
            "service_account_id": "sa_123",
            "provider": {
                "get_token": lambda: "fake_subject_token",
                "token_type": "jwt",
            },
        },
    )

    with pytest.raises(OAuthError) as exc:
        client.models.list()

    assert exc.value.message == "No service account mapping found for the provided service_account_id."
    assert exc.value.error == "invalid_grant"
    assert exc.value.status_code == 401
    assert exchange_route.call_count == 1
    assert api_route.call_count == 0


def test_k8s_service_account_token_provider(tmp_path: Path) -> None:
    token_file = tmp_path / "token"
    token_file.write_text("my-k8s-token")

    provider = k8s_service_account_token_provider(token_file)

    assert provider["token_type"] == "jwt"
    assert provider["get_token"]() == "my-k8s-token"


@respx.mock
def test_azure_managed_identity_token_provider() -> None:
    respx.get("http://169.254.169.254/metadata/identity/oauth2/token").mock(
        return_value=httpx.Response(200, json={"access_token": "azure-token"})
    )

    provider = azure_managed_identity_token_provider()

    assert provider["token_type"] == "jwt"
    assert provider["get_token"]() == "azure-token"


@respx.mock
def test_gcp_id_token_provider() -> None:
    respx.get("http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity").mock(
        return_value=httpx.Response(200, text="gcp-token")
    )

    provider = gcp_id_token_provider()

    assert provider["token_type"] == "id"
    assert provider["get_token"]() == "gcp-token"
