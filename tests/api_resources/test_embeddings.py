# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types import CreateEmbeddingResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEmbeddings:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        embedding = client.embeddings.create(
            input="The quick brown fox jumped over the lazy dog",
            model="text-embedding-3-small",
        )
        assert_matches_type(CreateEmbeddingResponse, embedding, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        embedding = client.embeddings.create(
            input="The quick brown fox jumped over the lazy dog",
            model="text-embedding-3-small",
            dimensions=1,
            encoding_format="float",
            user="user-1234",
        )
        assert_matches_type(CreateEmbeddingResponse, embedding, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.embeddings.with_raw_response.create(
            input="The quick brown fox jumped over the lazy dog",
            model="text-embedding-3-small",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        embedding = response.parse()
        assert_matches_type(CreateEmbeddingResponse, embedding, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.embeddings.with_streaming_response.create(
            input="The quick brown fox jumped over the lazy dog",
            model="text-embedding-3-small",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            embedding = response.parse()
            assert_matches_type(CreateEmbeddingResponse, embedding, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncEmbeddings:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        embedding = await async_client.embeddings.create(
            input="The quick brown fox jumped over the lazy dog",
            model="text-embedding-3-small",
        )
        assert_matches_type(CreateEmbeddingResponse, embedding, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncOpenAI) -> None:
        embedding = await async_client.embeddings.create(
            input="The quick brown fox jumped over the lazy dog",
            model="text-embedding-3-small",
            dimensions=1,
            encoding_format="float",
            user="user-1234",
        )
        assert_matches_type(CreateEmbeddingResponse, embedding, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.embeddings.with_raw_response.create(
            input="The quick brown fox jumped over the lazy dog",
            model="text-embedding-3-small",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        embedding = response.parse()
        assert_matches_type(CreateEmbeddingResponse, embedding, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.embeddings.with_streaming_response.create(
            input="The quick brown fox jumped over the lazy dog",
            model="text-embedding-3-small",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            embedding = await response.parse()
            assert_matches_type(CreateEmbeddingResponse, embedding, path=["response"])

        assert cast(Any, response.is_closed) is True
