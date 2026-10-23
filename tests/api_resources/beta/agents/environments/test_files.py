# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncTokenPage, AsyncTokenPage
from openai.types.beta.agents.environments import EnvironmentFile

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFiles:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create_overload_1(self, client: OpenAI) -> None:
        file = client.beta.agents.environments.files.create(
            environment_id="environment_id",
            file_id="x",
            path="x",
            type="file_id",
        )
        assert_matches_type(EnvironmentFile, file, path=["response"])

    @parametrize
    def test_raw_response_create_overload_1(self, client: OpenAI) -> None:
        response = client.beta.agents.environments.files.with_raw_response.create(
            environment_id="environment_id",
            file_id="x",
            path="x",
            type="file_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(EnvironmentFile, file, path=["response"])

    @parametrize
    def test_streaming_response_create_overload_1(self, client: OpenAI) -> None:
        with client.beta.agents.environments.files.with_streaming_response.create(
            environment_id="environment_id",
            file_id="x",
            path="x",
            type="file_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(EnvironmentFile, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create_overload_1(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `environment_id` but received ''"):
            client.beta.agents.environments.files.with_raw_response.create(
                environment_id="",
                file_id="x",
                path="x",
                type="file_id",
            )

    @parametrize
    def test_method_create_overload_2(self, client: OpenAI) -> None:
        file = client.beta.agents.environments.files.create(
            environment_id="environment_id",
            data="data",
            path="x",
            type="inline",
        )
        assert_matches_type(EnvironmentFile, file, path=["response"])

    @parametrize
    def test_raw_response_create_overload_2(self, client: OpenAI) -> None:
        response = client.beta.agents.environments.files.with_raw_response.create(
            environment_id="environment_id",
            data="data",
            path="x",
            type="inline",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(EnvironmentFile, file, path=["response"])

    @parametrize
    def test_streaming_response_create_overload_2(self, client: OpenAI) -> None:
        with client.beta.agents.environments.files.with_streaming_response.create(
            environment_id="environment_id",
            data="data",
            path="x",
            type="inline",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(EnvironmentFile, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create_overload_2(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `environment_id` but received ''"):
            client.beta.agents.environments.files.with_raw_response.create(
                environment_id="",
                data="data",
                path="x",
                type="inline",
            )

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        file = client.beta.agents.environments.files.list(
            environment_id="environment_id",
        )
        assert_matches_type(SyncTokenPage[EnvironmentFile], file, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        file = client.beta.agents.environments.files.list(
            environment_id="environment_id",
            limit=1,
            order="asc",
            page="page",
            path="path",
        )
        assert_matches_type(SyncTokenPage[EnvironmentFile], file, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.beta.agents.environments.files.with_raw_response.list(
            environment_id="environment_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(SyncTokenPage[EnvironmentFile], file, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.beta.agents.environments.files.with_streaming_response.list(
            environment_id="environment_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(SyncTokenPage[EnvironmentFile], file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `environment_id` but received ''"):
            client.beta.agents.environments.files.with_raw_response.list(
                environment_id="",
            )


class TestAsyncFiles:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create_overload_1(self, async_client: AsyncOpenAI) -> None:
        file = await async_client.beta.agents.environments.files.create(
            environment_id="environment_id",
            file_id="x",
            path="x",
            type="file_id",
        )
        assert_matches_type(EnvironmentFile, file, path=["response"])

    @parametrize
    async def test_raw_response_create_overload_1(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.environments.files.with_raw_response.create(
            environment_id="environment_id",
            file_id="x",
            path="x",
            type="file_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(EnvironmentFile, file, path=["response"])

    @parametrize
    async def test_streaming_response_create_overload_1(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.environments.files.with_streaming_response.create(
            environment_id="environment_id",
            file_id="x",
            path="x",
            type="file_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(EnvironmentFile, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create_overload_1(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `environment_id` but received ''"):
            await async_client.beta.agents.environments.files.with_raw_response.create(
                environment_id="",
                file_id="x",
                path="x",
                type="file_id",
            )

    @parametrize
    async def test_method_create_overload_2(self, async_client: AsyncOpenAI) -> None:
        file = await async_client.beta.agents.environments.files.create(
            environment_id="environment_id",
            data="data",
            path="x",
            type="inline",
        )
        assert_matches_type(EnvironmentFile, file, path=["response"])

    @parametrize
    async def test_raw_response_create_overload_2(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.environments.files.with_raw_response.create(
            environment_id="environment_id",
            data="data",
            path="x",
            type="inline",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(EnvironmentFile, file, path=["response"])

    @parametrize
    async def test_streaming_response_create_overload_2(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.environments.files.with_streaming_response.create(
            environment_id="environment_id",
            data="data",
            path="x",
            type="inline",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(EnvironmentFile, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create_overload_2(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `environment_id` but received ''"):
            await async_client.beta.agents.environments.files.with_raw_response.create(
                environment_id="",
                data="data",
                path="x",
                type="inline",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        file = await async_client.beta.agents.environments.files.list(
            environment_id="environment_id",
        )
        assert_matches_type(AsyncTokenPage[EnvironmentFile], file, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        file = await async_client.beta.agents.environments.files.list(
            environment_id="environment_id",
            limit=1,
            order="asc",
            page="page",
            path="path",
        )
        assert_matches_type(AsyncTokenPage[EnvironmentFile], file, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.environments.files.with_raw_response.list(
            environment_id="environment_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(AsyncTokenPage[EnvironmentFile], file, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.environments.files.with_streaming_response.list(
            environment_id="environment_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(AsyncTokenPage[EnvironmentFile], file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `environment_id` but received ''"):
            await async_client.beta.agents.environments.files.with_raw_response.list(
                environment_id="",
            )
