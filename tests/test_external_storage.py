from __future__ import annotations

import json
from typing import cast

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from tests.respx2 import MockRouter
from tests.respx2.models import Call
from openai.types.admin.organization import GcpExternalStorageProvider, ExternalStorageConfiguration
from openai.types.admin.organization.external_storage_create_params import Provider

BASE_URL = "https://example.com/v1"
PROVIDERS: list[tuple[Provider, dict[str, object]]] = [
    (
        {"type": "aws", "bucket": "test-bucket", "role_arn": "arn:aws:iam::000000000000:role/test"},
        {
            "type": "aws",
            "bucket": "test-bucket",
            "role_arn": "arn:aws:iam::000000000000:role/test",
            "account_id": "000000000000",
            "region": "us-east-1",
            "external_id": "test-external-id",
            "future_provider_field": {"retained": True},
        },
    ),
    (
        {
            "type": "azure",
            "tenant_id": "test-tenant",
            "subscription_id": "test-subscription",
            "resource_group": "test-group",
            "account_name": "test-account",
            "container": "test-container",
        },
        {
            "type": "azure",
            "tenant_id": "test-tenant",
            "subscription_id": "test-subscription",
            "resource_group": "test-group",
            "account_name": "test-account",
            "container": "test-container",
            "region": "eastus",
            "future_provider_field": {"retained": True},
        },
    ),
    (
        {
            "type": "gcp",
            "bucket": "test-bucket",
            "workload_identity_pool_id": "test-pool",
            "workload_identity_project_number": "000000000000",
            "workload_identity_provider_id": "test-provider",
        },
        {
            "type": "gcp",
            "bucket": "test-bucket",
            "workload_identity_pool_id": "test-pool",
            "workload_identity_project_number": "000000000000",
            "workload_identity_provider_id": "test-provider",
            "audience": "test-audience",
            "region": "us-central1",
            "future_provider_field": {"retained": True},
        },
    ),
]


def configuration(provider: dict[str, object], storage_id: str = "extstorage_test") -> dict[str, object]:
    return {
        "id": storage_id,
        "object": "organization.external_storage",
        "project_id": "proj_test",
        "provider": provider,
        "geography": "US",
        "status": "validated",
        "created_at": 123,
        "future_configuration_field": {"retained": True},
    }


@pytest.mark.respx2(base_url=BASE_URL)
@pytest.mark.parametrize("provider,response_provider", PROVIDERS, ids=["aws", "azure", "gcp"])
def test_sync_external_storage_provider_and_admin_auth(
    provider: Provider, response_provider: dict[str, object], respx2_mock: MockRouter
) -> None:
    payload = configuration(response_provider)
    route = respx2_mock.post("/organization/external_storage").mock(return_value=httpx2.Response(200, json=payload))
    with OpenAI(
        base_url=BASE_URL,
        api_key="test-project-key",
        admin_api_key="test-admin-key",
        _strict_response_validation=True,
    ) as client:
        result = client.admin.organization.external_storage.create(project_id="proj_test", provider=provider)

    assert isinstance(result, ExternalStorageConfiguration)
    if provider["type"] == "gcp":
        assert isinstance(result.provider, GcpExternalStorageProvider)
    assert result.to_dict() == payload
    request = route.calls.last.request
    assert request.headers["Authorization"] == "Bearer test-admin-key"
    assert json.loads(request.content) == {"project_id": "proj_test", "provider": provider}


