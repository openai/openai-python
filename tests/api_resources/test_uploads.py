# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types import Upload

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestUploads:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        upload = client.uploads.create(
            bytes=0,
            filename="filename",
            mime_type="mime_type",
            purpose="assistants",
        )
        assert_matches_type(Upload, upload, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.uploads.with_raw_response.create(
            bytes=0,
            filename="filename",
            mime_type="mime_type",
            purpose="assistants",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = response.parse()
        assert_matches_type(Upload, upload, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.uploads.with_streaming_response.create(
            bytes=0,
            filename="filename",
            mime_type="mime_type",
            purpose="assistants",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = response.parse()
            assert_matches_type(Upload, upload, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_cancel(self, client: OpenAI) -> None:
        upload = client.uploads.cancel(
            "upload_abc123",
        )
        assert_matches_type(Upload, upload, path=["response"])

    @parametrize
    def test_raw_response_cancel(self, client: OpenAI) -> None:
        response = client.uploads.with_raw_response.cancel(
            "upload_abc123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = response.parse()
        assert_matches_type(Upload, upload, path=["response"])

    @parametrize
    def test_streaming_response_cancel(self, client: OpenAI) -> None:
        with client.uploads.with_streaming_response.cancel(
            "upload_abc123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = response.parse()
            assert_matches_type(Upload, upload, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_cancel(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `upload_id` but received ''"):
            client.uploads.with_raw_response.cancel(
                "",
            )

    @parametrize
    def test_method_complete(self, client: OpenAI) -> None:
        upload = client.uploads.complete(
            upload_id="upload_abc123",
            part_ids=["string", "string", "string"],
        )
        assert_matches_type(Upload, upload, path=["response"])

    @parametrize
    def test_method_complete_with_all_params(self, client: OpenAI) -> None:
        upload = client.uploads.complete(
            upload_id="upload_abc123",
            part_ids=["string", "string", "string"],
            md5="md5",
        )
        assert_matches_type(Upload, upload, path=["response"])

    @parametrize
    def test_raw_response_complete(self, client: OpenAI) -> None:
        response = client.uploads.with_raw_response.complete(
            upload_id="upload_abc123",
            part_ids=["string", "string", "string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = response.parse()
        assert_matches_type(Upload, upload, path=["response"])

    @parametrize
    def test_streaming_response_complete(self, client: OpenAI) -> None:
        with client.uploads.with_streaming_response.complete(
            upload_id="upload_abc123",
            part_ids=["string", "string", "string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = response.parse()
            assert_matches_type(Upload, upload, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_complete(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `upload_id` but received ''"):
            client.uploads.with_raw_response.complete(
                upload_id="",
                part_ids=["string", "string", "string"],
            )


class TestAsyncUploads:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        upload = await async_client.uploads.create(
            bytes=0,
            filename="filename",
            mime_type="mime_type",
            purpose="assistants",
        )
        assert_matches_type(Upload, upload, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.uploads.with_raw_response.create(
            bytes=0,
            filename="filename",
            mime_type="mime_type",
            purpose="assistants",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = response.parse()
        assert_matches_type(Upload, upload, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.uploads.with_streaming_response.create(
            bytes=0,
            filename="filename",
            mime_type="mime_type",
            purpose="assistants",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = await response.parse()
            assert_matches_type(Upload, upload, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_cancel(self, async_client: AsyncOpenAI) -> None:
        upload = await async_client.uploads.cancel(
            "upload_abc123",
        )
        assert_matches_type(Upload, upload, path=["response"])

    @parametrize
    async def test_raw_response_cancel(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.uploads.with_raw_response.cancel(
            "upload_abc123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = response.parse()
        assert_matches_type(Upload, upload, path=["response"])

    @parametrize
    async def test_streaming_response_cancel(self, async_client: AsyncOpenAI) -> None:
        async with async_client.uploads.with_streaming_response.cancel(
            "upload_abc123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = await response.parse()
            assert_matches_type(Upload, upload, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_cancel(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `upload_id` but received ''"):
            await async_client.uploads.with_raw_response.cancel(
                "",
            )

    @parametrize
    async def test_method_complete(self, async_client: AsyncOpenAI) -> None:
        upload = await async_client.uploads.complete(
            upload_id="upload_abc123",
            part_ids=["string", "string", "string"],
        )
        assert_matches_type(Upload, upload, path=["response"])

    @parametrize
    async def test_method_complete_with_all_params(self, async_client: AsyncOpenAI) -> None:
        upload = await async_client.uploads.complete(
            upload_id="upload_abc123",
            part_ids=["string", "string", "string"],
            md5="md5",
        )
        assert_matches_type(Upload, upload, path=["response"])

    @parametrize
    async def test_raw_response_complete(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.uploads.with_raw_response.complete(
            upload_id="upload_abc123",
            part_ids=["string", "string", "string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = response.parse()
        assert_matches_type(Upload, upload, path=["response"])

    @parametrize
    async def test_streaming_response_complete(self, async_client: AsyncOpenAI) -> None:
        async with async_client.uploads.with_streaming_response.complete(
            upload_id="upload_abc123",
            part_ids=["string", "string", "string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = await response.parse()
            assert_matches_type(Upload, upload, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_complete(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `upload_id` but received ''"):
            await async_client.uploads.with_raw_response.complete(
                upload_id="",
                part_ids=["string", "string", "string"],
            )
