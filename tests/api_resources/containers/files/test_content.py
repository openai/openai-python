# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestContent:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        content = client.containers.files.content.retrieve(
            file_id="file_id",
            container_id="container_id",
        )
        assert content is None

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.containers.files.content.with_raw_response.retrieve(
            file_id="file_id",
            container_id="container_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        content = response.parse()
        assert content is None

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.containers.files.content.with_streaming_response.retrieve(
            file_id="file_id",
            container_id="container_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            content = response.parse()
            assert content is None

        assert cast(Any, response.is_closed) is True

    @parametrize
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
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        content = await async_client.containers.files.content.retrieve(
            file_id="file_id",
            container_id="container_id",
        )
        assert content is None

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.containers.files.content.with_raw_response.retrieve(
            file_id="file_id",
            container_id="container_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        content = response.parse()
        assert content is None

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.containers.files.content.with_streaming_response.retrieve(
            file_id="file_id",
            container_id="container_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            content = await response.parse()
            assert content is None

        assert cast(Any, response.is_closed) is True

    @parametrize
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
