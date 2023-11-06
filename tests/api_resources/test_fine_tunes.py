# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

import os

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types import FineTune, FineTuneEventsListResponse
from openai._client import OpenAI, AsyncOpenAI
from openai.pagination import SyncPage, AsyncPage

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")
api_key = "My API Key"


class TestFineTunes:
    strict_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
    loose_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)
    parametrize = pytest.mark.parametrize("client", [strict_client, loose_client], ids=["strict", "loose"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        fine_tune = client.fine_tunes.create(
            training_file="file-abc123",
        )
        assert_matches_type(FineTune, fine_tune, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        fine_tune = client.fine_tunes.create(
            training_file="file-abc123",
            batch_size=0,
            classification_betas=[0.6, 1, 1.5, 2],
            classification_n_classes=0,
            classification_positive_class="string",
            compute_classification_metrics=True,
            hyperparameters={"n_epochs": "auto"},
            learning_rate_multiplier=0,
            model="curie",
            prompt_loss_weight=0,
            suffix="x",
            validation_file="file-abc123",
        )
        assert_matches_type(FineTune, fine_tune, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.fine_tunes.with_raw_response.create(
            training_file="file-abc123",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tune = response.parse()
        assert_matches_type(FineTune, fine_tune, path=["response"])

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        fine_tune = client.fine_tunes.retrieve(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        )
        assert_matches_type(FineTune, fine_tune, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.fine_tunes.with_raw_response.retrieve(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tune = response.parse()
        assert_matches_type(FineTune, fine_tune, path=["response"])

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        fine_tune = client.fine_tunes.list()
        assert_matches_type(SyncPage[FineTune], fine_tune, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.fine_tunes.with_raw_response.list()
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tune = response.parse()
        assert_matches_type(SyncPage[FineTune], fine_tune, path=["response"])

    @parametrize
    def test_method_cancel(self, client: OpenAI) -> None:
        fine_tune = client.fine_tunes.cancel(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        )
        assert_matches_type(FineTune, fine_tune, path=["response"])

    @parametrize
    def test_raw_response_cancel(self, client: OpenAI) -> None:
        response = client.fine_tunes.with_raw_response.cancel(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tune = response.parse()
        assert_matches_type(FineTune, fine_tune, path=["response"])

    @pytest.mark.skip(reason="Prism chokes on this")
    @parametrize
    def test_method_list_events_overload_1(self, client: OpenAI) -> None:
        fine_tune = client.fine_tunes.list_events(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        )
        assert_matches_type(FineTuneEventsListResponse, fine_tune, path=["response"])

    @pytest.mark.skip(reason="Prism chokes on this")
    @parametrize
    def test_method_list_events_with_all_params_overload_1(self, client: OpenAI) -> None:
        fine_tune = client.fine_tunes.list_events(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
            stream=False,
        )
        assert_matches_type(FineTuneEventsListResponse, fine_tune, path=["response"])

    @pytest.mark.skip(reason="Prism chokes on this")
    @parametrize
    def test_raw_response_list_events_overload_1(self, client: OpenAI) -> None:
        response = client.fine_tunes.with_raw_response.list_events(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tune = response.parse()
        assert_matches_type(FineTuneEventsListResponse, fine_tune, path=["response"])

    @pytest.mark.skip(reason="Prism chokes on this")
    @parametrize
    def test_method_list_events_overload_2(self, client: OpenAI) -> None:
        client.fine_tunes.list_events(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
            stream=True,
        )

    @pytest.mark.skip(reason="Prism chokes on this")
    @parametrize
    def test_raw_response_list_events_overload_2(self, client: OpenAI) -> None:
        response = client.fine_tunes.with_raw_response.list_events(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
            stream=True,
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        response.parse()


class TestAsyncFineTunes:
    strict_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
    loose_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)
    parametrize = pytest.mark.parametrize("client", [strict_client, loose_client], ids=["strict", "loose"])

    @parametrize
    async def test_method_create(self, client: AsyncOpenAI) -> None:
        fine_tune = await client.fine_tunes.create(
            training_file="file-abc123",
        )
        assert_matches_type(FineTune, fine_tune, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, client: AsyncOpenAI) -> None:
        fine_tune = await client.fine_tunes.create(
            training_file="file-abc123",
            batch_size=0,
            classification_betas=[0.6, 1, 1.5, 2],
            classification_n_classes=0,
            classification_positive_class="string",
            compute_classification_metrics=True,
            hyperparameters={"n_epochs": "auto"},
            learning_rate_multiplier=0,
            model="curie",
            prompt_loss_weight=0,
            suffix="x",
            validation_file="file-abc123",
        )
        assert_matches_type(FineTune, fine_tune, path=["response"])

    @parametrize
    async def test_raw_response_create(self, client: AsyncOpenAI) -> None:
        response = await client.fine_tunes.with_raw_response.create(
            training_file="file-abc123",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tune = response.parse()
        assert_matches_type(FineTune, fine_tune, path=["response"])

    @parametrize
    async def test_method_retrieve(self, client: AsyncOpenAI) -> None:
        fine_tune = await client.fine_tunes.retrieve(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        )
        assert_matches_type(FineTune, fine_tune, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, client: AsyncOpenAI) -> None:
        response = await client.fine_tunes.with_raw_response.retrieve(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tune = response.parse()
        assert_matches_type(FineTune, fine_tune, path=["response"])

    @parametrize
    async def test_method_list(self, client: AsyncOpenAI) -> None:
        fine_tune = await client.fine_tunes.list()
        assert_matches_type(AsyncPage[FineTune], fine_tune, path=["response"])

    @parametrize
    async def test_raw_response_list(self, client: AsyncOpenAI) -> None:
        response = await client.fine_tunes.with_raw_response.list()
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tune = response.parse()
        assert_matches_type(AsyncPage[FineTune], fine_tune, path=["response"])

    @parametrize
    async def test_method_cancel(self, client: AsyncOpenAI) -> None:
        fine_tune = await client.fine_tunes.cancel(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        )
        assert_matches_type(FineTune, fine_tune, path=["response"])

    @parametrize
    async def test_raw_response_cancel(self, client: AsyncOpenAI) -> None:
        response = await client.fine_tunes.with_raw_response.cancel(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tune = response.parse()
        assert_matches_type(FineTune, fine_tune, path=["response"])

    @pytest.mark.skip(reason="Prism chokes on this")
    @parametrize
    async def test_method_list_events_overload_1(self, client: AsyncOpenAI) -> None:
        fine_tune = await client.fine_tunes.list_events(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        )
        assert_matches_type(FineTuneEventsListResponse, fine_tune, path=["response"])

    @pytest.mark.skip(reason="Prism chokes on this")
    @parametrize
    async def test_method_list_events_with_all_params_overload_1(self, client: AsyncOpenAI) -> None:
        fine_tune = await client.fine_tunes.list_events(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
            stream=False,
        )
        assert_matches_type(FineTuneEventsListResponse, fine_tune, path=["response"])

    @pytest.mark.skip(reason="Prism chokes on this")
    @parametrize
    async def test_raw_response_list_events_overload_1(self, client: AsyncOpenAI) -> None:
        response = await client.fine_tunes.with_raw_response.list_events(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tune = response.parse()
        assert_matches_type(FineTuneEventsListResponse, fine_tune, path=["response"])

    @pytest.mark.skip(reason="Prism chokes on this")
    @parametrize
    async def test_method_list_events_overload_2(self, client: AsyncOpenAI) -> None:
        await client.fine_tunes.list_events(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
            stream=True,
        )

    @pytest.mark.skip(reason="Prism chokes on this")
    @parametrize
    async def test_raw_response_list_events_overload_2(self, client: AsyncOpenAI) -> None:
        response = await client.fine_tunes.with_raw_response.list_events(
            "ft-AF1WoRqd3aJAHsqc9NY7iL8F",
            stream=True,
        )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        response.parse()
