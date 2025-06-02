# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types.fine_tuning.alpha import (
    GraderRunResponse,
    GraderValidateResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestGraders:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_run(self, client: OpenAI) -> None:
        grader = client.fine_tuning.alpha.graders.run(
            grader={
                "input": "input",
                "name": "name",
                "operation": "eq",
                "reference": "reference",
                "type": "string_check",
            },
            model_sample="model_sample",
        )
        assert_matches_type(GraderRunResponse, grader, path=["response"])

    @parametrize
    def test_method_run_with_all_params(self, client: OpenAI) -> None:
        grader = client.fine_tuning.alpha.graders.run(
            grader={
                "input": "input",
                "name": "name",
                "operation": "eq",
                "reference": "reference",
                "type": "string_check",
            },
            model_sample="model_sample",
            item={},
        )
        assert_matches_type(GraderRunResponse, grader, path=["response"])

    @parametrize
    def test_raw_response_run(self, client: OpenAI) -> None:
        response = client.fine_tuning.alpha.graders.with_raw_response.run(
            grader={
                "input": "input",
                "name": "name",
                "operation": "eq",
                "reference": "reference",
                "type": "string_check",
            },
            model_sample="model_sample",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        grader = response.parse()
        assert_matches_type(GraderRunResponse, grader, path=["response"])

    @parametrize
    def test_streaming_response_run(self, client: OpenAI) -> None:
        with client.fine_tuning.alpha.graders.with_streaming_response.run(
            grader={
                "input": "input",
                "name": "name",
                "operation": "eq",
                "reference": "reference",
                "type": "string_check",
            },
            model_sample="model_sample",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            grader = response.parse()
            assert_matches_type(GraderRunResponse, grader, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_validate(self, client: OpenAI) -> None:
        grader = client.fine_tuning.alpha.graders.validate(
            grader={
                "input": "input",
                "name": "name",
                "operation": "eq",
                "reference": "reference",
                "type": "string_check",
            },
        )
        assert_matches_type(GraderValidateResponse, grader, path=["response"])

    @parametrize
    def test_method_validate_with_all_params(self, client: OpenAI) -> None:
        grader = client.fine_tuning.alpha.graders.validate(
            grader={
                "input": "input",
                "name": "name",
                "operation": "eq",
                "reference": "reference",
                "type": "string_check",
            },
        )
        assert_matches_type(GraderValidateResponse, grader, path=["response"])

    @parametrize
    def test_raw_response_validate(self, client: OpenAI) -> None:
        response = client.fine_tuning.alpha.graders.with_raw_response.validate(
            grader={
                "input": "input",
                "name": "name",
                "operation": "eq",
                "reference": "reference",
                "type": "string_check",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        grader = response.parse()
        assert_matches_type(GraderValidateResponse, grader, path=["response"])

    @parametrize
    def test_streaming_response_validate(self, client: OpenAI) -> None:
        with client.fine_tuning.alpha.graders.with_streaming_response.validate(
            grader={
                "input": "input",
                "name": "name",
                "operation": "eq",
                "reference": "reference",
                "type": "string_check",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            grader = response.parse()
            assert_matches_type(GraderValidateResponse, grader, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncGraders:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_run(self, async_client: AsyncOpenAI) -> None:
        grader = await async_client.fine_tuning.alpha.graders.run(
            grader={
                "input": "input",
                "name": "name",
                "operation": "eq",
                "reference": "reference",
                "type": "string_check",
            },
            model_sample="model_sample",
        )
        assert_matches_type(GraderRunResponse, grader, path=["response"])

    @parametrize
    async def test_method_run_with_all_params(self, async_client: AsyncOpenAI) -> None:
        grader = await async_client.fine_tuning.alpha.graders.run(
            grader={
                "input": "input",
                "name": "name",
                "operation": "eq",
                "reference": "reference",
                "type": "string_check",
            },
            model_sample="model_sample",
            item={},
        )
        assert_matches_type(GraderRunResponse, grader, path=["response"])

    @parametrize
    async def test_raw_response_run(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.fine_tuning.alpha.graders.with_raw_response.run(
            grader={
                "input": "input",
                "name": "name",
                "operation": "eq",
                "reference": "reference",
                "type": "string_check",
            },
            model_sample="model_sample",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        grader = response.parse()
        assert_matches_type(GraderRunResponse, grader, path=["response"])

    @parametrize
    async def test_streaming_response_run(self, async_client: AsyncOpenAI) -> None:
        async with async_client.fine_tuning.alpha.graders.with_streaming_response.run(
            grader={
                "input": "input",
                "name": "name",
                "operation": "eq",
                "reference": "reference",
                "type": "string_check",
            },
            model_sample="model_sample",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            grader = await response.parse()
            assert_matches_type(GraderRunResponse, grader, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_validate(self, async_client: AsyncOpenAI) -> None:
        grader = await async_client.fine_tuning.alpha.graders.validate(
            grader={
                "input": "input",
                "name": "name",
                "operation": "eq",
                "reference": "reference",
                "type": "string_check",
            },
        )
        assert_matches_type(GraderValidateResponse, grader, path=["response"])

    @parametrize
    async def test_method_validate_with_all_params(self, async_client: AsyncOpenAI) -> None:
        grader = await async_client.fine_tuning.alpha.graders.validate(
            grader={
                "input": "input",
                "name": "name",
                "operation": "eq",
                "reference": "reference",
                "type": "string_check",
            },
        )
        assert_matches_type(GraderValidateResponse, grader, path=["response"])

    @parametrize
    async def test_raw_response_validate(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.fine_tuning.alpha.graders.with_raw_response.validate(
            grader={
                "input": "input",
                "name": "name",
                "operation": "eq",
                "reference": "reference",
                "type": "string_check",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        grader = response.parse()
        assert_matches_type(GraderValidateResponse, grader, path=["response"])

    @parametrize
    async def test_streaming_response_validate(self, async_client: AsyncOpenAI) -> None:
        async with async_client.fine_tuning.alpha.graders.with_streaming_response.validate(
            grader={
                "input": "input",
                "name": "name",
                "operation": "eq",
                "reference": "reference",
                "type": "string_check",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            grader = await response.parse()
            assert_matches_type(GraderValidateResponse, grader, path=["response"])

        assert cast(Any, response.is_closed) is True
