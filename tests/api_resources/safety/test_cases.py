# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types.safety import SafetyCase

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCases:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        case = client.safety.cases.retrieve(
            "id",
        )
        assert_matches_type(SafetyCase, case, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.safety.cases.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        case = response.parse()
        assert_matches_type(SafetyCase, case, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.safety.cases.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            case = response.parse()
            assert_matches_type(SafetyCase, case, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.safety.cases.with_raw_response.retrieve(
                "",
            )


class TestAsyncCases:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        case = await async_client.safety.cases.retrieve(
            "id",
        )
        assert_matches_type(SafetyCase, case, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.safety.cases.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        case = response.parse()
        assert_matches_type(SafetyCase, case, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.safety.cases.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            case = await response.parse()
            assert_matches_type(SafetyCase, case, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.safety.cases.with_raw_response.retrieve(
                "",
            )
