# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

import os

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types import FileObject, FileDeleted
from openai._client import OpenAI, AsyncOpenAI
from openai.pagination import SyncPage, AsyncPage

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")
api_key = "My API Key"


class TestFiles:
    strict_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
    loose_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)
    parametrize = pytest.mark.parametrize("client", [strict_client, loose_client], ids=["strict", "loose"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        file = client.files.create(
            file=b"raw file contents",
            purpose="string",
        )
        assert_matches_type(FileObject, file, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.files.with_raw_response.create(
            file=b"raw file contents",
            purpose="string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(FileObject, file, path=["response"])

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        file = client.files.retrieve(
            "string",
        )
        assert_matches_type(FileObject, file, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.files.with_raw_response.retrieve(
            "string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(FileObject, file, path=["response"])

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        file = client.files.list()
        assert_matches_type(SyncPage[FileObject], file, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.files.with_raw_response.list()
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(SyncPage[FileObject], file, path=["response"])

    @parametrize
    def test_method_delete(self, client: OpenAI) -> None:
        file = client.files.delete(
            "string",
        )
        assert_matches_type(FileDeleted, file, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: OpenAI) -> None:
        response = client.files.with_raw_response.delete(
            "string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(FileDeleted, file, path=["response"])

    @parametrize
    def test_method_retrieve_content(self, client: OpenAI) -> None:
        file = client.files.retrieve_content(
            "string",
        )
        assert_matches_type(str, file, path=["response"])

    @parametrize
    def test_raw_response_retrieve_content(self, client: OpenAI) -> None:
        response = client.files.with_raw_response.retrieve_content(
            "string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(str, file, path=["response"])


class TestAsyncFiles:
    strict_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
    loose_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)
    parametrize = pytest.mark.parametrize("client", [strict_client, loose_client], ids=["strict", "loose"])

    @parametrize
    async def test_method_create(self, client: AsyncOpenAI) -> None:
        file = await client.files.create(
            file=b"raw file contents",
            purpose="string",
        )
        assert_matches_type(FileObject, file, path=["response"])

    @parametrize
    async def test_raw_response_create(self, client: AsyncOpenAI) -> None:
        response = await client.files.with_raw_response.create(
            file=b"raw file contents",
            purpose="string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(FileObject, file, path=["response"])

    @parametrize
    async def test_method_retrieve(self, client: AsyncOpenAI) -> None:
        file = await client.files.retrieve(
            "string",
        )
        assert_matches_type(FileObject, file, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, client: AsyncOpenAI) -> None:
        response = await client.files.with_raw_response.retrieve(
            "string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(FileObject, file, path=["response"])

    @parametrize
    async def test_method_list(self, client: AsyncOpenAI) -> None:
        file = await client.files.list()
        assert_matches_type(AsyncPage[FileObject], file, path=["response"])

    @parametrize
    async def test_raw_response_list(self, client: AsyncOpenAI) -> None:
        response = await client.files.with_raw_response.list()
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(AsyncPage[FileObject], file, path=["response"])

    @parametrize
    async def test_method_delete(self, client: AsyncOpenAI) -> None:
        file = await client.files.delete(
            "string",
        )
        assert_matches_type(FileDeleted, file, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, client: AsyncOpenAI) -> None:
        response = await client.files.with_raw_response.delete(
            "string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(FileDeleted, file, path=["response"])

    @parametrize
    async def test_method_retrieve_content(self, client: AsyncOpenAI) -> None:
        file = await client.files.retrieve_content(
            "string",
        )
        assert_matches_type(str, file, path=["response"])

    @parametrize
    async def test_raw_response_retrieve_content(self, client: AsyncOpenAI) -> None:
        response = await client.files.with_raw_response.retrieve_content(
            "string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(str, file, path=["response"])
