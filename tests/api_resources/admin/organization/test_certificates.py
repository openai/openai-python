# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncPage, AsyncPage, SyncConversationCursorPage, AsyncConversationCursorPage
from openai.types.admin.organization import (
    Certificate,
    CertificateListResponse,
    CertificateDeleteResponse,
    CertificateActivateResponse,
    CertificateDeactivateResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCertificates:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        certificate = client.admin.organization.certificates.create(
            certificate="certificate",
        )
        assert_matches_type(Certificate, certificate, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        certificate = client.admin.organization.certificates.create(
            certificate="certificate",
            name="name",
        )
        assert_matches_type(Certificate, certificate, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.admin.organization.certificates.with_raw_response.create(
            certificate="certificate",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        certificate = response.parse()
        assert_matches_type(Certificate, certificate, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.admin.organization.certificates.with_streaming_response.create(
            certificate="certificate",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            certificate = response.parse()
            assert_matches_type(Certificate, certificate, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        certificate = client.admin.organization.certificates.retrieve(
            certificate_id="certificate_id",
        )
        assert_matches_type(Certificate, certificate, path=["response"])

    @parametrize
    def test_method_retrieve_with_all_params(self, client: OpenAI) -> None:
        certificate = client.admin.organization.certificates.retrieve(
            certificate_id="certificate_id",
            include=["content"],
        )
        assert_matches_type(Certificate, certificate, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.admin.organization.certificates.with_raw_response.retrieve(
            certificate_id="certificate_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        certificate = response.parse()
        assert_matches_type(Certificate, certificate, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.admin.organization.certificates.with_streaming_response.retrieve(
            certificate_id="certificate_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            certificate = response.parse()
            assert_matches_type(Certificate, certificate, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `certificate_id` but received ''"):
            client.admin.organization.certificates.with_raw_response.retrieve(
                certificate_id="",
            )

    @parametrize
    def test_method_update(self, client: OpenAI) -> None:
        certificate = client.admin.organization.certificates.update(
            certificate_id="certificate_id",
        )
        assert_matches_type(Certificate, certificate, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: OpenAI) -> None:
        certificate = client.admin.organization.certificates.update(
            certificate_id="certificate_id",
            name="name",
        )
        assert_matches_type(Certificate, certificate, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: OpenAI) -> None:
        response = client.admin.organization.certificates.with_raw_response.update(
            certificate_id="certificate_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        certificate = response.parse()
        assert_matches_type(Certificate, certificate, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: OpenAI) -> None:
        with client.admin.organization.certificates.with_streaming_response.update(
            certificate_id="certificate_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            certificate = response.parse()
            assert_matches_type(Certificate, certificate, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `certificate_id` but received ''"):
            client.admin.organization.certificates.with_raw_response.update(
                certificate_id="",
            )

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        certificate = client.admin.organization.certificates.list()
        assert_matches_type(SyncConversationCursorPage[CertificateListResponse], certificate, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        certificate = client.admin.organization.certificates.list(
            after="after",
            limit=0,
            order="asc",
        )
        assert_matches_type(SyncConversationCursorPage[CertificateListResponse], certificate, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.admin.organization.certificates.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        certificate = response.parse()
        assert_matches_type(SyncConversationCursorPage[CertificateListResponse], certificate, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.admin.organization.certificates.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            certificate = response.parse()
            assert_matches_type(SyncConversationCursorPage[CertificateListResponse], certificate, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: OpenAI) -> None:
        certificate = client.admin.organization.certificates.delete(
            "certificate_id",
        )
        assert_matches_type(CertificateDeleteResponse, certificate, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: OpenAI) -> None:
        response = client.admin.organization.certificates.with_raw_response.delete(
            "certificate_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        certificate = response.parse()
        assert_matches_type(CertificateDeleteResponse, certificate, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: OpenAI) -> None:
        with client.admin.organization.certificates.with_streaming_response.delete(
            "certificate_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            certificate = response.parse()
            assert_matches_type(CertificateDeleteResponse, certificate, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `certificate_id` but received ''"):
            client.admin.organization.certificates.with_raw_response.delete(
                "",
            )

    @parametrize
    def test_method_activate(self, client: OpenAI) -> None:
        certificate = client.admin.organization.certificates.activate(
            certificate_ids=["cert_abc"],
        )
        assert_matches_type(SyncPage[CertificateActivateResponse], certificate, path=["response"])

    @parametrize
    def test_raw_response_activate(self, client: OpenAI) -> None:
        response = client.admin.organization.certificates.with_raw_response.activate(
            certificate_ids=["cert_abc"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        certificate = response.parse()
        assert_matches_type(SyncPage[CertificateActivateResponse], certificate, path=["response"])

    @parametrize
    def test_streaming_response_activate(self, client: OpenAI) -> None:
        with client.admin.organization.certificates.with_streaming_response.activate(
            certificate_ids=["cert_abc"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            certificate = response.parse()
            assert_matches_type(SyncPage[CertificateActivateResponse], certificate, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_deactivate(self, client: OpenAI) -> None:
        certificate = client.admin.organization.certificates.deactivate(
            certificate_ids=["cert_abc"],
        )
        assert_matches_type(SyncPage[CertificateDeactivateResponse], certificate, path=["response"])

    @parametrize
    def test_raw_response_deactivate(self, client: OpenAI) -> None:
        response = client.admin.organization.certificates.with_raw_response.deactivate(
            certificate_ids=["cert_abc"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        certificate = response.parse()
        assert_matches_type(SyncPage[CertificateDeactivateResponse], certificate, path=["response"])

    @parametrize
    def test_streaming_response_deactivate(self, client: OpenAI) -> None:
        with client.admin.organization.certificates.with_streaming_response.deactivate(
            certificate_ids=["cert_abc"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            certificate = response.parse()
            assert_matches_type(SyncPage[CertificateDeactivateResponse], certificate, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncCertificates:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        certificate = await async_client.admin.organization.certificates.create(
            certificate="certificate",
        )
        assert_matches_type(Certificate, certificate, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncOpenAI) -> None:
        certificate = await async_client.admin.organization.certificates.create(
            certificate="certificate",
            name="name",
        )
        assert_matches_type(Certificate, certificate, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.certificates.with_raw_response.create(
            certificate="certificate",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        certificate = response.parse()
        assert_matches_type(Certificate, certificate, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.certificates.with_streaming_response.create(
            certificate="certificate",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            certificate = await response.parse()
            assert_matches_type(Certificate, certificate, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        certificate = await async_client.admin.organization.certificates.retrieve(
            certificate_id="certificate_id",
        )
        assert_matches_type(Certificate, certificate, path=["response"])

    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncOpenAI) -> None:
        certificate = await async_client.admin.organization.certificates.retrieve(
            certificate_id="certificate_id",
            include=["content"],
        )
        assert_matches_type(Certificate, certificate, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.certificates.with_raw_response.retrieve(
            certificate_id="certificate_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        certificate = response.parse()
        assert_matches_type(Certificate, certificate, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.certificates.with_streaming_response.retrieve(
            certificate_id="certificate_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            certificate = await response.parse()
            assert_matches_type(Certificate, certificate, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `certificate_id` but received ''"):
            await async_client.admin.organization.certificates.with_raw_response.retrieve(
                certificate_id="",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncOpenAI) -> None:
        certificate = await async_client.admin.organization.certificates.update(
            certificate_id="certificate_id",
        )
        assert_matches_type(Certificate, certificate, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncOpenAI) -> None:
        certificate = await async_client.admin.organization.certificates.update(
            certificate_id="certificate_id",
            name="name",
        )
        assert_matches_type(Certificate, certificate, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.certificates.with_raw_response.update(
            certificate_id="certificate_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        certificate = response.parse()
        assert_matches_type(Certificate, certificate, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.certificates.with_streaming_response.update(
            certificate_id="certificate_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            certificate = await response.parse()
            assert_matches_type(Certificate, certificate, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `certificate_id` but received ''"):
            await async_client.admin.organization.certificates.with_raw_response.update(
                certificate_id="",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        certificate = await async_client.admin.organization.certificates.list()
        assert_matches_type(AsyncConversationCursorPage[CertificateListResponse], certificate, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        certificate = await async_client.admin.organization.certificates.list(
            after="after",
            limit=0,
            order="asc",
        )
        assert_matches_type(AsyncConversationCursorPage[CertificateListResponse], certificate, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.certificates.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        certificate = response.parse()
        assert_matches_type(AsyncConversationCursorPage[CertificateListResponse], certificate, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.certificates.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            certificate = await response.parse()
            assert_matches_type(AsyncConversationCursorPage[CertificateListResponse], certificate, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, async_client: AsyncOpenAI) -> None:
        certificate = await async_client.admin.organization.certificates.delete(
            "certificate_id",
        )
        assert_matches_type(CertificateDeleteResponse, certificate, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.certificates.with_raw_response.delete(
            "certificate_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        certificate = response.parse()
        assert_matches_type(CertificateDeleteResponse, certificate, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.certificates.with_streaming_response.delete(
            "certificate_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            certificate = await response.parse()
            assert_matches_type(CertificateDeleteResponse, certificate, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `certificate_id` but received ''"):
            await async_client.admin.organization.certificates.with_raw_response.delete(
                "",
            )

    @parametrize
    async def test_method_activate(self, async_client: AsyncOpenAI) -> None:
        certificate = await async_client.admin.organization.certificates.activate(
            certificate_ids=["cert_abc"],
        )
        assert_matches_type(AsyncPage[CertificateActivateResponse], certificate, path=["response"])

    @parametrize
    async def test_raw_response_activate(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.certificates.with_raw_response.activate(
            certificate_ids=["cert_abc"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        certificate = response.parse()
        assert_matches_type(AsyncPage[CertificateActivateResponse], certificate, path=["response"])

    @parametrize
    async def test_streaming_response_activate(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.certificates.with_streaming_response.activate(
            certificate_ids=["cert_abc"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            certificate = await response.parse()
            assert_matches_type(AsyncPage[CertificateActivateResponse], certificate, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_deactivate(self, async_client: AsyncOpenAI) -> None:
        certificate = await async_client.admin.organization.certificates.deactivate(
            certificate_ids=["cert_abc"],
        )
        assert_matches_type(AsyncPage[CertificateDeactivateResponse], certificate, path=["response"])

    @parametrize
    async def test_raw_response_deactivate(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.certificates.with_raw_response.deactivate(
            certificate_ids=["cert_abc"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        certificate = response.parse()
        assert_matches_type(AsyncPage[CertificateDeactivateResponse], certificate, path=["response"])

    @parametrize
    async def test_streaming_response_deactivate(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.certificates.with_streaming_response.deactivate(
            certificate_ids=["cert_abc"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            certificate = await response.parse()
            assert_matches_type(AsyncPage[CertificateDeactivateResponse], certificate, path=["response"])

        assert cast(Any, response.is_closed) is True
