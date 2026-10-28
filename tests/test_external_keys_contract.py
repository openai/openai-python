from __future__ import annotations

import json
from typing import Any, Sequence, cast

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from tests.respx2 import MockRouter
from tests.respx2.models import Call

BASE_URL = "https://example.com/v1"
PROVIDERS: list[dict[str, Any]] = [
    {
        "type": "aws",
        "name": "AWS",
        "role_arn": "arn:aws:iam::000000000000:role/test",
        "external_id": "org_test",
        "kms_arn": "arn:aws:kms:us-east-1:000000000000:key/test",
    },
    {
        "type": "gcp",
        "name": "GCP",
        "audience": "org_test",
        "kms_key_location": "global",
        "kms_key_name": "key",
        "kms_key_ring_name": "ring",
        "kms_project_id": "project",
        "workload_identity_pool_id": "pool",
        "workload_identity_project_number": "123",
        "workload_identity_provider_id": "provider",
        "purpose": "psp_decryption",
        "kms_key_version": "1",
    },
    {
        "type": "azure",
        "name": "Azure",
        "key_name": "org_test--key",
        "tenant_id": "tenant",
        "vault_uri": "https://example.vault.azure.net",
        "purpose": "psp_decryption",
        "key_version": "version",
    },
]


def key_payload(key_id: str = "extkey_test", object_type: str = "organization.external_key") -> dict[str, Any]:
    return {
        "id": key_id,
        "object": object_type,
        "type": "aws",
        "name": "test",
        "api_project_ids": [],
        "workspace_id": "",
        "created_at": 123,
    }


@pytest.mark.respx2(base_url=BASE_URL)
@pytest.mark.parametrize("provider", PROVIDERS, ids=["aws", "gcp", "azure"])
def test_external_key_providers(provider: dict[str, Any], respx2_mock: MockRouter) -> None:
    payload = key_payload()
    route = respx2_mock.post("/organization/external_keys").mock(return_value=httpx2.Response(200, json=payload))
    with OpenAI(
        base_url=BASE_URL, api_key="project-test", admin_api_key="admin-test", _strict_response_validation=True
    ) as client:
        result = client.admin.organization.external_keys.create(**provider)
    assert result.to_dict() == payload
    assert result.purpose is None
    assert route.calls.last.request.headers["Authorization"] == "Bearer admin-test"
    assert json.loads(route.calls.last.request.content) == provider


@pytest.mark.respx2(base_url=BASE_URL)
@pytest.mark.parametrize("provider", PROVIDERS, ids=["aws", "gcp", "azure"])
async def test_async_external_key_providers(provider: dict[str, Any], respx2_mock: MockRouter) -> None:
    payload = key_payload()
    route = respx2_mock.post("/organization/external_keys").mock(return_value=httpx2.Response(200, json=payload))
    async with AsyncOpenAI(
        base_url=BASE_URL, api_key="project-test", admin_api_key="admin-test", _strict_response_validation=True
    ) as client:
        result = await client.admin.organization.external_keys.create(**provider)
    assert result.to_dict() == payload
    assert route.calls.last.request.headers["Authorization"] == "Bearer admin-test"
    assert json.loads(route.calls.last.request.content) == provider


def mock_pages(respx2_mock: MockRouter) -> None:
    respx2_mock.get("/organization/external_keys").mock(
        side_effect=[
            httpx2.Response(
                200,
                json={
                    "object": "list",
                    "data": [key_payload(key_id)],
                    "first_id": key_id,
                    "last_id": key_id,
                    "has_more": more,
                },
            )
            for key_id, more in [("extkey_first", True), ("extkey_last", False)]
        ]
    )


def recorded_requests(respx2_mock: MockRouter) -> list[httpx2.Request]:
    return [call.request for call in cast(Sequence[Call], respx2_mock.calls)]


def assert_pages(respx2_mock: MockRouter) -> None:
    requests = recorded_requests(respx2_mock)
    assert [dict(request.url.params) for request in requests] == [
        {"purpose": "psp_decryption", "limit": "1"},
        {"purpose": "psp_decryption", "limit": "1", "after": "extkey_first"},
    ]
    assert all(request.headers["Authorization"] == "Bearer admin-test" for request in requests)


@pytest.mark.respx2(base_url=BASE_URL)
def test_external_key_pagination(respx2_mock: MockRouter) -> None:
    mock_pages(respx2_mock)
    with OpenAI(base_url=BASE_URL, api_key="project-test", admin_api_key="admin-test") as client:
        items = list(client.admin.organization.external_keys.list(purpose="psp_decryption", limit=1))
    assert [item.id for item in items] == ["extkey_first", "extkey_last"]
    assert_pages(respx2_mock)


@pytest.mark.respx2(base_url=BASE_URL)
async def test_async_external_key_pagination(respx2_mock: MockRouter) -> None:
    mock_pages(respx2_mock)
    async with AsyncOpenAI(base_url=BASE_URL, api_key="project-test", admin_api_key="admin-test") as client:
        items = [item async for item in client.admin.organization.external_keys.list(purpose="psp_decryption", limit=1)]
    assert [item.id for item in items] == ["extkey_first", "extkey_last"]
    assert_pages(respx2_mock)


@pytest.mark.respx2(base_url=BASE_URL)
def test_external_key_lifecycle_and_raw_response(respx2_mock: MockRouter) -> None:
    base = "/organization/external_keys/extkey_test"
    respx2_mock.get(base).mock(return_value=httpx2.Response(200, json=key_payload()))
    respx2_mock.post(base + "/validate").mock(return_value=httpx2.Response(200, json={"status": "valid"}))
    deleted = key_payload(object_type="organization.external_key.deleted")
    respx2_mock.delete(base).mock(return_value=httpx2.Response(200, json=deleted))
    with OpenAI(base_url=BASE_URL, api_key="project-test", admin_api_key="admin-test") as client:
        keys = client.admin.organization.external_keys
        retrieved = keys.with_raw_response.retrieve("extkey_test").parse()
        validated = keys.validate("extkey_test")
        deletion = keys.delete("extkey_test")
        assert retrieved.id == "extkey_test"
        assert validated.status == "valid"
        assert deletion.to_dict() == deleted
    assert all(request.headers["Authorization"] == "Bearer admin-test" for request in recorded_requests(respx2_mock))


@pytest.mark.respx2(base_url=BASE_URL)
async def test_async_external_key_lifecycle_and_streamed_response(respx2_mock: MockRouter) -> None:
    base = "/organization/external_keys/extkey_test"
    respx2_mock.get(base).mock(return_value=httpx2.Response(200, json=key_payload()))
    respx2_mock.post(base + "/validate").mock(return_value=httpx2.Response(200, json={"status": "valid"}))
    deleted = key_payload(object_type="organization.external_key.deleted")
    respx2_mock.delete(base).mock(return_value=httpx2.Response(200, json=deleted))
    async with AsyncOpenAI(base_url=BASE_URL, api_key="project-test", admin_api_key="admin-test") as client:
        keys = client.admin.organization.external_keys
        async with keys.with_streaming_response.retrieve("extkey_test") as response:
            retrieved = await response.parse()
        validated = await keys.validate("extkey_test")
        deletion = await keys.delete("extkey_test")
        assert retrieved.id == "extkey_test"
        assert validated.status == "valid"
        assert deletion.to_dict() == deleted
    assert all(request.headers["Authorization"] == "Bearer admin-test" for request in recorded_requests(respx2_mock))
