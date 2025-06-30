# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import httpx
import pytest
from respx import MockRouter

import openai._legacy_response as _legacy_response
from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type

# pyright: reportDeprecated=false

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestContent:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_retrieve(self, client: OpenAI, respx_mock: MockRouter) -> None:
        respx_mock.get("/containers/container_id/files/file_id/content").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        content = client.containers.files.content.retrieve(
            file_id="file_id",
            container_id="container_id",
        )
        assert isinstance(content, _legacy_response.HttpxBinaryResponseContent)
        assert content.json() == {"foo": "bar"}

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_retrieve(self, client: OpenAI, respx_mock: MockRouter) -> None:
        respx_mock.get("/containers/container_id/files/file_id/content").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )

        response = client.containers.files.content.with_raw_response.retrieve(
            file_id="file_id",
            container_id="container_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        content = response.parse()
        assert_matches_type(_legacy_response.HttpxBinaryResponseContent, content, path=["response"])

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_retrieve(self, client: OpenAI, respx_mock: MockRouter) -> None:
        respx_mock.get("/containers/container_id/files/file_id/content").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        with client.containers.files.content.with_streaming_response.retrieve(
            file_id="file_id",
            container_id="container_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            content = response.parse()
            assert_matches_type(bytes, content, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `container_id` but received ''"):
            client.containers.files.content.with_raw_response.retrieve(
                file_id="file_id",
                container_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_id` but received ''"):
            client.containers.files.content.with_raw_response.retrieve(
                file_id="",
                container_id="container_id",
            )


class TestAsyncContent:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_retrieve(self, async_client: AsyncOpenAI, respx_mock: MockRouter) -> None:
        respx_mock.get("/containers/container_id/files/file_id/content").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        content = await async_client.containers.files.content.retrieve(
            file_id="file_id",
            container_id="container_id",
        )
        assert isinstance(content, _legacy_response.HttpxBinaryResponseContent)
        assert content.json() == {"foo": "bar"}

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI, respx_mock: MockRouter) -> None:
        respx_mock.get("/containers/container_id/files/file_id/content").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )

        response = await async_client.containers.files.content.with_raw_response.retrieve(
            file_id="file_id",
            container_id="container_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        content = response.parse()
        assert_matches_type(_legacy_response.HttpxBinaryResponseContent, content, path=["response"])

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI, respx_mock: MockRouter) -> None:
        respx_mock.get("/containers/container_id/files/file_id/content").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        async with async_client.containers.files.content.with_streaming_response.retrieve(
            file_id="file_id",
            container_id="container_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            content = await response.parse()
            assert_matches_type(bytes, content, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `container_id` but received ''"):
            await async_client.containers.files.content.with_raw_response.retrieve(
                file_id="file_id",
                container_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `file_id` but received ''"):
            await async_client.containers.files.content.with_raw_response.retrieve(
                file_id="",
                container_id="container_id",
            )
