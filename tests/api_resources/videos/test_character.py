# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types.videos import CharacterGetResponse, CharacterCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCharacter:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        character = client.videos.character.create(
            name="x",
            video=b"Example data",
        )
        assert_matches_type(CharacterCreateResponse, character, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.videos.character.with_raw_response.create(
            name="x",
            video=b"Example data",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        character = response.parse()
        assert_matches_type(CharacterCreateResponse, character, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.videos.character.with_streaming_response.create(
            name="x",
            video=b"Example data",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            character = response.parse()
            assert_matches_type(CharacterCreateResponse, character, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_get(self, client: OpenAI) -> None:
        character = client.videos.character.get(
            "char_123",
        )
        assert_matches_type(CharacterGetResponse, character, path=["response"])

    @parametrize
    def test_raw_response_get(self, client: OpenAI) -> None:
        response = client.videos.character.with_raw_response.get(
            "char_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        character = response.parse()
        assert_matches_type(CharacterGetResponse, character, path=["response"])

    @parametrize
    def test_streaming_response_get(self, client: OpenAI) -> None:
        with client.videos.character.with_streaming_response.get(
            "char_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            character = response.parse()
            assert_matches_type(CharacterGetResponse, character, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_get(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `character_id` but received ''"):
            client.videos.character.with_raw_response.get(
                "",
            )


class TestAsyncCharacter:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        character = await async_client.videos.character.create(
            name="x",
            video=b"Example data",
        )
        assert_matches_type(CharacterCreateResponse, character, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.videos.character.with_raw_response.create(
            name="x",
            video=b"Example data",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        character = response.parse()
        assert_matches_type(CharacterCreateResponse, character, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.videos.character.with_streaming_response.create(
            name="x",
            video=b"Example data",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            character = await response.parse()
            assert_matches_type(CharacterCreateResponse, character, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_get(self, async_client: AsyncOpenAI) -> None:
        character = await async_client.videos.character.get(
            "char_123",
        )
        assert_matches_type(CharacterGetResponse, character, path=["response"])

    @parametrize
    async def test_raw_response_get(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.videos.character.with_raw_response.get(
            "char_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        character = response.parse()
        assert_matches_type(CharacterGetResponse, character, path=["response"])

    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncOpenAI) -> None:
        async with async_client.videos.character.with_streaming_response.get(
            "char_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            character = await response.parse()
            assert_matches_type(CharacterGetResponse, character, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_get(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `character_id` but received ''"):
            await async_client.videos.character.with_raw_response.get(
                "",
            )
