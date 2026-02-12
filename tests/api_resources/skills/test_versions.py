# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncCursorPage, AsyncCursorPage
from openai.types.skills import SkillVersion, DeletedSkillVersion

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestVersions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        version = client.skills.versions.create(
            skill_id="skill_123",
        )
        assert_matches_type(SkillVersion, version, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        version = client.skills.versions.create(
            skill_id="skill_123",
            default=True,
            files=[b"raw file contents"],
        )
        assert_matches_type(SkillVersion, version, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.skills.versions.with_raw_response.create(
            skill_id="skill_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        version = response.parse()
        assert_matches_type(SkillVersion, version, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.skills.versions.with_streaming_response.create(
            skill_id="skill_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            version = response.parse()
            assert_matches_type(SkillVersion, version, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `skill_id` but received ''"):
            client.skills.versions.with_raw_response.create(
                skill_id="",
            )

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        version = client.skills.versions.retrieve(
            version="version",
            skill_id="skill_123",
        )
        assert_matches_type(SkillVersion, version, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.skills.versions.with_raw_response.retrieve(
            version="version",
            skill_id="skill_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        version = response.parse()
        assert_matches_type(SkillVersion, version, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.skills.versions.with_streaming_response.retrieve(
            version="version",
            skill_id="skill_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            version = response.parse()
            assert_matches_type(SkillVersion, version, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `skill_id` but received ''"):
            client.skills.versions.with_raw_response.retrieve(
                version="version",
                skill_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `version` but received ''"):
            client.skills.versions.with_raw_response.retrieve(
                version="",
                skill_id="skill_123",
            )

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        version = client.skills.versions.list(
            skill_id="skill_123",
        )
        assert_matches_type(SyncCursorPage[SkillVersion], version, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        version = client.skills.versions.list(
            skill_id="skill_123",
            after="skillver_123",
            limit=0,
            order="asc",
        )
        assert_matches_type(SyncCursorPage[SkillVersion], version, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.skills.versions.with_raw_response.list(
            skill_id="skill_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        version = response.parse()
        assert_matches_type(SyncCursorPage[SkillVersion], version, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.skills.versions.with_streaming_response.list(
            skill_id="skill_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            version = response.parse()
            assert_matches_type(SyncCursorPage[SkillVersion], version, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `skill_id` but received ''"):
            client.skills.versions.with_raw_response.list(
                skill_id="",
            )

    @parametrize
    def test_method_delete(self, client: OpenAI) -> None:
        version = client.skills.versions.delete(
            version="version",
            skill_id="skill_123",
        )
        assert_matches_type(DeletedSkillVersion, version, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: OpenAI) -> None:
        response = client.skills.versions.with_raw_response.delete(
            version="version",
            skill_id="skill_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        version = response.parse()
        assert_matches_type(DeletedSkillVersion, version, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: OpenAI) -> None:
        with client.skills.versions.with_streaming_response.delete(
            version="version",
            skill_id="skill_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            version = response.parse()
            assert_matches_type(DeletedSkillVersion, version, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `skill_id` but received ''"):
            client.skills.versions.with_raw_response.delete(
                version="version",
                skill_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `version` but received ''"):
            client.skills.versions.with_raw_response.delete(
                version="",
                skill_id="skill_123",
            )


class TestAsyncVersions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        version = await async_client.skills.versions.create(
            skill_id="skill_123",
        )
        assert_matches_type(SkillVersion, version, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncOpenAI) -> None:
        version = await async_client.skills.versions.create(
            skill_id="skill_123",
            default=True,
            files=[b"raw file contents"],
        )
        assert_matches_type(SkillVersion, version, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.skills.versions.with_raw_response.create(
            skill_id="skill_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        version = response.parse()
        assert_matches_type(SkillVersion, version, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.skills.versions.with_streaming_response.create(
            skill_id="skill_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            version = await response.parse()
            assert_matches_type(SkillVersion, version, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `skill_id` but received ''"):
            await async_client.skills.versions.with_raw_response.create(
                skill_id="",
            )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        version = await async_client.skills.versions.retrieve(
            version="version",
            skill_id="skill_123",
        )
        assert_matches_type(SkillVersion, version, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.skills.versions.with_raw_response.retrieve(
            version="version",
            skill_id="skill_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        version = response.parse()
        assert_matches_type(SkillVersion, version, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.skills.versions.with_streaming_response.retrieve(
            version="version",
            skill_id="skill_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            version = await response.parse()
            assert_matches_type(SkillVersion, version, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `skill_id` but received ''"):
            await async_client.skills.versions.with_raw_response.retrieve(
                version="version",
                skill_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `version` but received ''"):
            await async_client.skills.versions.with_raw_response.retrieve(
                version="",
                skill_id="skill_123",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        version = await async_client.skills.versions.list(
            skill_id="skill_123",
        )
        assert_matches_type(AsyncCursorPage[SkillVersion], version, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        version = await async_client.skills.versions.list(
            skill_id="skill_123",
            after="skillver_123",
            limit=0,
            order="asc",
        )
        assert_matches_type(AsyncCursorPage[SkillVersion], version, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.skills.versions.with_raw_response.list(
            skill_id="skill_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        version = response.parse()
        assert_matches_type(AsyncCursorPage[SkillVersion], version, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.skills.versions.with_streaming_response.list(
            skill_id="skill_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            version = await response.parse()
            assert_matches_type(AsyncCursorPage[SkillVersion], version, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `skill_id` but received ''"):
            await async_client.skills.versions.with_raw_response.list(
                skill_id="",
            )

    @parametrize
    async def test_method_delete(self, async_client: AsyncOpenAI) -> None:
        version = await async_client.skills.versions.delete(
            version="version",
            skill_id="skill_123",
        )
        assert_matches_type(DeletedSkillVersion, version, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.skills.versions.with_raw_response.delete(
            version="version",
            skill_id="skill_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        version = response.parse()
        assert_matches_type(DeletedSkillVersion, version, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncOpenAI) -> None:
        async with async_client.skills.versions.with_streaming_response.delete(
            version="version",
            skill_id="skill_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            version = await response.parse()
            assert_matches_type(DeletedSkillVersion, version, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `skill_id` but received ''"):
            await async_client.skills.versions.with_raw_response.delete(
                version="version",
                skill_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `version` but received ''"):
            await async_client.skills.versions.with_raw_response.delete(
                version="",
                skill_id="skill_123",
            )
