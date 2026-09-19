from __future__ import annotations

import json
import logging

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from openai._compat import get_model_fields
from openai.types.beta.agents.vaults import Credential, CredentialNetworkingParam
from openai.types.beta.agents.vaults.credential_auth import VaultCredentialAuthResourceEnvironmentVariable
from openai.types.beta.agents.vaults.credential_auth_create_param import (
    CredentialAuthCreateParam,
    CreateVaultCredentialAuthParamEnvironmentVariable,
)
from openai.types.beta.agents.vaults.credential_auth_rotate_param import (
    RotateVaultCredentialAuthParamEnvironmentVariable,
)

BASE_URL = "https://sdk-tests.example.invalid/v1"
SECRET = "synthetic-environment-credential-secret"
ROTATED_SECRET = "synthetic-rotated-environment-credential-secret"


def credential_response(auth: object) -> dict[str, object]:
    return {
        "id": "credential_synthetic",
        "vault_id": "vault_synthetic",
        "object": "vault.credential",
        "name": "Synthetic credential",
        "created_at": 1,
        "updated_at": 1,
        "auth": auth,
    }


def assert_environment_metadata(credential: Credential, networking: CredentialNetworkingParam) -> None:
    assert isinstance(credential.auth, VaultCredentialAuthResourceEnvironmentVariable)
    assert credential.auth.to_dict() == {
        "type": "environment_variable",
        "secret_name": "SYNTHETIC_SERVICE_KEY",
        "networking": networking,
    }
    assert "secret_value" not in get_model_fields(type(credential.auth))
    assert SECRET not in repr(credential)
    assert ROTATED_SECRET not in credential.to_json()


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("strict", [False, True])
@pytest.mark.parametrize(
    "networking",
    [
        {"type": "limited", "allowed_hosts": ["destination.example.test", "192.0.2.1"]},
        {"type": "unrestricted"},
    ],
)
async def test_environment_credential_create(
    mode: str, strict: bool, networking: CredentialNetworkingParam, caplog: pytest.LogCaptureFixture
) -> None:
    auth: CreateVaultCredentialAuthParamEnvironmentVariable = {
        "type": "environment_variable",
        "secret_name": "SYNTHETIC_SERVICE_KEY",
        "secret_value": SECRET,
        "networking": networking,
    }
    requests: list[httpx2.Request] = []

    def respond(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        assert request.method == "POST"
        assert str(request.url) == BASE_URL + "/vaults/vault_synthetic/credentials"
        assert json.loads(request.content) == {"auth": auth, "name": "Synthetic credential"}
        return httpx2.Response(
            200,
            json=credential_response(
                {"type": "environment_variable", "secret_name": "SYNTHETIC_SERVICE_KEY", "networking": networking}
            ),
        )

    with caplog.at_level(logging.DEBUG, logger="openai._base_client"):
        if mode == "sync":
            with OpenAI(
                api_key="synthetic-api-key",
                organization="synthetic-organization",
                project="synthetic-project",
                base_url=BASE_URL,
                max_retries=0,
                _strict_response_validation=strict,
                http_client=httpx2.Client(transport=httpx2.MockTransport(respond), trust_env=False),
            ) as client:
                credential = client.beta.agents.vaults.credentials.create(
                    "vault_synthetic", auth=auth, name="Synthetic credential"
                )
        else:
            async with AsyncOpenAI(
                api_key="synthetic-api-key",
                organization="synthetic-organization",
                project="synthetic-project",
                base_url=BASE_URL,
                max_retries=0,
                _strict_response_validation=strict,
                http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(respond), trust_env=False),
            ) as async_client:
                credential = await async_client.beta.agents.vaults.credentials.create(
                    "vault_synthetic", auth=auth, name="Synthetic credential"
                )

    assert len(requests) == 1
    assert_environment_metadata(credential, networking)
    assert SECRET not in caplog.text


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("strict", [False, True])
async def test_environment_credential_rotation(mode: str, strict: bool, caplog: pytest.LogCaptureFixture) -> None:
    auth: RotateVaultCredentialAuthParamEnvironmentVariable = {
        "type": "environment_variable",
        "secret_value": ROTATED_SECRET,
    }
    networking: CredentialNetworkingParam = {"type": "limited", "allowed_hosts": ["destination.example.test"]}
    requests: list[httpx2.Request] = []

    def respond(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        assert request.method == "POST"
        assert str(request.url) == BASE_URL + "/vaults/vault_synthetic/credentials/credential_synthetic"
        assert json.loads(request.content) == {"auth": auth}
        return httpx2.Response(
            200,
            json=credential_response(
                {"type": "environment_variable", "secret_name": "SYNTHETIC_SERVICE_KEY", "networking": networking}
            ),
        )

    with caplog.at_level(logging.DEBUG, logger="openai._base_client"):
        if mode == "sync":
            with OpenAI(
                api_key="synthetic-api-key",
                organization="synthetic-organization",
                project="synthetic-project",
                base_url=BASE_URL,
                max_retries=0,
                _strict_response_validation=strict,
                http_client=httpx2.Client(transport=httpx2.MockTransport(respond), trust_env=False),
            ) as client:
                credential = client.beta.agents.vaults.credentials.update(
                    "credential_synthetic", vault_id="vault_synthetic", auth=auth
                )
        else:
            async with AsyncOpenAI(
                api_key="synthetic-api-key",
                organization="synthetic-organization",
                project="synthetic-project",
                base_url=BASE_URL,
                max_retries=0,
                _strict_response_validation=strict,
                http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(respond), trust_env=False),
            ) as async_client:
                credential = await async_client.beta.agents.vaults.credentials.update(
                    "credential_synthetic", vault_id="vault_synthetic", auth=auth
                )

    assert len(requests) == 1
    assert_environment_metadata(credential, networking)
    assert ROTATED_SECRET not in caplog.text


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize(
    ("auth", "response_auth"),
    [
        (
            {"type": "static_bearer", "token": SECRET, "mcp_server_url": "https://mcp.example.test"},
            {"type": "static_bearer", "mcp_server_url": "https://mcp.example.test"},
        ),
        (
            {"type": "mcp_oauth", "access_token": SECRET, "mcp_server_url": "https://mcp.example.test"},
            {"type": "mcp_oauth", "mcp_server_url": "https://mcp.example.test"},
        ),
    ],
)
async def test_existing_credential_auth_variants(
    mode: str, auth: CredentialAuthCreateParam, response_auth: dict[str, str]
) -> None:
    requests: list[httpx2.Request] = []

    def respond(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        assert request.method == "POST"
        assert str(request.url) == BASE_URL + "/vaults/vault_synthetic/credentials"
        assert json.loads(request.content) == {"auth": auth, "name": "Synthetic credential"}
        return httpx2.Response(200, json=credential_response(response_auth))

    if mode == "sync":
        with OpenAI(
            api_key="synthetic-api-key",
            base_url=BASE_URL,
            max_retries=0,
            _strict_response_validation=True,
            http_client=httpx2.Client(transport=httpx2.MockTransport(respond), trust_env=False),
        ) as client:
            credential = client.beta.agents.vaults.credentials.create(
                "vault_synthetic", auth=auth, name="Synthetic credential"
            )
    else:
        async with AsyncOpenAI(
            api_key="synthetic-api-key",
            base_url=BASE_URL,
            max_retries=0,
            _strict_response_validation=True,
            http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(respond), trust_env=False),
        ) as async_client:
            credential = await async_client.beta.agents.vaults.credentials.create(
                "vault_synthetic", auth=auth, name="Synthetic credential"
            )

    assert len(requests) == 1
    assert credential.auth.type == response_auth["type"]
    assert not isinstance(credential.auth, VaultCredentialAuthResourceEnvironmentVariable)
