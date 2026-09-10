# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import httpx2
import pytest

import openai._legacy_response as _legacy_response
from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from tests.respx2 import MockRouter
from openai.pagination import SyncCursorPage, AsyncCursorPage
from openai.types.beta.agents.sessions import (
    SessionArtifact,
    SessionArtifactDeleted,
)

# pyright: reportDeprecated=false

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestArtifacts:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        artifact = client.beta.agents.sessions.artifacts.retrieve(
            artifact_id="artifact_id",
            session_id="session_id",
        )
        assert_matches_type(SessionArtifact, artifact, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.beta.agents.sessions.artifacts.with_raw_response.retrieve(
            artifact_id="artifact_id",
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        artifact = response.parse()
        assert_matches_type(SessionArtifact, artifact, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.beta.agents.sessions.artifacts.with_streaming_response.retrieve(
            artifact_id="artifact_id",
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            artifact = response.parse()
            assert_matches_type(SessionArtifact, artifact, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.beta.agents.sessions.artifacts.with_raw_response.retrieve(
                artifact_id="artifact_id",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `artifact_id` but received ''"):
            client.beta.agents.sessions.artifacts.with_raw_response.retrieve(
                artifact_id="",
                session_id="session_id",
            )

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        artifact = client.beta.agents.sessions.artifacts.list(
            session_id="session_id",
        )
        assert_matches_type(SyncCursorPage[SessionArtifact], artifact, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        artifact = client.beta.agents.sessions.artifacts.list(
            session_id="session_id",
            after="after",
            environment_id="environment_id",
            limit=1,
            order="asc",
        )
        assert_matches_type(SyncCursorPage[SessionArtifact], artifact, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.beta.agents.sessions.artifacts.with_raw_response.list(
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        artifact = response.parse()
        assert_matches_type(SyncCursorPage[SessionArtifact], artifact, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.beta.agents.sessions.artifacts.with_streaming_response.list(
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            artifact = response.parse()
            assert_matches_type(SyncCursorPage[SessionArtifact], artifact, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.beta.agents.sessions.artifacts.with_raw_response.list(
                session_id="",
            )

    @parametrize
    def test_method_delete(self, client: OpenAI) -> None:
        artifact = client.beta.agents.sessions.artifacts.delete(
            artifact_id="artifact_id",
            session_id="session_id",
        )
        assert_matches_type(SessionArtifactDeleted, artifact, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: OpenAI) -> None:
        response = client.beta.agents.sessions.artifacts.with_raw_response.delete(
            artifact_id="artifact_id",
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        artifact = response.parse()
        assert_matches_type(SessionArtifactDeleted, artifact, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: OpenAI) -> None:
        with client.beta.agents.sessions.artifacts.with_streaming_response.delete(
            artifact_id="artifact_id",
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            artifact = response.parse()
            assert_matches_type(SessionArtifactDeleted, artifact, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.beta.agents.sessions.artifacts.with_raw_response.delete(
                artifact_id="artifact_id",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `artifact_id` but received ''"):
            client.beta.agents.sessions.artifacts.with_raw_response.delete(
                artifact_id="",
                session_id="session_id",
            )

    @parametrize
    @pytest.mark.respx2(base_url=base_url)
    def test_method_content(self, client: OpenAI, respx2_mock: MockRouter) -> None:
        respx2_mock.get("/agents/sessions/session_id/artifacts/artifact_id/content").mock(
            return_value=httpx2.Response(200, json={"foo": "bar"})
        )
        artifact = client.beta.agents.sessions.artifacts.content(
            artifact_id="artifact_id",
            session_id="session_id",
        )
        assert isinstance(artifact, _legacy_response.HttpxBinaryResponseContent)
        assert artifact.json() == {"foo": "bar"}

    @parametrize
    @pytest.mark.respx2(base_url=base_url)
    def test_raw_response_content(self, client: OpenAI, respx2_mock: MockRouter) -> None:
        respx2_mock.get("/agents/sessions/session_id/artifacts/artifact_id/content").mock(
            return_value=httpx2.Response(200, json={"foo": "bar"})
        )

        response = client.beta.agents.sessions.artifacts.with_raw_response.content(
            artifact_id="artifact_id",
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        artifact = response.parse()
        assert_matches_type(_legacy_response.HttpxBinaryResponseContent, artifact, path=["response"])

    @parametrize
    @pytest.mark.respx2(base_url=base_url)
    def test_streaming_response_content(self, client: OpenAI, respx2_mock: MockRouter) -> None:
        respx2_mock.get("/agents/sessions/session_id/artifacts/artifact_id/content").mock(
            return_value=httpx2.Response(200, json={"foo": "bar"})
        )
        with client.beta.agents.sessions.artifacts.with_streaming_response.content(
            artifact_id="artifact_id",
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            artifact = response.parse()
            assert_matches_type(bytes, artifact, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    @pytest.mark.respx2(base_url=base_url)
    def test_path_params_content(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.beta.agents.sessions.artifacts.with_raw_response.content(
                artifact_id="artifact_id",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `artifact_id` but received ''"):
            client.beta.agents.sessions.artifacts.with_raw_response.content(
                artifact_id="",
                session_id="session_id",
            )


class TestAsyncArtifacts:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        artifact = await async_client.beta.agents.sessions.artifacts.retrieve(
            artifact_id="artifact_id",
            session_id="session_id",
        )
        assert_matches_type(SessionArtifact, artifact, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.sessions.artifacts.with_raw_response.retrieve(
            artifact_id="artifact_id",
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        artifact = response.parse()
        assert_matches_type(SessionArtifact, artifact, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.sessions.artifacts.with_streaming_response.retrieve(
            artifact_id="artifact_id",
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            artifact = await response.parse()
            assert_matches_type(SessionArtifact, artifact, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.beta.agents.sessions.artifacts.with_raw_response.retrieve(
                artifact_id="artifact_id",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `artifact_id` but received ''"):
            await async_client.beta.agents.sessions.artifacts.with_raw_response.retrieve(
                artifact_id="",
                session_id="session_id",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        artifact = await async_client.beta.agents.sessions.artifacts.list(
            session_id="session_id",
        )
        assert_matches_type(AsyncCursorPage[SessionArtifact], artifact, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        artifact = await async_client.beta.agents.sessions.artifacts.list(
            session_id="session_id",
            after="after",
            environment_id="environment_id",
            limit=1,
            order="asc",
        )
        assert_matches_type(AsyncCursorPage[SessionArtifact], artifact, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.sessions.artifacts.with_raw_response.list(
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        artifact = response.parse()
        assert_matches_type(AsyncCursorPage[SessionArtifact], artifact, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.sessions.artifacts.with_streaming_response.list(
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            artifact = await response.parse()
            assert_matches_type(AsyncCursorPage[SessionArtifact], artifact, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.beta.agents.sessions.artifacts.with_raw_response.list(
                session_id="",
            )

    @parametrize
    async def test_method_delete(self, async_client: AsyncOpenAI) -> None:
        artifact = await async_client.beta.agents.sessions.artifacts.delete(
            artifact_id="artifact_id",
            session_id="session_id",
        )
        assert_matches_type(SessionArtifactDeleted, artifact, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.sessions.artifacts.with_raw_response.delete(
            artifact_id="artifact_id",
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        artifact = response.parse()
        assert_matches_type(SessionArtifactDeleted, artifact, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.sessions.artifacts.with_streaming_response.delete(
            artifact_id="artifact_id",
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            artifact = await response.parse()
            assert_matches_type(SessionArtifactDeleted, artifact, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.beta.agents.sessions.artifacts.with_raw_response.delete(
                artifact_id="artifact_id",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `artifact_id` but received ''"):
            await async_client.beta.agents.sessions.artifacts.with_raw_response.delete(
                artifact_id="",
                session_id="session_id",
            )

    @parametrize
    @pytest.mark.respx2(base_url=base_url)
    async def test_method_content(self, async_client: AsyncOpenAI, respx2_mock: MockRouter) -> None:
        respx2_mock.get("/agents/sessions/session_id/artifacts/artifact_id/content").mock(
            return_value=httpx2.Response(200, json={"foo": "bar"})
        )
        artifact = await async_client.beta.agents.sessions.artifacts.content(
            artifact_id="artifact_id",
            session_id="session_id",
        )
        assert isinstance(artifact, _legacy_response.HttpxBinaryResponseContent)
        assert artifact.json() == {"foo": "bar"}

    @parametrize
    @pytest.mark.respx2(base_url=base_url)
    async def test_raw_response_content(self, async_client: AsyncOpenAI, respx2_mock: MockRouter) -> None:
        respx2_mock.get("/agents/sessions/session_id/artifacts/artifact_id/content").mock(
            return_value=httpx2.Response(200, json={"foo": "bar"})
        )

        response = await async_client.beta.agents.sessions.artifacts.with_raw_response.content(
            artifact_id="artifact_id",
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        artifact = response.parse()
        assert_matches_type(_legacy_response.HttpxBinaryResponseContent, artifact, path=["response"])

    @parametrize
    @pytest.mark.respx2(base_url=base_url)
    async def test_streaming_response_content(self, async_client: AsyncOpenAI, respx2_mock: MockRouter) -> None:
        respx2_mock.get("/agents/sessions/session_id/artifacts/artifact_id/content").mock(
            return_value=httpx2.Response(200, json={"foo": "bar"})
        )
        async with async_client.beta.agents.sessions.artifacts.with_streaming_response.content(
            artifact_id="artifact_id",
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            artifact = await response.parse()
            assert_matches_type(bytes, artifact, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    @pytest.mark.respx2(base_url=base_url)
    async def test_path_params_content(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.beta.agents.sessions.artifacts.with_raw_response.content(
                artifact_id="artifact_id",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `artifact_id` but received ''"):
            await async_client.beta.agents.sessions.artifacts.with_raw_response.content(
                artifact_id="",
                session_id="session_id",
            )
