# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
import json
from typing import Any, cast

import httpx
import pytest
from respx import MockRouter

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types import (
    ContainerListResponse,
    ContainerCreateResponse,
    ContainerRetrieveResponse,
)
from openai.pagination import SyncCursorPage, AsyncCursorPage

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


def _container_response() -> dict[str, object]:
    return {
        "id": "container_123",
        "created_at": 0,
        "name": "name",
        "object": "container",
        "status": "active",
    }


def _skills_payload() -> list[dict[str, Any]]:
    return [
        {
            "skill_id": "skill_123",
            "type": "skill_reference",
            "version": "latest",
        },
        {
            "description": "description",
            "name": "inline",
            "source": {
                "data": "UEsDBAo=",
                "media_type": "application/zip",
                "type": "base64",
            },
            "type": "inline",
        },
    ]


class TestContainers:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        container = client.containers.create(
            name="name",
        )
        assert_matches_type(ContainerCreateResponse, container, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        container = client.containers.create(
            name="name",
            expires_after={
                "anchor": "last_active_at",
                "minutes": 0,
            },
            file_ids=["string"],
            memory_limit="1g",
            network_policy={"type": "disabled"},
            skills=[
                {
                    "skill_id": "x",
                    "type": "skill_reference",
                    "version": "version",
                }
            ],
        )
        assert_matches_type(ContainerCreateResponse, container, path=["response"])

    @pytest.mark.respx(base_url=base_url)
    def test_method_create_sends_skills(self, client: OpenAI, respx_mock: MockRouter) -> None:
        respx_mock.post("/containers").mock(return_value=httpx.Response(200, json=_container_response()))

        client.containers.create(
            name="name",
            skills=_skills_payload(),
        )

        request = cast(Any, respx_mock.calls[0]).request
        assert json.loads(request.content.decode("utf-8")) == {
            "name": "name",
            "skills": _skills_payload(),
        }

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.containers.with_raw_response.create(
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        container = response.parse()
        assert_matches_type(ContainerCreateResponse, container, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.containers.with_streaming_response.create(
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            container = response.parse()
            assert_matches_type(ContainerCreateResponse, container, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        container = client.containers.retrieve(
            "container_id",
        )
        assert_matches_type(ContainerRetrieveResponse, container, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.containers.with_raw_response.retrieve(
            "container_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        container = response.parse()
        assert_matches_type(ContainerRetrieveResponse, container, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.containers.with_streaming_response.retrieve(
            "container_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            container = response.parse()
            assert_matches_type(ContainerRetrieveResponse, container, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `container_id` but received ''"):
            client.containers.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        container = client.containers.list()
        assert_matches_type(SyncCursorPage[ContainerListResponse], container, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        container = client.containers.list(
            after="after",
            limit=0,
            name="name",
            order="asc",
        )
        assert_matches_type(SyncCursorPage[ContainerListResponse], container, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.containers.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        container = response.parse()
        assert_matches_type(SyncCursorPage[ContainerListResponse], container, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.containers.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            container = response.parse()
            assert_matches_type(SyncCursorPage[ContainerListResponse], container, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: OpenAI) -> None:
        container = client.containers.delete(
            "container_id",
        )
        assert container is None

    @parametrize
    def test_raw_response_delete(self, client: OpenAI) -> None:
        response = client.containers.with_raw_response.delete(
            "container_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        container = response.parse()
        assert container is None

    @parametrize
    def test_streaming_response_delete(self, client: OpenAI) -> None:
        with client.containers.with_streaming_response.delete(
            "container_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            container = response.parse()
            assert container is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `container_id` but received ''"):
            client.containers.with_raw_response.delete(
                "",
            )


class TestAsyncContainers:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        container = await async_client.containers.create(
            name="name",
        )
        assert_matches_type(ContainerCreateResponse, container, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncOpenAI) -> None:
        container = await async_client.containers.create(
            name="name",
            expires_after={
                "anchor": "last_active_at",
                "minutes": 0,
            },
            file_ids=["string"],
            memory_limit="1g",
            network_policy={"type": "disabled"},
            skills=[
                {
                    "skill_id": "x",
                    "type": "skill_reference",
                    "version": "version",
                }
            ],
        )
        assert_matches_type(ContainerCreateResponse, container, path=["response"])

    @pytest.mark.respx(base_url=base_url)
    async def test_method_create_sends_skills(self, async_client: AsyncOpenAI, respx_mock: MockRouter) -> None:
        respx_mock.post("/containers").mock(return_value=httpx.Response(200, json=_container_response()))

        await async_client.containers.create(
            name="name",
            skills=_skills_payload(),
        )

        request = cast(Any, respx_mock.calls[0]).request
        assert json.loads(request.content.decode("utf-8")) == {
            "name": "name",
            "skills": _skills_payload(),
        }

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.containers.with_raw_response.create(
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        container = response.parse()
        assert_matches_type(ContainerCreateResponse, container, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.containers.with_streaming_response.create(
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            container = await response.parse()
            assert_matches_type(ContainerCreateResponse, container, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        container = await async_client.containers.retrieve(
            "container_id",
        )
        assert_matches_type(ContainerRetrieveResponse, container, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.containers.with_raw_response.retrieve(
            "container_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        container = response.parse()
        assert_matches_type(ContainerRetrieveResponse, container, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.containers.with_streaming_response.retrieve(
            "container_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            container = await response.parse()
            assert_matches_type(ContainerRetrieveResponse, container, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `container_id` but received ''"):
            await async_client.containers.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        container = await async_client.containers.list()
        assert_matches_type(AsyncCursorPage[ContainerListResponse], container, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        container = await async_client.containers.list(
            after="after",
            limit=0,
            name="name",
            order="asc",
        )
        assert_matches_type(AsyncCursorPage[ContainerListResponse], container, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.containers.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        container = response.parse()
        assert_matches_type(AsyncCursorPage[ContainerListResponse], container, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.containers.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            container = await response.parse()
            assert_matches_type(AsyncCursorPage[ContainerListResponse], container, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, async_client: AsyncOpenAI) -> None:
        container = await async_client.containers.delete(
            "container_id",
        )
        assert container is None

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.containers.with_raw_response.delete(
            "container_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        container = response.parse()
        assert container is None

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncOpenAI) -> None:
        async with async_client.containers.with_streaming_response.delete(
            "container_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            container = await response.parse()
            assert container is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `container_id` but received ''"):
            await async_client.containers.with_raw_response.delete(
                "",
            )
