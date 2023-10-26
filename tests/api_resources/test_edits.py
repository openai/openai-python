# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

import os

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types import Edit
from openai._client import OpenAI, AsyncOpenAI

# pyright: reportDeprecated=false

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")
api_key = "My API Key"


class TestEdits:
    strict_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
    loose_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)
    parametrize = pytest.mark.parametrize("client", [strict_client, loose_client], ids=["strict", "loose"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        with pytest.warns(DeprecationWarning):
            edit = client.edits.create(
                instruction="Fix the spelling mistakes.",
                model="text-davinci-edit-001",
            )
        assert_matches_type(Edit, edit, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        with pytest.warns(DeprecationWarning):
            edit = client.edits.create(
                instruction="Fix the spelling mistakes.",
                model="text-davinci-edit-001",
                input="What day of the wek is it?",
                n=1,
                temperature=1,
                top_p=1,
            )
        assert_matches_type(Edit, edit, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        with pytest.warns(DeprecationWarning):
            response = client.edits.with_raw_response.create(
                instruction="Fix the spelling mistakes.",
                model="text-davinci-edit-001",
            )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        edit = response.parse()
        assert_matches_type(Edit, edit, path=["response"])


class TestAsyncEdits:
    strict_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
    loose_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)
    parametrize = pytest.mark.parametrize("client", [strict_client, loose_client], ids=["strict", "loose"])

    @parametrize
    async def test_method_create(self, client: AsyncOpenAI) -> None:
        with pytest.warns(DeprecationWarning):
            edit = await client.edits.create(
                instruction="Fix the spelling mistakes.",
                model="text-davinci-edit-001",
            )
        assert_matches_type(Edit, edit, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, client: AsyncOpenAI) -> None:
        with pytest.warns(DeprecationWarning):
            edit = await client.edits.create(
                instruction="Fix the spelling mistakes.",
                model="text-davinci-edit-001",
                input="What day of the wek is it?",
                n=1,
                temperature=1,
                top_p=1,
            )
        assert_matches_type(Edit, edit, path=["response"])

    @parametrize
    async def test_raw_response_create(self, client: AsyncOpenAI) -> None:
        with pytest.warns(DeprecationWarning):
            response = await client.edits.with_raw_response.create(
                instruction="Fix the spelling mistakes.",
                model="text-davinci-edit-001",
            )
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        edit = response.parse()
        assert_matches_type(Edit, edit, path=["response"])
