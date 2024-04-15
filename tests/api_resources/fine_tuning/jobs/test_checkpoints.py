# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncCursorPage, AsyncCursorPage
from openai.types.fine_tuning.jobs import FineTuningJobCheckpoint

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCheckpoints:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        checkpoint = client.fine_tuning.jobs.checkpoints.list(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        )
        assert_matches_type(SyncCursorPage[FineTuningJobCheckpoint], checkpoint, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        checkpoint = client.fine_tuning.jobs.checkpoints.list(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
            after="string",
            limit=0,
        )
        assert_matches_type(SyncCursorPage[FineTuningJobCheckpoint], checkpoint, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.fine_tuning.jobs.checkpoints.with_raw_response.list(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        checkpoint = response.parse()
        assert_matches_type(SyncCursorPage[FineTuningJobCheckpoint], checkpoint, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.fine_tuning.jobs.checkpoints.with_streaming_response.list(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            checkpoint = response.parse()
            assert_matches_type(SyncCursorPage[FineTuningJobCheckpoint], checkpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `fine_tuning_job_id` but received ''"):
            client.fine_tuning.jobs.checkpoints.with_raw_response.list(
                "",
            )


class TestAsyncCheckpoints:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        checkpoint = await async_client.fine_tuning.jobs.checkpoints.list(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        )
        assert_matches_type(AsyncCursorPage[FineTuningJobCheckpoint], checkpoint, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        checkpoint = await async_client.fine_tuning.jobs.checkpoints.list(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
            after="string",
            limit=0,
        )
        assert_matches_type(AsyncCursorPage[FineTuningJobCheckpoint], checkpoint, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.fine_tuning.jobs.checkpoints.with_raw_response.list(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        checkpoint = response.parse()
        assert_matches_type(AsyncCursorPage[FineTuningJobCheckpoint], checkpoint, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.fine_tuning.jobs.checkpoints.with_streaming_response.list(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            checkpoint = await response.parse()
            assert_matches_type(AsyncCursorPage[FineTuningJobCheckpoint], checkpoint, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `fine_tuning_job_id` but received ''"):
            await async_client.fine_tuning.jobs.checkpoints.with_raw_response.list(
                "",
            )
