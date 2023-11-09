# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

import os

import httpx
import pytest
from respx import MockRouter

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types import FileObject, FileDeleted
from openai._types import BinaryResponseContent
from openai._client import OpenAI, AsyncOpenAI
from openai.pagination import SyncPage, AsyncPage

# pyright: reportDeprecated=false

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
            purpose="fine-tune",
        )
        assert_matches_type(FileObject, file, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.files.with_raw_response.create(
            file=b"raw file contents",
            purpose="fine-tune",
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
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        file = client.files.list(
            purpose="string",
        )
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
    @pytest.mark.respx(base_url=base_url)
    def test_method_content(self, client: OpenAI, respx_mock: MockRouter) -> None:
        respx_mock.get("/files/{file_id}/content").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        file = client.files.content(
            "string",
        )
        assert isinstance(file, BinaryResponseContent)
        assert file.json() == {"foo": "bar"}

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_content(self, client: OpenAI, respx_mock: MockRouter) -> None:
        respx_mock.get("/files/{file_id}/content").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        response = client.files.with_raw_response.content(
            "string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert isinstance(file, BinaryResponseContent)
        assert file.json() == {"foo": "bar"}

    @parametrize
    def test_method_retrieve_content(self, client: OpenAI) -> None:
        with pytest.warns(DeprecationWarning):
            file = client.files.retrieve_content(
                "string",
            )
        assert_matches_type(str, file, path=["response"])

    @parametrize
    def test_raw_response_retrieve_content(self, client: OpenAI) -> None:
        with pytest.warns(DeprecationWarning):
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
            purpose="fine-tune",
        )
        assert_matches_type(FileObject, file, path=["response"])

    @parametrize
    async def test_raw_response_create(self, client: AsyncOpenAI) -> None:
        response = await client.files.with_raw_response.create(
            file=b"raw file contents",
            purpose="fine-tune",
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
    async def test_method_list_with_all_params(self, client: AsyncOpenAI) -> None:
        file = await client.files.list(
            purpose="string",
        )
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
    @pytest.mark.respx(base_url=base_url)
    async def test_method_content(self, client: AsyncOpenAI, respx_mock: MockRouter) -> None:
        respx_mock.get("/files/{file_id}/content").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        file = await client.files.content(
            "string",
        )
        assert isinstance(file, BinaryResponseContent)
        assert file.json() == {"foo": "bar"}

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_content(self, client: AsyncOpenAI, respx_mock: MockRouter) -> None:
        respx_mock.get("/files/{file_id}/content").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        response = await client.files.with_raw_response.content(
            "string",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert isinstance(file, BinaryResponseContent)
        assert file.json() == {"foo": "bar"}

    @parametrize
    async def test_method_retrieve_content(self, client: AsyncOpenAI) -> None:
        with pytest.warns(DeprecationWarning):
            file = await client.files.retrieve_content(
                "string",
            )
        assert_matches_type(str, file, path=["response"])

    @parametrize
    async def test_raw_response_retrieve_content(self, client: AsyncOpenAI) -> None:
        with pytest.warns(DeprecationWarning):
            response = await client.files.with_raw_response.retrieve_content(
                "string",
            )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(str, file, path=["response"])
