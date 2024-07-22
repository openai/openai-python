# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types.uploads import UploadPart

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestParts:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        part = client.uploads.parts.create(
            upload_id="upload_abc123",
            data=b"raw file contents",
        )
        assert_matches_type(UploadPart, part, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.uploads.parts.with_raw_response.create(
            upload_id="upload_abc123",
            data=b"raw file contents",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        part = response.parse()
        assert_matches_type(UploadPart, part, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.uploads.parts.with_streaming_response.create(
            upload_id="upload_abc123",
            data=b"raw file contents",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            part = response.parse()
            assert_matches_type(UploadPart, part, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `upload_id` but received ''"):
            client.uploads.parts.with_raw_response.create(
                upload_id="",
                data=b"raw file contents",
            )


class TestAsyncParts:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        part = await async_client.uploads.parts.create(
            upload_id="upload_abc123",
            data=b"raw file contents",
        )
        assert_matches_type(UploadPart, part, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.uploads.parts.with_raw_response.create(
            upload_id="upload_abc123",
            data=b"raw file contents",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        part = response.parse()
        assert_matches_type(UploadPart, part, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.uploads.parts.with_streaming_response.create(
            upload_id="upload_abc123",
            data=b"raw file contents",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            part = await response.parse()
            assert_matches_type(UploadPart, part, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `upload_id` but received ''"):
            await async_client.uploads.parts.with_raw_response.create(
                upload_id="",
                data=b"raw file contents",
            )
