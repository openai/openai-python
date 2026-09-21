# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncCursorPage, AsyncCursorPage
from openai.types.beta.agents.environments import (
    EnvironmentTemplate,
    EnvironmentTemplateDeleted,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTemplates:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        template = client.beta.agents.environments.templates.create()
        assert_matches_type(EnvironmentTemplate, template, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        template = client.beta.agents.environments.templates.create(
            capability_directories=["string"],
            env={"foo": "string"},
            files=[
                {
                    "file_id": "x",
                    "path": "x",
                    "type": "file_id",
                }
            ],
            name="x",
            network={
                "access": "enabled",
                "allowed_domains": ["string"],
            },
            packages={
                "npm": ["string"],
                "python": ["string"],
                "system": ["string"],
            },
            plugins=[
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
            setup_commands=[
                {
                    "command": "command",
                    "cwd": "cwd",
                }
            ],
            skills=[
                {
                    "skill_id": "x",
                    "type": "skill_reference",
                    "version": "version",
                }
            ],
        )
        assert_matches_type(EnvironmentTemplate, template, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.beta.agents.environments.templates.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        template = response.parse()
        assert_matches_type(EnvironmentTemplate, template, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.beta.agents.environments.templates.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            template = response.parse()
            assert_matches_type(EnvironmentTemplate, template, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        template = client.beta.agents.environments.templates.retrieve(
            "environment_template_id",
        )
        assert_matches_type(EnvironmentTemplate, template, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.beta.agents.environments.templates.with_raw_response.retrieve(
            "environment_template_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        template = response.parse()
        assert_matches_type(EnvironmentTemplate, template, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.beta.agents.environments.templates.with_streaming_response.retrieve(
            "environment_template_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            template = response.parse()
            assert_matches_type(EnvironmentTemplate, template, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `environment_template_id` but received ''"
        ):
            client.beta.agents.environments.templates.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_update(self, client: OpenAI) -> None:
        template = client.beta.agents.environments.templates.update(
            environment_template_id="environment_template_id",
        )
        assert_matches_type(EnvironmentTemplate, template, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: OpenAI) -> None:
        template = client.beta.agents.environments.templates.update(
            environment_template_id="environment_template_id",
            capability_directories=["string"],
            env={"foo": "string"},
            files=[
                {
                    "file_id": "x",
                    "path": "x",
                    "type": "file_id",
                }
            ],
            name="x",
            network={
                "access": "enabled",
                "allowed_domains": ["string"],
            },
            packages={
                "npm": ["string"],
                "python": ["string"],
                "system": ["string"],
            },
            plugins=[
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
            setup_commands=[
                {
                    "command": "command",
                    "cwd": "cwd",
                }
            ],
            skills=[
                {
                    "skill_id": "x",
                    "type": "skill_reference",
                    "version": "version",
                }
            ],
        )
        assert_matches_type(EnvironmentTemplate, template, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: OpenAI) -> None:
        response = client.beta.agents.environments.templates.with_raw_response.update(
            environment_template_id="environment_template_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        template = response.parse()
        assert_matches_type(EnvironmentTemplate, template, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: OpenAI) -> None:
        with client.beta.agents.environments.templates.with_streaming_response.update(
            environment_template_id="environment_template_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            template = response.parse()
            assert_matches_type(EnvironmentTemplate, template, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: OpenAI) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `environment_template_id` but received ''"
        ):
            client.beta.agents.environments.templates.with_raw_response.update(
                environment_template_id="",
            )

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        template = client.beta.agents.environments.templates.list()
        assert_matches_type(SyncCursorPage[EnvironmentTemplate], template, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        template = client.beta.agents.environments.templates.list(
            after="after",
            limit=1,
            order="asc",
        )
        assert_matches_type(SyncCursorPage[EnvironmentTemplate], template, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.beta.agents.environments.templates.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        template = response.parse()
        assert_matches_type(SyncCursorPage[EnvironmentTemplate], template, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.beta.agents.environments.templates.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            template = response.parse()
            assert_matches_type(SyncCursorPage[EnvironmentTemplate], template, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: OpenAI) -> None:
        template = client.beta.agents.environments.templates.delete(
            "environment_template_id",
        )
        assert_matches_type(EnvironmentTemplateDeleted, template, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: OpenAI) -> None:
        response = client.beta.agents.environments.templates.with_raw_response.delete(
            "environment_template_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        template = response.parse()
        assert_matches_type(EnvironmentTemplateDeleted, template, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: OpenAI) -> None:
        with client.beta.agents.environments.templates.with_streaming_response.delete(
            "environment_template_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            template = response.parse()
            assert_matches_type(EnvironmentTemplateDeleted, template, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: OpenAI) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `environment_template_id` but received ''"
        ):
            client.beta.agents.environments.templates.with_raw_response.delete(
                "",
            )


class TestAsyncTemplates:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        template = await async_client.beta.agents.environments.templates.create()
        assert_matches_type(EnvironmentTemplate, template, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncOpenAI) -> None:
        template = await async_client.beta.agents.environments.templates.create(
            capability_directories=["string"],
            env={"foo": "string"},
            files=[
                {
                    "file_id": "x",
                    "path": "x",
                    "type": "file_id",
                }
            ],
            name="x",
            network={
                "access": "enabled",
                "allowed_domains": ["string"],
            },
            packages={
                "npm": ["string"],
                "python": ["string"],
                "system": ["string"],
            },
            plugins=[
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
            setup_commands=[
                {
                    "command": "command",
                    "cwd": "cwd",
                }
            ],
            skills=[
                {
                    "skill_id": "x",
                    "type": "skill_reference",
                    "version": "version",
                }
            ],
        )
        assert_matches_type(EnvironmentTemplate, template, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.environments.templates.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        template = response.parse()
        assert_matches_type(EnvironmentTemplate, template, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.environments.templates.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            template = await response.parse()
            assert_matches_type(EnvironmentTemplate, template, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        template = await async_client.beta.agents.environments.templates.retrieve(
            "environment_template_id",
        )
        assert_matches_type(EnvironmentTemplate, template, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.environments.templates.with_raw_response.retrieve(
            "environment_template_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        template = response.parse()
        assert_matches_type(EnvironmentTemplate, template, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.environments.templates.with_streaming_response.retrieve(
            "environment_template_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            template = await response.parse()
            assert_matches_type(EnvironmentTemplate, template, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `environment_template_id` but received ''"
        ):
            await async_client.beta.agents.environments.templates.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncOpenAI) -> None:
        template = await async_client.beta.agents.environments.templates.update(
            environment_template_id="environment_template_id",
        )
        assert_matches_type(EnvironmentTemplate, template, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncOpenAI) -> None:
        template = await async_client.beta.agents.environments.templates.update(
            environment_template_id="environment_template_id",
            capability_directories=["string"],
            env={"foo": "string"},
            files=[
                {
                    "file_id": "x",
                    "path": "x",
                    "type": "file_id",
                }
            ],
            name="x",
            network={
                "access": "enabled",
                "allowed_domains": ["string"],
            },
            packages={
                "npm": ["string"],
                "python": ["string"],
                "system": ["string"],
            },
            plugins=[
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
            setup_commands=[
                {
                    "command": "command",
                    "cwd": "cwd",
                }
            ],
            skills=[
                {
                    "skill_id": "x",
                    "type": "skill_reference",
                    "version": "version",
                }
            ],
        )
        assert_matches_type(EnvironmentTemplate, template, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.environments.templates.with_raw_response.update(
            environment_template_id="environment_template_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        template = response.parse()
        assert_matches_type(EnvironmentTemplate, template, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.environments.templates.with_streaming_response.update(
            environment_template_id="environment_template_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            template = await response.parse()
            assert_matches_type(EnvironmentTemplate, template, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `environment_template_id` but received ''"
        ):
            await async_client.beta.agents.environments.templates.with_raw_response.update(
                environment_template_id="",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        template = await async_client.beta.agents.environments.templates.list()
        assert_matches_type(AsyncCursorPage[EnvironmentTemplate], template, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        template = await async_client.beta.agents.environments.templates.list(
            after="after",
            limit=1,
            order="asc",
        )
        assert_matches_type(AsyncCursorPage[EnvironmentTemplate], template, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.environments.templates.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        template = response.parse()
        assert_matches_type(AsyncCursorPage[EnvironmentTemplate], template, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.environments.templates.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            template = await response.parse()
            assert_matches_type(AsyncCursorPage[EnvironmentTemplate], template, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, async_client: AsyncOpenAI) -> None:
        template = await async_client.beta.agents.environments.templates.delete(
            "environment_template_id",
        )
        assert_matches_type(EnvironmentTemplateDeleted, template, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.environments.templates.with_raw_response.delete(
            "environment_template_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        template = response.parse()
        assert_matches_type(EnvironmentTemplateDeleted, template, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.environments.templates.with_streaming_response.delete(
            "environment_template_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            template = await response.parse()
            assert_matches_type(EnvironmentTemplateDeleted, template, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `environment_template_id` but received ''"
        ):
            await async_client.beta.agents.environments.templates.with_raw_response.delete(
                "",
            )
