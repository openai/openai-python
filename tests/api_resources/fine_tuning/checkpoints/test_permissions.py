# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncPage, AsyncPage
from openai.types.fine_tuning.checkpoints import (
    PermissionCreateResponse,
    PermissionDeleteResponse,
    PermissionRetrieveResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPermissions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        permission = client.fine_tuning.checkpoints.permissions.create(
            fine_tuned_model_checkpoint="ft:gpt-4o-mini-2024-07-18:org:weather:B7R9VjQd",
            project_ids=["string"],
        )
        assert_matches_type(SyncPage[PermissionCreateResponse], permission, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.fine_tuning.checkpoints.permissions.with_raw_response.create(
            fine_tuned_model_checkpoint="ft:gpt-4o-mini-2024-07-18:org:weather:B7R9VjQd",
            project_ids=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = response.parse()
        assert_matches_type(SyncPage[PermissionCreateResponse], permission, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.fine_tuning.checkpoints.permissions.with_streaming_response.create(
            fine_tuned_model_checkpoint="ft:gpt-4o-mini-2024-07-18:org:weather:B7R9VjQd",
            project_ids=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = response.parse()
            assert_matches_type(SyncPage[PermissionCreateResponse], permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create(self, client: OpenAI) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `fine_tuned_model_checkpoint` but received ''"
        ):
            client.fine_tuning.checkpoints.permissions.with_raw_response.create(
                fine_tuned_model_checkpoint="",
                project_ids=["string"],
            )

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        permission = client.fine_tuning.checkpoints.permissions.retrieve(
            fine_tuned_model_checkpoint="ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        )
        assert_matches_type(PermissionRetrieveResponse, permission, path=["response"])

    @parametrize
    def test_method_retrieve_with_all_params(self, client: OpenAI) -> None:
        permission = client.fine_tuning.checkpoints.permissions.retrieve(
            fine_tuned_model_checkpoint="ft-AF1WoRqd3aJAHsqc9NY7iL8F",
            after="after",
            limit=0,
            order="ascending",
            project_id="project_id",
        )
        assert_matches_type(PermissionRetrieveResponse, permission, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.fine_tuning.checkpoints.permissions.with_raw_response.retrieve(
            fine_tuned_model_checkpoint="ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = response.parse()
        assert_matches_type(PermissionRetrieveResponse, permission, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.fine_tuning.checkpoints.permissions.with_streaming_response.retrieve(
            fine_tuned_model_checkpoint="ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = response.parse()
            assert_matches_type(PermissionRetrieveResponse, permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `fine_tuned_model_checkpoint` but received ''"
        ):
            client.fine_tuning.checkpoints.permissions.with_raw_response.retrieve(
                fine_tuned_model_checkpoint="",
            )

    @parametrize
    def test_method_delete(self, client: OpenAI) -> None:
        permission = client.fine_tuning.checkpoints.permissions.delete(
            permission_id="cp_zc4Q7MP6XxulcVzj4MZdwsAB",
            fine_tuned_model_checkpoint="ft:gpt-4o-mini-2024-07-18:org:weather:B7R9VjQd",
        )
        assert_matches_type(PermissionDeleteResponse, permission, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: OpenAI) -> None:
        response = client.fine_tuning.checkpoints.permissions.with_raw_response.delete(
            permission_id="cp_zc4Q7MP6XxulcVzj4MZdwsAB",
            fine_tuned_model_checkpoint="ft:gpt-4o-mini-2024-07-18:org:weather:B7R9VjQd",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = response.parse()
        assert_matches_type(PermissionDeleteResponse, permission, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: OpenAI) -> None:
        with client.fine_tuning.checkpoints.permissions.with_streaming_response.delete(
            permission_id="cp_zc4Q7MP6XxulcVzj4MZdwsAB",
            fine_tuned_model_checkpoint="ft:gpt-4o-mini-2024-07-18:org:weather:B7R9VjQd",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = response.parse()
            assert_matches_type(PermissionDeleteResponse, permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: OpenAI) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `fine_tuned_model_checkpoint` but received ''"
        ):
            client.fine_tuning.checkpoints.permissions.with_raw_response.delete(
                permission_id="cp_zc4Q7MP6XxulcVzj4MZdwsAB",
                fine_tuned_model_checkpoint="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `permission_id` but received ''"):
            client.fine_tuning.checkpoints.permissions.with_raw_response.delete(
                permission_id="",
                fine_tuned_model_checkpoint="ft:gpt-4o-mini-2024-07-18:org:weather:B7R9VjQd",
            )


class TestAsyncPermissions:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        permission = await async_client.fine_tuning.checkpoints.permissions.create(
            fine_tuned_model_checkpoint="ft:gpt-4o-mini-2024-07-18:org:weather:B7R9VjQd",
            project_ids=["string"],
        )
        assert_matches_type(AsyncPage[PermissionCreateResponse], permission, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.fine_tuning.checkpoints.permissions.with_raw_response.create(
            fine_tuned_model_checkpoint="ft:gpt-4o-mini-2024-07-18:org:weather:B7R9VjQd",
            project_ids=["string"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = response.parse()
        assert_matches_type(AsyncPage[PermissionCreateResponse], permission, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.fine_tuning.checkpoints.permissions.with_streaming_response.create(
            fine_tuned_model_checkpoint="ft:gpt-4o-mini-2024-07-18:org:weather:B7R9VjQd",
            project_ids=["string"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = await response.parse()
            assert_matches_type(AsyncPage[PermissionCreateResponse], permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `fine_tuned_model_checkpoint` but received ''"
        ):
            await async_client.fine_tuning.checkpoints.permissions.with_raw_response.create(
                fine_tuned_model_checkpoint="",
                project_ids=["string"],
            )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        permission = await async_client.fine_tuning.checkpoints.permissions.retrieve(
            fine_tuned_model_checkpoint="ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        )
        assert_matches_type(PermissionRetrieveResponse, permission, path=["response"])

    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncOpenAI) -> None:
        permission = await async_client.fine_tuning.checkpoints.permissions.retrieve(
            fine_tuned_model_checkpoint="ft-AF1WoRqd3aJAHsqc9NY7iL8F",
            after="after",
            limit=0,
            order="ascending",
            project_id="project_id",
        )
        assert_matches_type(PermissionRetrieveResponse, permission, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.fine_tuning.checkpoints.permissions.with_raw_response.retrieve(
            fine_tuned_model_checkpoint="ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = response.parse()
        assert_matches_type(PermissionRetrieveResponse, permission, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.fine_tuning.checkpoints.permissions.with_streaming_response.retrieve(
            fine_tuned_model_checkpoint="ft-AF1WoRqd3aJAHsqc9NY7iL8F",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = await response.parse()
            assert_matches_type(PermissionRetrieveResponse, permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `fine_tuned_model_checkpoint` but received ''"
        ):
            await async_client.fine_tuning.checkpoints.permissions.with_raw_response.retrieve(
                fine_tuned_model_checkpoint="",
            )

    @parametrize
    async def test_method_delete(self, async_client: AsyncOpenAI) -> None:
        permission = await async_client.fine_tuning.checkpoints.permissions.delete(
            permission_id="cp_zc4Q7MP6XxulcVzj4MZdwsAB",
            fine_tuned_model_checkpoint="ft:gpt-4o-mini-2024-07-18:org:weather:B7R9VjQd",
        )
        assert_matches_type(PermissionDeleteResponse, permission, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.fine_tuning.checkpoints.permissions.with_raw_response.delete(
            permission_id="cp_zc4Q7MP6XxulcVzj4MZdwsAB",
            fine_tuned_model_checkpoint="ft:gpt-4o-mini-2024-07-18:org:weather:B7R9VjQd",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        permission = response.parse()
        assert_matches_type(PermissionDeleteResponse, permission, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncOpenAI) -> None:
        async with async_client.fine_tuning.checkpoints.permissions.with_streaming_response.delete(
            permission_id="cp_zc4Q7MP6XxulcVzj4MZdwsAB",
            fine_tuned_model_checkpoint="ft:gpt-4o-mini-2024-07-18:org:weather:B7R9VjQd",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            permission = await response.parse()
            assert_matches_type(PermissionDeleteResponse, permission, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(
            ValueError, match=r"Expected a non-empty value for `fine_tuned_model_checkpoint` but received ''"
        ):
            await async_client.fine_tuning.checkpoints.permissions.with_raw_response.delete(
                permission_id="cp_zc4Q7MP6XxulcVzj4MZdwsAB",
                fine_tuned_model_checkpoint="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `permission_id` but received ''"):
            await async_client.fine_tuning.checkpoints.permissions.with_raw_response.delete(
                permission_id="",
                fine_tuned_model_checkpoint="ft:gpt-4o-mini-2024-07-18:org:weather:B7R9VjQd",
            )
