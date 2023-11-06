# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

import os

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types import CreateEmbeddingResponse
from openai._client import OpenAI, AsyncOpenAI

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")
api_key = "My API Key"


class TestEmbeddings:
    strict_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
    loose_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)
    parametrize = pytest.mark.parametrize("client", [strict_client, loose_client], ids=["strict", "loose"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        embedding = client.embeddings.create(
            input="The quick brown fox jumped over the lazy dog",
            model="text-embedding-ada-002",
        )
        assert_matches_type(CreateEmbeddingResponse, embedding, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        embedding = client.embeddings.create(
            input="The quick brown fox jumped over the lazy dog",
            model="text-embedding-ada-002",
            encoding_format="float",
            user="user-1234",
        )
        assert_matches_type(CreateEmbeddingResponse, embedding, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.embeddings.with_raw_response.create(
            input="The quick brown fox jumped over the lazy dog",
            model="text-embedding-ada-002",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        embedding = response.parse()
        assert_matches_type(CreateEmbeddingResponse, embedding, path=["response"])


class TestAsyncEmbeddings:
    strict_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
    loose_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)
    parametrize = pytest.mark.parametrize("client", [strict_client, loose_client], ids=["strict", "loose"])

    @parametrize
    async def test_method_create(self, client: AsyncOpenAI) -> None:
        embedding = await client.embeddings.create(
            input="The quick brown fox jumped over the lazy dog",
            model="text-embedding-ada-002",
        )
        assert_matches_type(CreateEmbeddingResponse, embedding, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, client: AsyncOpenAI) -> None:
        embedding = await client.embeddings.create(
            input="The quick brown fox jumped over the lazy dog",
            model="text-embedding-ada-002",
            encoding_format="float",
            user="user-1234",
        )
        assert_matches_type(CreateEmbeddingResponse, embedding, path=["response"])

    @parametrize
    async def test_raw_response_create(self, client: AsyncOpenAI) -> None:
        response = await client.embeddings.with_raw_response.create(
            input="The quick brown fox jumped over the lazy dog",
            model="text-embedding-ada-002",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        embedding = response.parse()
        assert_matches_type(CreateEmbeddingResponse, embedding, path=["response"])
