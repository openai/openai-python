# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types import ContentProvenanceCheck

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestContentProvenanceChecks:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        content_provenance_check = client.content_provenance_checks.create(
            file=b"Example data",
        )
        assert_matches_type(ContentProvenanceCheck, content_provenance_check, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.content_provenance_checks.with_raw_response.create(
            file=b"Example data",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        content_provenance_check = response.parse()
        assert_matches_type(ContentProvenanceCheck, content_provenance_check, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.content_provenance_checks.with_streaming_response.create(
            file=b"Example data",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            content_provenance_check = response.parse()
            assert_matches_type(ContentProvenanceCheck, content_provenance_check, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncContentProvenanceChecks:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        content_provenance_check = await async_client.content_provenance_checks.create(
            file=b"Example data",
        )
        assert_matches_type(ContentProvenanceCheck, content_provenance_check, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.content_provenance_checks.with_raw_response.create(
            file=b"Example data",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        content_provenance_check = response.parse()
        assert_matches_type(ContentProvenanceCheck, content_provenance_check, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.content_provenance_checks.with_streaming_response.create(
            file=b"Example data",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            content_provenance_check = await response.parse()
            assert_matches_type(ContentProvenanceCheck, content_provenance_check, path=["response"])

        assert cast(Any, response.is_closed) is True
