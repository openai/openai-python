# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncCursorPage, AsyncCursorPage
from openai.types.beta.agents.vaults import (
    Credential,
    CredentialDeleted,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCredentials:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        credential = client.beta.agents.vaults.credentials.create(
            vault_id="vault_id",
            auth={
                "access_token": "access_token",
                "mcp_server_url": "mcp_server_url",
                "type": "mcp_oauth",
            },
            name="x",
        )
        assert_matches_type(Credential, credential, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        credential = client.beta.agents.vaults.credentials.create(
            vault_id="vault_id",
            auth={
                "access_token": "access_token",
                "mcp_server_url": "mcp_server_url",
                "type": "mcp_oauth",
                "expires_at": "expires_at",
                "refresh": {
                    "client_id": "client_id",
                    "refresh_token": "refresh_token",
                    "token_endpoint": "token_endpoint",
                    "token_endpoint_auth": {"type": "none"},
                    "resource": "resource",
                    "scope": "scope",
                },
            },
            name="x",
        )
        assert_matches_type(Credential, credential, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.beta.agents.vaults.credentials.with_raw_response.create(
            vault_id="vault_id",
            auth={
                "access_token": "access_token",
                "mcp_server_url": "mcp_server_url",
                "type": "mcp_oauth",
            },
            name="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        credential = response.parse()
        assert_matches_type(Credential, credential, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.beta.agents.vaults.credentials.with_streaming_response.create(
            vault_id="vault_id",
            auth={
                "access_token": "access_token",
                "mcp_server_url": "mcp_server_url",
                "type": "mcp_oauth",
            },
            name="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            credential = response.parse()
            assert_matches_type(Credential, credential, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `vault_id` but received ''"):
            client.beta.agents.vaults.credentials.with_raw_response.create(
                vault_id="",
                auth={
                    "access_token": "access_token",
                    "mcp_server_url": "mcp_server_url",
                    "type": "mcp_oauth",
                },
                name="x",
            )

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        credential = client.beta.agents.vaults.credentials.retrieve(
            credential_id="credential_id",
            vault_id="vault_id",
        )
        assert_matches_type(Credential, credential, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.beta.agents.vaults.credentials.with_raw_response.retrieve(
            credential_id="credential_id",
            vault_id="vault_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        credential = response.parse()
        assert_matches_type(Credential, credential, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.beta.agents.vaults.credentials.with_streaming_response.retrieve(
            credential_id="credential_id",
            vault_id="vault_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            credential = response.parse()
            assert_matches_type(Credential, credential, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `vault_id` but received ''"):
            client.beta.agents.vaults.credentials.with_raw_response.retrieve(
                credential_id="credential_id",
                vault_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `credential_id` but received ''"):
            client.beta.agents.vaults.credentials.with_raw_response.retrieve(
                credential_id="",
                vault_id="vault_id",
            )

    @parametrize
    def test_method_update(self, client: OpenAI) -> None:
        credential = client.beta.agents.vaults.credentials.update(
            credential_id="credential_id",
            vault_id="vault_id",
            auth={"type": "mcp_oauth"},
        )
        assert_matches_type(Credential, credential, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: OpenAI) -> None:
        credential = client.beta.agents.vaults.credentials.update(
            credential_id="credential_id",
            vault_id="vault_id",
            auth={
                "type": "mcp_oauth",
                "access_token": "access_token",
                "expires_at": "expires_at",
                "refresh": {
                    "refresh_token": "refresh_token",
                    "scope": "scope",
                    "token_endpoint_auth": {
                        "type": "client_secret_basic",
                        "client_secret": "client_secret",
                    },
                },
            },
        )
        assert_matches_type(Credential, credential, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: OpenAI) -> None:
        response = client.beta.agents.vaults.credentials.with_raw_response.update(
            credential_id="credential_id",
            vault_id="vault_id",
            auth={"type": "mcp_oauth"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        credential = response.parse()
        assert_matches_type(Credential, credential, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: OpenAI) -> None:
        with client.beta.agents.vaults.credentials.with_streaming_response.update(
            credential_id="credential_id",
            vault_id="vault_id",
            auth={"type": "mcp_oauth"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            credential = response.parse()
            assert_matches_type(Credential, credential, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `vault_id` but received ''"):
            client.beta.agents.vaults.credentials.with_raw_response.update(
                credential_id="credential_id",
                vault_id="",
                auth={"type": "mcp_oauth"},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `credential_id` but received ''"):
            client.beta.agents.vaults.credentials.with_raw_response.update(
                credential_id="",
                vault_id="vault_id",
                auth={"type": "mcp_oauth"},
            )

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        credential = client.beta.agents.vaults.credentials.list(
            vault_id="vault_id",
        )
        assert_matches_type(SyncCursorPage[Credential], credential, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        credential = client.beta.agents.vaults.credentials.list(
            vault_id="vault_id",
            after="after",
            limit=0,
            order="asc",
            status="active",
        )
        assert_matches_type(SyncCursorPage[Credential], credential, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.beta.agents.vaults.credentials.with_raw_response.list(
            vault_id="vault_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        credential = response.parse()
        assert_matches_type(SyncCursorPage[Credential], credential, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.beta.agents.vaults.credentials.with_streaming_response.list(
            vault_id="vault_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            credential = response.parse()
            assert_matches_type(SyncCursorPage[Credential], credential, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `vault_id` but received ''"):
            client.beta.agents.vaults.credentials.with_raw_response.list(
                vault_id="",
            )

    @parametrize
    def test_method_delete(self, client: OpenAI) -> None:
        credential = client.beta.agents.vaults.credentials.delete(
            credential_id="credential_id",
            vault_id="vault_id",
        )
        assert_matches_type(CredentialDeleted, credential, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: OpenAI) -> None:
        response = client.beta.agents.vaults.credentials.with_raw_response.delete(
            credential_id="credential_id",
            vault_id="vault_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        credential = response.parse()
        assert_matches_type(CredentialDeleted, credential, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: OpenAI) -> None:
        with client.beta.agents.vaults.credentials.with_streaming_response.delete(
            credential_id="credential_id",
            vault_id="vault_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            credential = response.parse()
            assert_matches_type(CredentialDeleted, credential, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `vault_id` but received ''"):
            client.beta.agents.vaults.credentials.with_raw_response.delete(
                credential_id="credential_id",
                vault_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `credential_id` but received ''"):
            client.beta.agents.vaults.credentials.with_raw_response.delete(
                credential_id="",
                vault_id="vault_id",
            )


class TestAsyncCredentials:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        credential = await async_client.beta.agents.vaults.credentials.create(
            vault_id="vault_id",
            auth={
                "access_token": "access_token",
                "mcp_server_url": "mcp_server_url",
                "type": "mcp_oauth",
            },
            name="x",
        )
        assert_matches_type(Credential, credential, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncOpenAI) -> None:
        credential = await async_client.beta.agents.vaults.credentials.create(
            vault_id="vault_id",
            auth={
                "access_token": "access_token",
                "mcp_server_url": "mcp_server_url",
                "type": "mcp_oauth",
                "expires_at": "expires_at",
                "refresh": {
                    "client_id": "client_id",
                    "refresh_token": "refresh_token",
                    "token_endpoint": "token_endpoint",
                    "token_endpoint_auth": {"type": "none"},
                    "resource": "resource",
                    "scope": "scope",
                },
            },
            name="x",
        )
        assert_matches_type(Credential, credential, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.vaults.credentials.with_raw_response.create(
            vault_id="vault_id",
            auth={
                "access_token": "access_token",
                "mcp_server_url": "mcp_server_url",
                "type": "mcp_oauth",
            },
            name="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        credential = response.parse()
        assert_matches_type(Credential, credential, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.vaults.credentials.with_streaming_response.create(
            vault_id="vault_id",
            auth={
                "access_token": "access_token",
                "mcp_server_url": "mcp_server_url",
                "type": "mcp_oauth",
            },
            name="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            credential = await response.parse()
            assert_matches_type(Credential, credential, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `vault_id` but received ''"):
            await async_client.beta.agents.vaults.credentials.with_raw_response.create(
                vault_id="",
                auth={
                    "access_token": "access_token",
                    "mcp_server_url": "mcp_server_url",
                    "type": "mcp_oauth",
                },
                name="x",
            )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        credential = await async_client.beta.agents.vaults.credentials.retrieve(
            credential_id="credential_id",
            vault_id="vault_id",
        )
        assert_matches_type(Credential, credential, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.vaults.credentials.with_raw_response.retrieve(
            credential_id="credential_id",
            vault_id="vault_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        credential = response.parse()
        assert_matches_type(Credential, credential, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.vaults.credentials.with_streaming_response.retrieve(
            credential_id="credential_id",
            vault_id="vault_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            credential = await response.parse()
            assert_matches_type(Credential, credential, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `vault_id` but received ''"):
            await async_client.beta.agents.vaults.credentials.with_raw_response.retrieve(
                credential_id="credential_id",
                vault_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `credential_id` but received ''"):
            await async_client.beta.agents.vaults.credentials.with_raw_response.retrieve(
                credential_id="",
                vault_id="vault_id",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncOpenAI) -> None:
        credential = await async_client.beta.agents.vaults.credentials.update(
            credential_id="credential_id",
            vault_id="vault_id",
            auth={"type": "mcp_oauth"},
        )
        assert_matches_type(Credential, credential, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncOpenAI) -> None:
        credential = await async_client.beta.agents.vaults.credentials.update(
            credential_id="credential_id",
            vault_id="vault_id",
            auth={
                "type": "mcp_oauth",
                "access_token": "access_token",
                "expires_at": "expires_at",
                "refresh": {
                    "refresh_token": "refresh_token",
                    "scope": "scope",
                    "token_endpoint_auth": {
                        "type": "client_secret_basic",
                        "client_secret": "client_secret",
                    },
                },
            },
        )
        assert_matches_type(Credential, credential, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.vaults.credentials.with_raw_response.update(
            credential_id="credential_id",
            vault_id="vault_id",
            auth={"type": "mcp_oauth"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        credential = response.parse()
        assert_matches_type(Credential, credential, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.vaults.credentials.with_streaming_response.update(
            credential_id="credential_id",
            vault_id="vault_id",
            auth={"type": "mcp_oauth"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            credential = await response.parse()
            assert_matches_type(Credential, credential, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `vault_id` but received ''"):
            await async_client.beta.agents.vaults.credentials.with_raw_response.update(
                credential_id="credential_id",
                vault_id="",
                auth={"type": "mcp_oauth"},
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `credential_id` but received ''"):
            await async_client.beta.agents.vaults.credentials.with_raw_response.update(
                credential_id="",
                vault_id="vault_id",
                auth={"type": "mcp_oauth"},
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        credential = await async_client.beta.agents.vaults.credentials.list(
            vault_id="vault_id",
        )
        assert_matches_type(AsyncCursorPage[Credential], credential, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        credential = await async_client.beta.agents.vaults.credentials.list(
            vault_id="vault_id",
            after="after",
            limit=0,
            order="asc",
            status="active",
        )
        assert_matches_type(AsyncCursorPage[Credential], credential, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.vaults.credentials.with_raw_response.list(
            vault_id="vault_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        credential = response.parse()
        assert_matches_type(AsyncCursorPage[Credential], credential, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.vaults.credentials.with_streaming_response.list(
            vault_id="vault_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            credential = await response.parse()
            assert_matches_type(AsyncCursorPage[Credential], credential, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `vault_id` but received ''"):
            await async_client.beta.agents.vaults.credentials.with_raw_response.list(
                vault_id="",
            )

    @parametrize
    async def test_method_delete(self, async_client: AsyncOpenAI) -> None:
        credential = await async_client.beta.agents.vaults.credentials.delete(
            credential_id="credential_id",
            vault_id="vault_id",
        )
        assert_matches_type(CredentialDeleted, credential, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.vaults.credentials.with_raw_response.delete(
            credential_id="credential_id",
            vault_id="vault_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        credential = response.parse()
        assert_matches_type(CredentialDeleted, credential, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.vaults.credentials.with_streaming_response.delete(
            credential_id="credential_id",
            vault_id="vault_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            credential = await response.parse()
            assert_matches_type(CredentialDeleted, credential, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `vault_id` but received ''"):
            await async_client.beta.agents.vaults.credentials.with_raw_response.delete(
                credential_id="credential_id",
                vault_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `credential_id` but received ''"):
            await async_client.beta.agents.vaults.credentials.with_raw_response.delete(
                credential_id="",
                vault_id="vault_id",
            )
