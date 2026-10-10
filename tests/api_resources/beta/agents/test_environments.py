# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncCursorPage, AsyncCursorPage
from openai.types.beta.agents import (
    EnvironmentInfo,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEnvironments:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        environment = client.beta.agents.environments.create(
            environment={"type": "openai_hosted"},
        )
        assert_matches_type(EnvironmentInfo, environment, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        environment = client.beta.agents.environments.create(
            environment={
                "type": "openai_hosted",
                "capability_directories": ["string"],
                "desktop": {"enabled": True},
                "env": {"foo": "string"},
                "environment_template_id": "environment_template_id",
                "files": [
                    {
                        "file_id": "x",
                        "path": "x",
                        "type": "file_id",
                    }
                ],
                "network": {
                    "access": "enabled",
                    "allowed_domains": ["string"],
                    "blocked_domains": ["string"],
                },
                "packages": {
                    "npm": ["string"],
                    "python": ["string"],
                    "system": ["string"],
                },
                "plugins": [
                    {
                        "description": "description",
                        "name": "x",
                        "source": {
                            "data": "x",
                            "media_type": "application/zip",
                            "type": "base64",
                        },
                        "type": "inline",
                    }
                ],
                "setup_commands": [
                    {
                        "command": "command",
                        "cwd": "cwd",
                    }
                ],
                "skills": [
                    {
                        "skill_id": "x",
                        "type": "skill_reference",
                        "version": "version",
                    }
                ],
            },
            vault_ids=["string"],
            idempotency_key="x",
        )
        assert_matches_type(EnvironmentInfo, environment, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.beta.agents.environments.with_raw_response.create(
            environment={"type": "openai_hosted"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = response.parse()
        assert_matches_type(EnvironmentInfo, environment, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.beta.agents.environments.with_streaming_response.create(
            environment={"type": "openai_hosted"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = response.parse()
            assert_matches_type(EnvironmentInfo, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        environment = client.beta.agents.environments.retrieve(
            "environment_id",
        )
        assert_matches_type(EnvironmentInfo, environment, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.beta.agents.environments.with_raw_response.retrieve(
            "environment_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = response.parse()
        assert_matches_type(EnvironmentInfo, environment, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.beta.agents.environments.with_streaming_response.retrieve(
            "environment_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = response.parse()
            assert_matches_type(EnvironmentInfo, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `environment_id` but received ''"):
            client.beta.agents.environments.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        environment = client.beta.agents.environments.list()
        assert_matches_type(SyncCursorPage[EnvironmentInfo], environment, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        environment = client.beta.agents.environments.list(
            after="after",
            limit=1,
            order="asc",
            type="openai_hosted",
        )
        assert_matches_type(SyncCursorPage[EnvironmentInfo], environment, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.beta.agents.environments.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = response.parse()
        assert_matches_type(SyncCursorPage[EnvironmentInfo], environment, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.beta.agents.environments.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = response.parse()
            assert_matches_type(SyncCursorPage[EnvironmentInfo], environment, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncEnvironments:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        environment = await async_client.beta.agents.environments.create(
            environment={"type": "openai_hosted"},
        )
        assert_matches_type(EnvironmentInfo, environment, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncOpenAI) -> None:
        environment = await async_client.beta.agents.environments.create(
            environment={
                "type": "openai_hosted",
                "capability_directories": ["string"],
                "desktop": {"enabled": True},
                "env": {"foo": "string"},
                "environment_template_id": "environment_template_id",
                "files": [
                    {
                        "file_id": "x",
                        "path": "x",
                        "type": "file_id",
                    }
                ],
                "network": {
                    "access": "enabled",
                    "allowed_domains": ["string"],
                    "blocked_domains": ["string"],
                },
                "packages": {
                    "npm": ["string"],
                    "python": ["string"],
                    "system": ["string"],
                },
                "plugins": [
                    {
                        "description": "description",
                        "name": "x",
                        "source": {
                            "data": "x",
                            "media_type": "application/zip",
                            "type": "base64",
                        },
                        "type": "inline",
                    }
                ],
                "setup_commands": [
                    {
                        "command": "command",
                        "cwd": "cwd",
                    }
                ],
                "skills": [
                    {
                        "skill_id": "x",
                        "type": "skill_reference",
                        "version": "version",
                    }
                ],
            },
            vault_ids=["string"],
            idempotency_key="x",
        )
        assert_matches_type(EnvironmentInfo, environment, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.environments.with_raw_response.create(
            environment={"type": "openai_hosted"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = response.parse()
        assert_matches_type(EnvironmentInfo, environment, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.environments.with_streaming_response.create(
            environment={"type": "openai_hosted"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = await response.parse()
            assert_matches_type(EnvironmentInfo, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        environment = await async_client.beta.agents.environments.retrieve(
            "environment_id",
        )
        assert_matches_type(EnvironmentInfo, environment, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.environments.with_raw_response.retrieve(
            "environment_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = response.parse()
        assert_matches_type(EnvironmentInfo, environment, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.environments.with_streaming_response.retrieve(
            "environment_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = await response.parse()
            assert_matches_type(EnvironmentInfo, environment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `environment_id` but received ''"):
            await async_client.beta.agents.environments.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        environment = await async_client.beta.agents.environments.list()
        assert_matches_type(AsyncCursorPage[EnvironmentInfo], environment, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        environment = await async_client.beta.agents.environments.list(
            after="after",
            limit=1,
            order="asc",
            type="openai_hosted",
        )
        assert_matches_type(AsyncCursorPage[EnvironmentInfo], environment, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.environments.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        environment = response.parse()
        assert_matches_type(AsyncCursorPage[EnvironmentInfo], environment, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.environments.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            environment = await response.parse()
            assert_matches_type(AsyncCursorPage[EnvironmentInfo], environment, path=["response"])

        assert cast(Any, response.is_closed) is True
