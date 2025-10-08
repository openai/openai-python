# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types.beta import ChatKitUploadFileResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestChatKit:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_upload_file(self, client: OpenAI) -> None:
        chatkit = client.beta.chatkit.upload_file(
            file=b"raw file contents",
        )
        assert_matches_type(ChatKitUploadFileResponse, chatkit, path=["response"])

    @parametrize
    def test_raw_response_upload_file(self, client: OpenAI) -> None:
        response = client.beta.chatkit.with_raw_response.upload_file(
            file=b"raw file contents",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        chatkit = response.parse()
        assert_matches_type(ChatKitUploadFileResponse, chatkit, path=["response"])

    @parametrize
    def test_streaming_response_upload_file(self, client: OpenAI) -> None:
        with client.beta.chatkit.with_streaming_response.upload_file(
            file=b"raw file contents",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            chatkit = response.parse()
            assert_matches_type(ChatKitUploadFileResponse, chatkit, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncChatKit:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_upload_file(self, async_client: AsyncOpenAI) -> None:
        chatkit = await async_client.beta.chatkit.upload_file(
            file=b"raw file contents",
        )
        assert_matches_type(ChatKitUploadFileResponse, chatkit, path=["response"])

    @parametrize
    async def test_raw_response_upload_file(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.chatkit.with_raw_response.upload_file(
            file=b"raw file contents",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        chatkit = response.parse()
        assert_matches_type(ChatKitUploadFileResponse, chatkit, path=["response"])

    @parametrize
    async def test_streaming_response_upload_file(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.chatkit.with_streaming_response.upload_file(
            file=b"raw file contents",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            chatkit = await response.parse()
            assert_matches_type(ChatKitUploadFileResponse, chatkit, path=["response"])

        assert cast(Any, response.is_closed) is True
