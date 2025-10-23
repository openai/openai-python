# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types import ImagesResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestImages:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create_variation(self, client: OpenAI) -> None:
        image = client.images.create_variation(
            image=b"raw file contents",
        )
        assert_matches_type(ImagesResponse, image, path=["response"])

    @parametrize
    def test_method_create_variation_with_all_params(self, client: OpenAI) -> None:
        image = client.images.create_variation(
            image=b"raw file contents",
            model="string",
            n=1,
            response_format="url",
            size="1024x1024",
            user="user-1234",
        )
        assert_matches_type(ImagesResponse, image, path=["response"])

    @parametrize
    def test_raw_response_create_variation(self, client: OpenAI) -> None:
        response = client.images.with_raw_response.create_variation(
            image=b"raw file contents",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        image = response.parse()
        assert_matches_type(ImagesResponse, image, path=["response"])

    @parametrize
    def test_streaming_response_create_variation(self, client: OpenAI) -> None:
        with client.images.with_streaming_response.create_variation(
            image=b"raw file contents",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            image = response.parse()
            assert_matches_type(ImagesResponse, image, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_edit_overload_1(self, client: OpenAI) -> None:
        image = client.images.edit(
            image=b"raw file contents",
            prompt="A cute baby sea otter wearing a beret",
        )
        assert_matches_type(ImagesResponse, image, path=["response"])

    @parametrize
    def test_method_edit_with_all_params_overload_1(self, client: OpenAI) -> None:
        image = client.images.edit(
            image=b"raw file contents",
            prompt="A cute baby sea otter wearing a beret",
            background="transparent",
            input_fidelity="high",
            mask=b"raw file contents",
            model="string",
            n=1,
            output_compression=100,
            output_format="png",
            partial_images=1,
            quality="high",
            response_format="url",
            size="1024x1024",
            stream=False,
            user="user-1234",
        )
        assert_matches_type(ImagesResponse, image, path=["response"])

    @parametrize
    def test_raw_response_edit_overload_1(self, client: OpenAI) -> None:
        response = client.images.with_raw_response.edit(
            image=b"raw file contents",
            prompt="A cute baby sea otter wearing a beret",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        image = response.parse()
        assert_matches_type(ImagesResponse, image, path=["response"])

    @parametrize
    def test_streaming_response_edit_overload_1(self, client: OpenAI) -> None:
        with client.images.with_streaming_response.edit(
            image=b"raw file contents",
            prompt="A cute baby sea otter wearing a beret",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            image = response.parse()
            assert_matches_type(ImagesResponse, image, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_edit_overload_2(self, client: OpenAI) -> None:
        image_stream = client.images.edit(
            image=b"raw file contents",
            prompt="A cute baby sea otter wearing a beret",
            stream=True,
        )
        image_stream.response.close()

    @parametrize
    def test_method_edit_with_all_params_overload_2(self, client: OpenAI) -> None:
        image_stream = client.images.edit(
            image=b"raw file contents",
            prompt="A cute baby sea otter wearing a beret",
            stream=True,
            background="transparent",
            input_fidelity="high",
            mask=b"raw file contents",
            model="string",
            n=1,
            output_compression=100,
            output_format="png",
            partial_images=1,
            quality="high",
            response_format="url",
            size="1024x1024",
            user="user-1234",
        )
        image_stream.response.close()

    @parametrize
    def test_raw_response_edit_overload_2(self, client: OpenAI) -> None:
        response = client.images.with_raw_response.edit(
            image=b"raw file contents",
            prompt="A cute baby sea otter wearing a beret",
            stream=True,
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = response.parse()
        stream.close()

    @parametrize
    def test_streaming_response_edit_overload_2(self, client: OpenAI) -> None:
        with client.images.with_streaming_response.edit(
            image=b"raw file contents",
            prompt="A cute baby sea otter wearing a beret",
            stream=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = response.parse()
            stream.close()

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_generate_overload_1(self, client: OpenAI) -> None:
        image = client.images.generate(
            prompt="A cute baby sea otter",
        )
        assert_matches_type(ImagesResponse, image, path=["response"])

    @parametrize
    def test_method_generate_with_all_params_overload_1(self, client: OpenAI) -> None:
        image = client.images.generate(
            prompt="A cute baby sea otter",
            background="transparent",
            model="string",
            moderation="low",
            n=1,
            output_compression=100,
            output_format="png",
            partial_images=1,
            quality="medium",
            response_format="url",
            size="1024x1024",
            stream=False,
            style="vivid",
            user="user-1234",
        )
        assert_matches_type(ImagesResponse, image, path=["response"])

    @parametrize
    def test_raw_response_generate_overload_1(self, client: OpenAI) -> None:
        response = client.images.with_raw_response.generate(
            prompt="A cute baby sea otter",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        image = response.parse()
        assert_matches_type(ImagesResponse, image, path=["response"])

    @parametrize
    def test_streaming_response_generate_overload_1(self, client: OpenAI) -> None:
        with client.images.with_streaming_response.generate(
            prompt="A cute baby sea otter",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            image = response.parse()
            assert_matches_type(ImagesResponse, image, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_generate_overload_2(self, client: OpenAI) -> None:
        image_stream = client.images.generate(
            prompt="A cute baby sea otter",
            stream=True,
        )
        image_stream.response.close()

    @parametrize
    def test_method_generate_with_all_params_overload_2(self, client: OpenAI) -> None:
        image_stream = client.images.generate(
            prompt="A cute baby sea otter",
            stream=True,
            background="transparent",
            model="string",
            moderation="low",
            n=1,
            output_compression=100,
            output_format="png",
            partial_images=1,
            quality="medium",
            response_format="url",
            size="1024x1024",
            style="vivid",
            user="user-1234",
        )
        image_stream.response.close()

    @parametrize
    def test_raw_response_generate_overload_2(self, client: OpenAI) -> None:
        response = client.images.with_raw_response.generate(
            prompt="A cute baby sea otter",
            stream=True,
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = response.parse()
        stream.close()

    @parametrize
    def test_streaming_response_generate_overload_2(self, client: OpenAI) -> None:
        with client.images.with_streaming_response.generate(
            prompt="A cute baby sea otter",
            stream=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = response.parse()
            stream.close()

        assert cast(Any, response.is_closed) is True


class TestAsyncImages:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create_variation(self, async_client: AsyncOpenAI) -> None:
        image = await async_client.images.create_variation(
            image=b"raw file contents",
        )
        assert_matches_type(ImagesResponse, image, path=["response"])

    @parametrize
    async def test_method_create_variation_with_all_params(self, async_client: AsyncOpenAI) -> None:
        image = await async_client.images.create_variation(
            image=b"raw file contents",
            model="string",
            n=1,
            response_format="url",
            size="1024x1024",
            user="user-1234",
        )
        assert_matches_type(ImagesResponse, image, path=["response"])

    @parametrize
    async def test_raw_response_create_variation(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.images.with_raw_response.create_variation(
            image=b"raw file contents",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        image = response.parse()
        assert_matches_type(ImagesResponse, image, path=["response"])

    @parametrize
    async def test_streaming_response_create_variation(self, async_client: AsyncOpenAI) -> None:
        async with async_client.images.with_streaming_response.create_variation(
            image=b"raw file contents",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            image = await response.parse()
            assert_matches_type(ImagesResponse, image, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_edit_overload_1(self, async_client: AsyncOpenAI) -> None:
        image = await async_client.images.edit(
            image=b"raw file contents",
            prompt="A cute baby sea otter wearing a beret",
        )
        assert_matches_type(ImagesResponse, image, path=["response"])

    @parametrize
    async def test_method_edit_with_all_params_overload_1(self, async_client: AsyncOpenAI) -> None:
        image = await async_client.images.edit(
            image=b"raw file contents",
            prompt="A cute baby sea otter wearing a beret",
            background="transparent",
            input_fidelity="high",
            mask=b"raw file contents",
            model="string",
            n=1,
            output_compression=100,
            output_format="png",
            partial_images=1,
            quality="high",
            response_format="url",
            size="1024x1024",
            stream=False,
            user="user-1234",
        )
        assert_matches_type(ImagesResponse, image, path=["response"])

    @parametrize
    async def test_raw_response_edit_overload_1(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.images.with_raw_response.edit(
            image=b"raw file contents",
            prompt="A cute baby sea otter wearing a beret",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        image = response.parse()
        assert_matches_type(ImagesResponse, image, path=["response"])

    @parametrize
    async def test_streaming_response_edit_overload_1(self, async_client: AsyncOpenAI) -> None:
        async with async_client.images.with_streaming_response.edit(
            image=b"raw file contents",
            prompt="A cute baby sea otter wearing a beret",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            image = await response.parse()
            assert_matches_type(ImagesResponse, image, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_edit_overload_2(self, async_client: AsyncOpenAI) -> None:
        image_stream = await async_client.images.edit(
            image=b"raw file contents",
            prompt="A cute baby sea otter wearing a beret",
            stream=True,
        )
        await image_stream.response.aclose()

    @parametrize
    async def test_method_edit_with_all_params_overload_2(self, async_client: AsyncOpenAI) -> None:
        image_stream = await async_client.images.edit(
            image=b"raw file contents",
            prompt="A cute baby sea otter wearing a beret",
            stream=True,
            background="transparent",
            input_fidelity="high",
            mask=b"raw file contents",
            model="string",
            n=1,
            output_compression=100,
            output_format="png",
            partial_images=1,
            quality="high",
            response_format="url",
            size="1024x1024",
            user="user-1234",
        )
        await image_stream.response.aclose()

    @parametrize
    async def test_raw_response_edit_overload_2(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.images.with_raw_response.edit(
            image=b"raw file contents",
            prompt="A cute baby sea otter wearing a beret",
            stream=True,
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = response.parse()
        await stream.close()

    @parametrize
    async def test_streaming_response_edit_overload_2(self, async_client: AsyncOpenAI) -> None:
        async with async_client.images.with_streaming_response.edit(
            image=b"raw file contents",
            prompt="A cute baby sea otter wearing a beret",
            stream=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = await response.parse()
            await stream.close()

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_generate_overload_1(self, async_client: AsyncOpenAI) -> None:
        image = await async_client.images.generate(
            prompt="A cute baby sea otter",
        )
        assert_matches_type(ImagesResponse, image, path=["response"])

    @parametrize
    async def test_method_generate_with_all_params_overload_1(self, async_client: AsyncOpenAI) -> None:
        image = await async_client.images.generate(
            prompt="A cute baby sea otter",
            background="transparent",
            model="string",
            moderation="low",
            n=1,
            output_compression=100,
            output_format="png",
            partial_images=1,
            quality="medium",
            response_format="url",
            size="1024x1024",
            stream=False,
            style="vivid",
            user="user-1234",
        )
        assert_matches_type(ImagesResponse, image, path=["response"])

    @parametrize
    async def test_raw_response_generate_overload_1(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.images.with_raw_response.generate(
            prompt="A cute baby sea otter",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        image = response.parse()
        assert_matches_type(ImagesResponse, image, path=["response"])

    @parametrize
    async def test_streaming_response_generate_overload_1(self, async_client: AsyncOpenAI) -> None:
        async with async_client.images.with_streaming_response.generate(
            prompt="A cute baby sea otter",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            image = await response.parse()
            assert_matches_type(ImagesResponse, image, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_generate_overload_2(self, async_client: AsyncOpenAI) -> None:
        image_stream = await async_client.images.generate(
            prompt="A cute baby sea otter",
            stream=True,
        )
        await image_stream.response.aclose()

    @parametrize
    async def test_method_generate_with_all_params_overload_2(self, async_client: AsyncOpenAI) -> None:
        image_stream = await async_client.images.generate(
            prompt="A cute baby sea otter",
            stream=True,
            background="transparent",
            model="string",
            moderation="low",
            n=1,
            output_compression=100,
            output_format="png",
            partial_images=1,
            quality="medium",
            response_format="url",
            size="1024x1024",
            style="vivid",
            user="user-1234",
        )
        await image_stream.response.aclose()

    @parametrize
    async def test_raw_response_generate_overload_2(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.images.with_raw_response.generate(
            prompt="A cute baby sea otter",
            stream=True,
        )

        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream = response.parse()
        await stream.close()

    @parametrize
    async def test_streaming_response_generate_overload_2(self, async_client: AsyncOpenAI) -> None:
        async with async_client.images.with_streaming_response.generate(
            prompt="A cute baby sea otter",
            stream=True,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream = await response.parse()
            await stream.close()

        assert cast(Any, response.is_closed) is True
