# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

import os

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai._client import OpenAI, AsyncOpenAI
from openai.pagination import SyncCursorPage, AsyncCursorPage
from openai.types.beta.assistants import AssistantFile, FileDeleteResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")
api_key = "My API Key"


class TestFiles:
    strict_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
    loose_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)
    parametrize = pytest.mark.parametrize("client", [strict_client, loose_client], ids=["strict", "loose"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        file = client.beta.assistants.files.create(
            "file-AF1WoRqd3aJAHsqc9NY7iL8F",
            file_id="string",
        )
        assert_matches_type(AssistantFile, file, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.beta.assistants.files.with_raw_response.create(
            "file-AF1WoRqd3aJAHsqc9NY7iL8F",
            file_id="string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(AssistantFile, file, path=["response"])

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        file = client.beta.assistants.files.retrieve(
            "string",
            assistant_id="string",
        )
        assert_matches_type(AssistantFile, file, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.beta.assistants.files.with_raw_response.retrieve(
            "string",
            assistant_id="string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(AssistantFile, file, path=["response"])

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        file = client.beta.assistants.files.list(
            "string",
        )
        assert_matches_type(SyncCursorPage[AssistantFile], file, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        file = client.beta.assistants.files.list(
            "string",
            after="string",
            before="string",
            limit=0,
            order="asc",
        )
        assert_matches_type(SyncCursorPage[AssistantFile], file, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.beta.assistants.files.with_raw_response.list(
            "string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(SyncCursorPage[AssistantFile], file, path=["response"])

    @parametrize
    def test_method_delete(self, client: OpenAI) -> None:
        file = client.beta.assistants.files.delete(
            "string",
            assistant_id="string",
        )
        assert_matches_type(FileDeleteResponse, file, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: OpenAI) -> None:
        response = client.beta.assistants.files.with_raw_response.delete(
            "string",
            assistant_id="string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(FileDeleteResponse, file, path=["response"])


class TestAsyncFiles:
    strict_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
    loose_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)
    parametrize = pytest.mark.parametrize("client", [strict_client, loose_client], ids=["strict", "loose"])

    @parametrize
    async def test_method_create(self, client: AsyncOpenAI) -> None:
        file = await client.beta.assistants.files.create(
            "file-AF1WoRqd3aJAHsqc9NY7iL8F",
            file_id="string",
        )
        assert_matches_type(AssistantFile, file, path=["response"])

    @parametrize
    async def test_raw_response_create(self, client: AsyncOpenAI) -> None:
        response = await client.beta.assistants.files.with_raw_response.create(
            "file-AF1WoRqd3aJAHsqc9NY7iL8F",
            file_id="string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(AssistantFile, file, path=["response"])

    @parametrize
    async def test_method_retrieve(self, client: AsyncOpenAI) -> None:
        file = await client.beta.assistants.files.retrieve(
            "string",
            assistant_id="string",
        )
        assert_matches_type(AssistantFile, file, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, client: AsyncOpenAI) -> None:
        response = await client.beta.assistants.files.with_raw_response.retrieve(
            "string",
            assistant_id="string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(AssistantFile, file, path=["response"])

    @parametrize
    async def test_method_list(self, client: AsyncOpenAI) -> None:
        file = await client.beta.assistants.files.list(
            "string",
        )
        assert_matches_type(AsyncCursorPage[AssistantFile], file, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, client: AsyncOpenAI) -> None:
        file = await client.beta.assistants.files.list(
            "string",
            after="string",
            before="string",
            limit=0,
            order="asc",
        )
        assert_matches_type(AsyncCursorPage[AssistantFile], file, path=["response"])

    @parametrize
    async def test_raw_response_list(self, client: AsyncOpenAI) -> None:
        response = await client.beta.assistants.files.with_raw_response.list(
            "string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(AsyncCursorPage[AssistantFile], file, path=["response"])

    @parametrize
    async def test_method_delete(self, client: AsyncOpenAI) -> None:
        file = await client.beta.assistants.files.delete(
            "string",
            assistant_id="string",
        )
        assert_matches_type(FileDeleteResponse, file, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, client: AsyncOpenAI) -> None:
        response = await client.beta.assistants.files.with_raw_response.delete(
            "string",
            assistant_id="string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(FileDeleteResponse, file, path=["response"])
