# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncCursorPage, AsyncCursorPage
from openai.types.evals.runs import OutputItemListResponse, OutputItemRetrieveResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestOutputItems:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        output_item = client.evals.runs.output_items.retrieve(
            output_item_id="output_item_id",
            eval_id="eval_id",
            run_id="run_id",
        )
        assert_matches_type(OutputItemRetrieveResponse, output_item, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.evals.runs.output_items.with_raw_response.retrieve(
            output_item_id="output_item_id",
            eval_id="eval_id",
            run_id="run_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        output_item = response.parse()
        assert_matches_type(OutputItemRetrieveResponse, output_item, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.evals.runs.output_items.with_streaming_response.retrieve(
            output_item_id="output_item_id",
            eval_id="eval_id",
            run_id="run_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            output_item = response.parse()
            assert_matches_type(OutputItemRetrieveResponse, output_item, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `eval_id` but received ''"):
            client.evals.runs.output_items.with_raw_response.retrieve(
                output_item_id="output_item_id",
                eval_id="",
                run_id="run_id",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `run_id` but received ''"):
            client.evals.runs.output_items.with_raw_response.retrieve(
                output_item_id="output_item_id",
                eval_id="eval_id",
                run_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `output_item_id` but received ''"):
            client.evals.runs.output_items.with_raw_response.retrieve(
                output_item_id="",
                eval_id="eval_id",
                run_id="run_id",
            )

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        output_item = client.evals.runs.output_items.list(
            run_id="run_id",
            eval_id="eval_id",
        )
        assert_matches_type(SyncCursorPage[OutputItemListResponse], output_item, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        output_item = client.evals.runs.output_items.list(
            run_id="run_id",
            eval_id="eval_id",
            after="after",
            limit=0,
            order="asc",
            status="fail",
        )
        assert_matches_type(SyncCursorPage[OutputItemListResponse], output_item, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.evals.runs.output_items.with_raw_response.list(
            run_id="run_id",
            eval_id="eval_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        output_item = response.parse()
        assert_matches_type(SyncCursorPage[OutputItemListResponse], output_item, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.evals.runs.output_items.with_streaming_response.list(
            run_id="run_id",
            eval_id="eval_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            output_item = response.parse()
            assert_matches_type(SyncCursorPage[OutputItemListResponse], output_item, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `eval_id` but received ''"):
            client.evals.runs.output_items.with_raw_response.list(
                run_id="run_id",
                eval_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `run_id` but received ''"):
            client.evals.runs.output_items.with_raw_response.list(
                run_id="",
                eval_id="eval_id",
            )


class TestAsyncOutputItems:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        output_item = await async_client.evals.runs.output_items.retrieve(
            output_item_id="output_item_id",
            eval_id="eval_id",
            run_id="run_id",
        )
        assert_matches_type(OutputItemRetrieveResponse, output_item, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.evals.runs.output_items.with_raw_response.retrieve(
            output_item_id="output_item_id",
            eval_id="eval_id",
            run_id="run_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        output_item = response.parse()
        assert_matches_type(OutputItemRetrieveResponse, output_item, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.evals.runs.output_items.with_streaming_response.retrieve(
            output_item_id="output_item_id",
            eval_id="eval_id",
            run_id="run_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            output_item = await response.parse()
            assert_matches_type(OutputItemRetrieveResponse, output_item, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `eval_id` but received ''"):
            await async_client.evals.runs.output_items.with_raw_response.retrieve(
                output_item_id="output_item_id",
                eval_id="",
                run_id="run_id",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `run_id` but received ''"):
            await async_client.evals.runs.output_items.with_raw_response.retrieve(
                output_item_id="output_item_id",
                eval_id="eval_id",
                run_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `output_item_id` but received ''"):
            await async_client.evals.runs.output_items.with_raw_response.retrieve(
                output_item_id="",
                eval_id="eval_id",
                run_id="run_id",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        output_item = await async_client.evals.runs.output_items.list(
            run_id="run_id",
            eval_id="eval_id",
        )
        assert_matches_type(AsyncCursorPage[OutputItemListResponse], output_item, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        output_item = await async_client.evals.runs.output_items.list(
            run_id="run_id",
            eval_id="eval_id",
            after="after",
            limit=0,
            order="asc",
            status="fail",
        )
        assert_matches_type(AsyncCursorPage[OutputItemListResponse], output_item, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.evals.runs.output_items.with_raw_response.list(
            run_id="run_id",
            eval_id="eval_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        output_item = response.parse()
        assert_matches_type(AsyncCursorPage[OutputItemListResponse], output_item, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.evals.runs.output_items.with_streaming_response.list(
            run_id="run_id",
            eval_id="eval_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            output_item = await response.parse()
            assert_matches_type(AsyncCursorPage[OutputItemListResponse], output_item, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `eval_id` but received ''"):
            await async_client.evals.runs.output_items.with_raw_response.list(
                run_id="run_id",
                eval_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `run_id` but received ''"):
            await async_client.evals.runs.output_items.with_raw_response.list(
                run_id="",
                eval_id="eval_id",
            )
