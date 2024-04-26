# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncCursorPage, AsyncCursorPage
from openai.types.fine_tuning import (
    FineTuningJob,
    FineTuningJobEvent,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestJobs:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        job = client.fine_tuning.jobs.create(
            model="gpt-3.5-turbo",
            training_file="file-abc123",
        )
        assert_matches_type(FineTuningJob, job, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        job = client.fine_tuning.jobs.create(
            model="gpt-3.5-turbo",
            training_file="file-abc123",
            hyperparameters={
                "batch_size": "auto",
                "learning_rate_multiplier": "auto",
                "n_epochs": "auto",
            },
            integrations=[
                {
                    "type": "wandb",
                    "wandb": {
                        "project": "my-wandb-project",
                        "name": "string",
                        "entity": "string",
                        "tags": ["custom-tag", "custom-tag", "custom-tag"],
                    },
                },
                {
                    "type": "wandb",
                    "wandb": {
                        "project": "my-wandb-project",
                        "name": "string",
                        "entity": "string",
                        "tags": ["custom-tag", "custom-tag", "custom-tag"],
                    },
                },
                {
                    "type": "wandb",
                    "wandb": {
                        "project": "my-wandb-project",
                        "name": "string",
                        "entity": "string",
                        "tags": ["custom-tag", "custom-tag", "custom-tag"],
                    },
                },
            ],
            seed=42,
            suffix="x",
            validation_file="file-abc123",
        )
        assert_matches_type(FineTuningJob, job, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.fine_tuning.jobs.with_raw_response.create(
            model="gpt-3.5-turbo",
            training_file="file-abc123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = response.parse()
        assert_matches_type(FineTuningJob, job, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.fine_tuning.jobs.with_streaming_response.create(
            model="gpt-3.5-turbo",
            training_file="file-abc123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = response.parse()
            assert_matches_type(FineTuningJob, job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        job = client.fine_tuning.jobs.retrieve(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        )
        assert_matches_type(FineTuningJob, job, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.fine_tuning.jobs.with_raw_response.retrieve(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = response.parse()
        assert_matches_type(FineTuningJob, job, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.fine_tuning.jobs.with_streaming_response.retrieve(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = response.parse()
            assert_matches_type(FineTuningJob, job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `fine_tuning_job_id` but received ''"):
            client.fine_tuning.jobs.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        job = client.fine_tuning.jobs.list()
        assert_matches_type(SyncCursorPage[FineTuningJob], job, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        job = client.fine_tuning.jobs.list(
            after="string",
            limit=0,
        )
        assert_matches_type(SyncCursorPage[FineTuningJob], job, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.fine_tuning.jobs.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = response.parse()
        assert_matches_type(SyncCursorPage[FineTuningJob], job, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.fine_tuning.jobs.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = response.parse()
            assert_matches_type(SyncCursorPage[FineTuningJob], job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_cancel(self, client: OpenAI) -> None:
        job = client.fine_tuning.jobs.cancel(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        )
        assert_matches_type(FineTuningJob, job, path=["response"])

    @parametrize
    def test_raw_response_cancel(self, client: OpenAI) -> None:
        response = client.fine_tuning.jobs.with_raw_response.cancel(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = response.parse()
        assert_matches_type(FineTuningJob, job, path=["response"])

    @parametrize
    def test_streaming_response_cancel(self, client: OpenAI) -> None:
        with client.fine_tuning.jobs.with_streaming_response.cancel(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = response.parse()
            assert_matches_type(FineTuningJob, job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_cancel(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `fine_tuning_job_id` but received ''"):
            client.fine_tuning.jobs.with_raw_response.cancel(
                "",
            )

    @parametrize
    def test_method_list_events(self, client: OpenAI) -> None:
        job = client.fine_tuning.jobs.list_events(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        )
        assert_matches_type(SyncCursorPage[FineTuningJobEvent], job, path=["response"])

    @parametrize
    def test_method_list_events_with_all_params(self, client: OpenAI) -> None:
        job = client.fine_tuning.jobs.list_events(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
            after="string",
            limit=0,
        )
        assert_matches_type(SyncCursorPage[FineTuningJobEvent], job, path=["response"])

    @parametrize
    def test_raw_response_list_events(self, client: OpenAI) -> None:
        response = client.fine_tuning.jobs.with_raw_response.list_events(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = response.parse()
        assert_matches_type(SyncCursorPage[FineTuningJobEvent], job, path=["response"])

    @parametrize
    def test_streaming_response_list_events(self, client: OpenAI) -> None:
        with client.fine_tuning.jobs.with_streaming_response.list_events(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = response.parse()
            assert_matches_type(SyncCursorPage[FineTuningJobEvent], job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list_events(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `fine_tuning_job_id` but received ''"):
            client.fine_tuning.jobs.with_raw_response.list_events(
                "",
            )


class TestAsyncJobs:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        job = await async_client.fine_tuning.jobs.create(
            model="gpt-3.5-turbo",
            training_file="file-abc123",
        )
        assert_matches_type(FineTuningJob, job, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncOpenAI) -> None:
        job = await async_client.fine_tuning.jobs.create(
            model="gpt-3.5-turbo",
            training_file="file-abc123",
            hyperparameters={
                "batch_size": "auto",
                "learning_rate_multiplier": "auto",
                "n_epochs": "auto",
            },
            integrations=[
                {
                    "type": "wandb",
                    "wandb": {
                        "project": "my-wandb-project",
                        "name": "string",
                        "entity": "string",
                        "tags": ["custom-tag", "custom-tag", "custom-tag"],
                    },
                },
                {
                    "type": "wandb",
                    "wandb": {
                        "project": "my-wandb-project",
                        "name": "string",
                        "entity": "string",
                        "tags": ["custom-tag", "custom-tag", "custom-tag"],
                    },
                },
                {
                    "type": "wandb",
                    "wandb": {
                        "project": "my-wandb-project",
                        "name": "string",
                        "entity": "string",
                        "tags": ["custom-tag", "custom-tag", "custom-tag"],
                    },
                },
            ],
            seed=42,
            suffix="x",
            validation_file="file-abc123",
        )
        assert_matches_type(FineTuningJob, job, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.fine_tuning.jobs.with_raw_response.create(
            model="gpt-3.5-turbo",
            training_file="file-abc123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = response.parse()
        assert_matches_type(FineTuningJob, job, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.fine_tuning.jobs.with_streaming_response.create(
            model="gpt-3.5-turbo",
            training_file="file-abc123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = await response.parse()
            assert_matches_type(FineTuningJob, job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        job = await async_client.fine_tuning.jobs.retrieve(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        )
        assert_matches_type(FineTuningJob, job, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.fine_tuning.jobs.with_raw_response.retrieve(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = response.parse()
        assert_matches_type(FineTuningJob, job, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.fine_tuning.jobs.with_streaming_response.retrieve(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = await response.parse()
            assert_matches_type(FineTuningJob, job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `fine_tuning_job_id` but received ''"):
            await async_client.fine_tuning.jobs.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        job = await async_client.fine_tuning.jobs.list()
        assert_matches_type(AsyncCursorPage[FineTuningJob], job, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        job = await async_client.fine_tuning.jobs.list(
            after="string",
            limit=0,
        )
        assert_matches_type(AsyncCursorPage[FineTuningJob], job, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.fine_tuning.jobs.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = response.parse()
        assert_matches_type(AsyncCursorPage[FineTuningJob], job, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.fine_tuning.jobs.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = await response.parse()
            assert_matches_type(AsyncCursorPage[FineTuningJob], job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_cancel(self, async_client: AsyncOpenAI) -> None:
        job = await async_client.fine_tuning.jobs.cancel(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        )
        assert_matches_type(FineTuningJob, job, path=["response"])

    @parametrize
    async def test_raw_response_cancel(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.fine_tuning.jobs.with_raw_response.cancel(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = response.parse()
        assert_matches_type(FineTuningJob, job, path=["response"])

    @parametrize
    async def test_streaming_response_cancel(self, async_client: AsyncOpenAI) -> None:
        async with async_client.fine_tuning.jobs.with_streaming_response.cancel(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = await response.parse()
            assert_matches_type(FineTuningJob, job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_cancel(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `fine_tuning_job_id` but received ''"):
            await async_client.fine_tuning.jobs.with_raw_response.cancel(
                "",
            )

    @parametrize
    async def test_method_list_events(self, async_client: AsyncOpenAI) -> None:
        job = await async_client.fine_tuning.jobs.list_events(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        )
        assert_matches_type(AsyncCursorPage[FineTuningJobEvent], job, path=["response"])

    @parametrize
    async def test_method_list_events_with_all_params(self, async_client: AsyncOpenAI) -> None:
        job = await async_client.fine_tuning.jobs.list_events(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
            after="string",
            limit=0,
        )
        assert_matches_type(AsyncCursorPage[FineTuningJobEvent], job, path=["response"])

    @parametrize
    async def test_raw_response_list_events(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.fine_tuning.jobs.with_raw_response.list_events(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        job = response.parse()
        assert_matches_type(AsyncCursorPage[FineTuningJobEvent], job, path=["response"])

    @parametrize
    async def test_streaming_response_list_events(self, async_client: AsyncOpenAI) -> None:
        async with async_client.fine_tuning.jobs.with_streaming_response.list_events(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            job = await response.parse()
            assert_matches_type(AsyncCursorPage[FineTuningJobEvent], job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list_events(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `fine_tuning_job_id` but received ''"):
            await async_client.fine_tuning.jobs.with_raw_response.list_events(
                "",
            )
