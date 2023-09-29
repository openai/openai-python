# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

import os

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types import Model, ModelDeleted
from openai.pagination import SyncPage, AsyncPage

base_url = os.environ.get("API_BASE_URL", "http://127.0.0.1:4010")
api_key = os.environ.get("API_KEY", "something1234")


class TestModels:
    strict_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
    loose_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)
    parametrize = pytest.mark.parametrize("client", [strict_client, loose_client], ids=["strict", "loose"])

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        model = client.models.retrieve(
            "gpt-3.5-turbo",
        )
        assert_matches_type(Model, model, path=["response"])

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        model = client.models.list()
        assert_matches_type(SyncPage[Model], model, path=["response"])

    @parametrize
    def test_method_delete(self, client: OpenAI) -> None:
        model = client.models.delete(
            "ft:gpt-3.5-turbo:acemeco:suffix:abc123",
        )
        assert_matches_type(ModelDeleted, model, path=["response"])


class TestAsyncModels:
    strict_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
    loose_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)
    parametrize = pytest.mark.parametrize("client", [strict_client, loose_client], ids=["strict", "loose"])

    @parametrize
    async def test_method_retrieve(self, client: AsyncOpenAI) -> None:
        model = await client.models.retrieve(
            "gpt-3.5-turbo",
        )
        assert_matches_type(Model, model, path=["response"])

    @parametrize
    async def test_method_list(self, client: AsyncOpenAI) -> None:
        model = await client.models.list()
        assert_matches_type(AsyncPage[Model], model, path=["response"])

    @parametrize
    async def test_method_delete(self, client: AsyncOpenAI) -> None:
        model = await client.models.delete(
            "ft:gpt-3.5-turbo:acemeco:suffix:abc123",
        )
        assert_matches_type(ModelDeleted, model, path=["response"])
