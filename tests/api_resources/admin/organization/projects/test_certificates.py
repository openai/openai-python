# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncPage, AsyncPage, SyncConversationCursorPage, AsyncConversationCursorPage
from openai.types.admin.organization.projects import (
    CertificateListResponse,
    CertificateActivateResponse,
    CertificateDeactivateResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCertificates:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        certificate = client.admin.organization.projects.certificates.list(
            project_id="project_id",
        )
        assert_matches_type(SyncConversationCursorPage[CertificateListResponse], certificate, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        certificate = client.admin.organization.projects.certificates.list(
            project_id="project_id",
            after="after",
            limit=0,
            order="asc",
        )
        assert_matches_type(SyncConversationCursorPage[CertificateListResponse], certificate, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.admin.organization.projects.certificates.with_raw_response.list(
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        certificate = response.parse()
        assert_matches_type(SyncConversationCursorPage[CertificateListResponse], certificate, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.admin.organization.projects.certificates.with_streaming_response.list(
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            certificate = response.parse()
            assert_matches_type(SyncConversationCursorPage[CertificateListResponse], certificate, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.admin.organization.projects.certificates.with_raw_response.list(
                project_id="",
            )

    @parametrize
    def test_method_activate(self, client: OpenAI) -> None:
        certificate = client.admin.organization.projects.certificates.activate(
            project_id="project_id",
            certificate_ids=["cert_abc"],
        )
        assert_matches_type(SyncPage[CertificateActivateResponse], certificate, path=["response"])

    @parametrize
    def test_raw_response_activate(self, client: OpenAI) -> None:
        response = client.admin.organization.projects.certificates.with_raw_response.activate(
            project_id="project_id",
            certificate_ids=["cert_abc"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        certificate = response.parse()
        assert_matches_type(SyncPage[CertificateActivateResponse], certificate, path=["response"])

    @parametrize
    def test_streaming_response_activate(self, client: OpenAI) -> None:
        with client.admin.organization.projects.certificates.with_streaming_response.activate(
            project_id="project_id",
            certificate_ids=["cert_abc"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            certificate = response.parse()
            assert_matches_type(SyncPage[CertificateActivateResponse], certificate, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_activate(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.admin.organization.projects.certificates.with_raw_response.activate(
                project_id="",
                certificate_ids=["cert_abc"],
            )

    @parametrize
    def test_method_deactivate(self, client: OpenAI) -> None:
        certificate = client.admin.organization.projects.certificates.deactivate(
            project_id="project_id",
            certificate_ids=["cert_abc"],
        )
        assert_matches_type(SyncPage[CertificateDeactivateResponse], certificate, path=["response"])

    @parametrize
    def test_raw_response_deactivate(self, client: OpenAI) -> None:
        response = client.admin.organization.projects.certificates.with_raw_response.deactivate(
            project_id="project_id",
            certificate_ids=["cert_abc"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        certificate = response.parse()
        assert_matches_type(SyncPage[CertificateDeactivateResponse], certificate, path=["response"])

    @parametrize
    def test_streaming_response_deactivate(self, client: OpenAI) -> None:
        with client.admin.organization.projects.certificates.with_streaming_response.deactivate(
            project_id="project_id",
            certificate_ids=["cert_abc"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            certificate = response.parse()
            assert_matches_type(SyncPage[CertificateDeactivateResponse], certificate, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_deactivate(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.admin.organization.projects.certificates.with_raw_response.deactivate(
                project_id="",
                certificate_ids=["cert_abc"],
            )


class TestAsyncCertificates:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        certificate = await async_client.admin.organization.projects.certificates.list(
            project_id="project_id",
        )
        assert_matches_type(AsyncConversationCursorPage[CertificateListResponse], certificate, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        certificate = await async_client.admin.organization.projects.certificates.list(
            project_id="project_id",
            after="after",
            limit=0,
            order="asc",
        )
        assert_matches_type(AsyncConversationCursorPage[CertificateListResponse], certificate, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.projects.certificates.with_raw_response.list(
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        certificate = response.parse()
        assert_matches_type(AsyncConversationCursorPage[CertificateListResponse], certificate, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.projects.certificates.with_streaming_response.list(
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            certificate = await response.parse()
            assert_matches_type(AsyncConversationCursorPage[CertificateListResponse], certificate, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.admin.organization.projects.certificates.with_raw_response.list(
                project_id="",
            )

    @parametrize
    async def test_method_activate(self, async_client: AsyncOpenAI) -> None:
        certificate = await async_client.admin.organization.projects.certificates.activate(
            project_id="project_id",
            certificate_ids=["cert_abc"],
        )
        assert_matches_type(AsyncPage[CertificateActivateResponse], certificate, path=["response"])

    @parametrize
    async def test_raw_response_activate(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.projects.certificates.with_raw_response.activate(
            project_id="project_id",
            certificate_ids=["cert_abc"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        certificate = response.parse()
        assert_matches_type(AsyncPage[CertificateActivateResponse], certificate, path=["response"])

    @parametrize
    async def test_streaming_response_activate(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.projects.certificates.with_streaming_response.activate(
            project_id="project_id",
            certificate_ids=["cert_abc"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            certificate = await response.parse()
            assert_matches_type(AsyncPage[CertificateActivateResponse], certificate, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_activate(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.admin.organization.projects.certificates.with_raw_response.activate(
                project_id="",
                certificate_ids=["cert_abc"],
            )

    @parametrize
    async def test_method_deactivate(self, async_client: AsyncOpenAI) -> None:
        certificate = await async_client.admin.organization.projects.certificates.deactivate(
            project_id="project_id",
            certificate_ids=["cert_abc"],
        )
        assert_matches_type(AsyncPage[CertificateDeactivateResponse], certificate, path=["response"])

    @parametrize
    async def test_raw_response_deactivate(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.projects.certificates.with_raw_response.deactivate(
            project_id="project_id",
            certificate_ids=["cert_abc"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        certificate = response.parse()
        assert_matches_type(AsyncPage[CertificateDeactivateResponse], certificate, path=["response"])

    @parametrize
    async def test_streaming_response_deactivate(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.projects.certificates.with_streaming_response.deactivate(
            project_id="project_id",
            certificate_ids=["cert_abc"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            certificate = await response.parse()
            assert_matches_type(AsyncPage[CertificateDeactivateResponse], certificate, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_deactivate(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.admin.organization.projects.certificates.with_raw_response.deactivate(
                project_id="",
                certificate_ids=["cert_abc"],
            )
