from __future__ import annotations

import json
import base64
from typing import cast
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import respx
import pytest
from respx.models import Call
from inline_snapshot import snapshot

from openai import OpenAI, OAuthError
from openai._exceptions import SubjectTokenProviderError
from openai.auth._workload import (
    gcp_id_token_provider,
    aws_bedrock_token_provider,
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


def _make_mock_botocore(
    access_key: str = "AKIAIOSFODNN7EXAMPLE",
    secret_key: str = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    token: str | None = None,
) -> MagicMock:
    """Create a mock botocore module with fake credentials."""
    mock_botocore = MagicMock()

    frozen = MagicMock()
    frozen.access_key = access_key
    frozen.secret_key = secret_key
    frozen.token = token

    creds = MagicMock()
    creds.get_frozen_credentials.return_value = frozen

    session_instance = MagicMock()
    session_instance.get_credentials.return_value = creds

    mock_botocore.session.Session.return_value = session_instance

    # Use real SigV4QueryAuth and AWSRequest from botocore
    import botocore.auth
    import botocore.awsrequest

    mock_botocore.auth.SigV4QueryAuth = botocore.auth.SigV4QueryAuth
    mock_botocore.awsrequest.AWSRequest = botocore.awsrequest.AWSRequest

    return mock_botocore


def test_aws_bedrock_token_provider() -> None:
    mock_botocore = _make_mock_botocore()

    with patch.dict("sys.modules", {"botocore": mock_botocore, "botocore.session": mock_botocore.session, "botocore.auth": mock_botocore.auth, "botocore.awsrequest": mock_botocore.awsrequest}):
        get_token = aws_bedrock_token_provider(region="us-east-1")

        token = get_token()
        assert token.startswith("bedrock-api-key-")

        encoded_part = token[len("bedrock-api-key-"):]
        decoded_url = base64.b64decode(encoded_part).decode()

        assert "bedrock.amazonaws.com" in decoded_url
        assert "X-Amz-Signature=" in decoded_url
        assert "X-Amz-Credential=" in decoded_url
        assert "Action=CallWithBearerToken" in decoded_url
        assert "&Version=1" in decoded_url


def test_aws_bedrock_token_provider_custom_region() -> None:
    mock_botocore = _make_mock_botocore()

    with patch.dict("sys.modules", {"botocore": mock_botocore, "botocore.session": mock_botocore.session, "botocore.auth": mock_botocore.auth, "botocore.awsrequest": mock_botocore.awsrequest}):
        get_token = aws_bedrock_token_provider(region="eu-west-1")
        token = get_token()

        encoded_part = token[len("bedrock-api-key-"):]
        decoded_url = base64.b64decode(encoded_part).decode()

        assert "eu-west-1" in decoded_url


def test_aws_bedrock_token_provider_no_credentials() -> None:
    mock_botocore = MagicMock()
    session_instance = MagicMock()
    session_instance.get_credentials.return_value = None
    mock_botocore.session.Session.return_value = session_instance

    with patch.dict("sys.modules", {"botocore": mock_botocore, "botocore.session": mock_botocore.session, "botocore.auth": mock_botocore.auth, "botocore.awsrequest": mock_botocore.awsrequest}):
        get_token = aws_bedrock_token_provider(region="us-east-1")

        with pytest.raises(SubjectTokenProviderError, match="No AWS credentials found"):
            get_token()


def test_aws_bedrock_token_provider_no_botocore() -> None:
    with patch.dict("sys.modules", {"botocore": None, "botocore.session": None, "botocore.auth": None, "botocore.awsrequest": None}):
        get_token = aws_bedrock_token_provider(region="us-east-1")

        with pytest.raises(ImportError, match="botocore is required.*openai\\[bedrock\\]"):
            get_token()
