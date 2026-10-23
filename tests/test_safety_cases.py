from __future__ import annotations

from collections.abc import Callable

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from openai.types.safety import SafetyCase

BASE_URL = "https://example.com/v1"
CASE_ID = "case/with ?#%"


def safety_case(notice_type: str, reason: str | None) -> dict[str, object]:
    return {
        "id": CASE_ID,
        "object": "safety.case",
        "created_at": 123,
        "entity_identifier": "synthetic-entity",
        "reason": reason,
        "notice": {"type": notice_type, "future_notice_field": "retained"},
        "future_case_field": {"retained": True},
    }


def response_handler(
    payload: dict[str, object], requests: list[httpx2.Request]
) -> Callable[[httpx2.Request], httpx2.Response]:
    def handle(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, json=payload)

    return handle


def assert_request(requests: list[httpx2.Request]) -> None:
    assert len(requests) == 1
    request = requests[0]
    assert request.method == "GET"
    assert request.url.raw_path.split(b"?", 1)[0] == b"/v1/safety/cases/case%2Fwith%20%3F%23%25"
    assert dict(request.url.params) == {"trace": "contract"}
    assert request.content == b""
    assert request.headers["Authorization"] == "Bearer test-project-key"
    assert request.headers["X-Case-Trace"] == "caller-owned"


@pytest.mark.parametrize("notice_type", ["warning", "deactivation"])
@pytest.mark.parametrize("reason", [None, "synthetic reason"])
def test_sync_safety_case_contract(notice_type: str, reason: str | None) -> None:
    payload = safety_case(notice_type, reason)
    requests: list[httpx2.Request] = []
    with OpenAI(
        base_url=BASE_URL,
        api_key="test-project-key",
        admin_api_key="test-admin-key",
        http_client=httpx2.Client(transport=httpx2.MockTransport(response_handler(payload, requests))),
        _strict_response_validation=True,
    ) as client:
        result = client.safety.cases.retrieve(
            CASE_ID,
            extra_headers={"X-Case-Trace": "caller-owned"},
            extra_query={"trace": "contract"},
        )

    assert isinstance(result, SafetyCase)
    assert result.to_dict() == payload
    assert_request(requests)


@pytest.mark.asyncio
@pytest.mark.parametrize("notice_type", ["warning", "deactivation"])
@pytest.mark.parametrize("reason", [None, "synthetic reason"])
async def test_async_safety_case_contract(notice_type: str, reason: str | None) -> None:
    payload = safety_case(notice_type, reason)
    requests: list[httpx2.Request] = []
    async with AsyncOpenAI(
        base_url=BASE_URL,
        api_key="test-project-key",
        admin_api_key="test-admin-key",
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(response_handler(payload, requests))),
        _strict_response_validation=True,
    ) as client:
        result = await client.safety.cases.retrieve(
            CASE_ID,
            extra_headers={"X-Case-Trace": "caller-owned"},
            extra_query={"trace": "contract"},
        )

    assert isinstance(result, SafetyCase)
    assert result.to_dict() == payload
    assert_request(requests)


def test_safety_case_future_notice_is_preserved_by_default() -> None:
    payload = safety_case("future-notice", None)
    requests: list[httpx2.Request] = []
    with OpenAI(
        base_url=BASE_URL,
        api_key="test-project-key",
        admin_api_key="test-admin-key",
        http_client=httpx2.Client(transport=httpx2.MockTransport(response_handler(payload, requests))),
    ) as client:
        result = client.safety.cases.retrieve(CASE_ID)

    assert result.to_dict() == payload
    assert len(requests) == 1
    assert requests[0].headers["Authorization"] == "Bearer test-project-key"


def test_sync_safety_case_never_uses_admin_key_as_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    requests: list[httpx2.Request] = []
    with OpenAI(
        base_url=BASE_URL,
        api_key=None,
        admin_api_key="test-admin-key",
        http_client=httpx2.Client(
            transport=httpx2.MockTransport(response_handler(safety_case("warning", None), requests))
        ),
    ) as client:
        with pytest.raises(TypeError, match="Could not resolve authentication method"):
            client.safety.cases.retrieve(CASE_ID)
    assert not requests


@pytest.mark.asyncio
async def test_async_safety_case_never_uses_admin_key_as_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    requests: list[httpx2.Request] = []
    async with AsyncOpenAI(
        base_url=BASE_URL,
        api_key=None,
        admin_api_key="test-admin-key",
        http_client=httpx2.AsyncClient(
            transport=httpx2.MockTransport(response_handler(safety_case("warning", None), requests))
        ),
    ) as client:
        with pytest.raises(TypeError, match="Could not resolve authentication method"):
            await client.safety.cases.retrieve(CASE_ID)
    assert not requests