@pytest.mark.respx2(base_url=BASE_URL)
@pytest.mark.parametrize("provider,response_provider", PROVIDERS, ids=["aws", "azure", "gcp"])
async def test_async_external_storage_provider_and_admin_auth(
    provider: Provider, response_provider: dict[str, object], respx2_mock: MockRouter
) -> None:
    payload = configuration(response_provider)
    route = respx2_mock.post("/organization/external_storage").mock(return_value=httpx2.Response(200, json=payload))
    async with AsyncOpenAI(
        base_url=BASE_URL,
        api_key="test-project-key",
        admin_api_key="test-admin-key",
        _strict_response_validation=True,
    ) as client:
        result = await client.admin.organization.external_storage.create(project_id="proj_test", provider=provider)

    assert isinstance(result, ExternalStorageConfiguration)
    if provider["type"] == "gcp":
        assert isinstance(result.provider, GcpExternalStorageProvider)
    assert result.to_dict() == payload
    request = route.calls.last.request
    assert request.headers["Authorization"] == "Bearer test-admin-key"
    assert json.loads(request.content) == {"project_id": "proj_test", "provider": provider}


def mock_pages(respx2_mock: MockRouter) -> None:
    respx2_mock.get("/organization/external_storage").mock(
        side_effect=[
            httpx2.Response(
                200,
                json={
                    "object": "list",
                    "data": [configuration(PROVIDERS[0][1], storage_id)],
                    "first_id": storage_id,
                    "last_id": storage_id,
                    "has_more": has_more,
                },
            )
            for storage_id, has_more in [("extstorage_first", True), ("extstorage_last", False)]
        ]
    )


def assert_pagination_requests(respx2_mock: MockRouter) -> None:
    calls = cast("list[Call]", respx2_mock.calls)
    assert [dict(call.request.url.params) for call in calls] == [
        {"project_id": "proj_test", "order": "desc", "limit": "1"},
        {"project_id": "proj_test", "order": "desc", "limit": "1", "after": "extstorage_first"},
    ]
    assert all(call.request.headers["Authorization"] == "Bearer test-admin-key" for call in calls)


@pytest.mark.respx2(base_url=BASE_URL)
def test_sync_external_storage_pagination_preserves_filters_and_admin_auth(respx2_mock: MockRouter) -> None:
    mock_pages(respx2_mock)
    with OpenAI(base_url=BASE_URL, api_key="test-project-key", admin_api_key="test-admin-key") as client:
        items = list(client.admin.organization.external_storage.list(project_id="proj_test", order="desc", limit=1))

    assert [item.id for item in items] == ["extstorage_first", "extstorage_last"]
    assert_pagination_requests(respx2_mock)


@pytest.mark.respx2(base_url=BASE_URL)
async def test_async_external_storage_pagination_preserves_filters_and_admin_auth(respx2_mock: MockRouter) -> None:
    mock_pages(respx2_mock)
    async with AsyncOpenAI(base_url=BASE_URL, api_key="test-project-key", admin_api_key="test-admin-key") as client:
        items = [
            item
            async for item in client.admin.organization.external_storage.list(
                project_id="proj_test", order="desc", limit=1
            )
        ]

    assert [item.id for item in items] == ["extstorage_first", "extstorage_last"]
    assert_pagination_requests(respx2_mock)


@pytest.mark.respx2(base_url=BASE_URL)
def test_sync_external_storage_never_falls_back_to_project_key(
    monkeypatch: pytest.MonkeyPatch, respx2_mock: MockRouter
) -> None:
    monkeypatch.delenv("OPENAI_ADMIN_KEY", raising=False)
    with OpenAI(base_url=BASE_URL, api_key="test-project-key", admin_api_key=None) as client:
        with pytest.raises(TypeError, match="Could not resolve authentication method"):
            client.admin.organization.external_storage.retrieve("extstorage_test")
    assert len(respx2_mock.calls) == 0


@pytest.mark.respx2(base_url=BASE_URL)
async def test_async_external_storage_never_falls_back_to_project_key(
    monkeypatch: pytest.MonkeyPatch, respx2_mock: MockRouter
) -> None:
    monkeypatch.delenv("OPENAI_ADMIN_KEY", raising=False)
    async with AsyncOpenAI(base_url=BASE_URL, api_key="test-project-key", admin_api_key=None) as client:
        with pytest.raises(TypeError, match="Could not resolve authentication method"):
            await client.admin.organization.external_storage.retrieve("extstorage_test")
    assert len(respx2_mock.calls) == 0
