from __future__ import annotations

import json
from typing import Any, NoReturn, cast

import httpx
import respx
import pytest
from respx.models import Call

import openai.auth._workload as workload
from openai import OpenAI, OAuthError, AsyncOpenAI, APITimeoutError, APIConnectionError
from openai.auth import WorkloadIdentity

httpx2 = pytest.importorskip("httpx2")


def workload_identity(get_token: Any = lambda: "subject-token") -> WorkloadIdentity:
    return {
        "identity_provider_id": "idp_123",
        "service_account_id": "sa_123",
        "provider": {"get_token": get_token, "token_type": "jwt"},
    }


def exchange_payload(access_token: str) -> dict[str, object]:
    return {"access_token": access_token, "expires_in": 3600}


def forbidden_httpx_send(*_args: Any, **_kwargs: Any) -> NoReturn:
    pytest.fail("HTTPX unexpectedly sent a request")


def test_sync_httpx2_workload_exchange_is_native_and_cached(monkeypatch: pytest.MonkeyPatch) -> None:
    exchange_requests: list[Any] = []
    api_requests: list[Any] = []
    provider_calls = 0

    def get_token() -> str:
        nonlocal provider_calls
        provider_calls += 1
        return "subject-token"

    def exchange_handler(request: Any) -> Any:
        exchange_requests.append(request)
        return httpx2.Response(200, request=request, json=exchange_payload("access-token"))

    def exchange_client(**kwargs: Any) -> Any:
        assert kwargs == {"follow_redirects": False}
        return httpx2.Client(transport=httpx2.MockTransport(exchange_handler), trust_env=False)

    def api_handler(request: Any) -> Any:
        api_requests.append(request)
        return httpx2.Response(200, request=request, json={"object": "list", "data": []})

    monkeypatch.setattr(workload, "DefaultHttpx2Client", exchange_client)
    monkeypatch.setattr(httpx.Client, "send", forbidden_httpx_send)

    with OpenAI(
        workload_identity=workload_identity(get_token),
        base_url="https://api.example.test/v1",
        http_client=httpx2.Client(transport=httpx2.MockTransport(api_handler), trust_env=False),
        max_retries=0,
    ) as client:
        assert client.models.list().object == "list"
        assert client.models.list().object == "list"

    assert provider_calls == 1
    assert len(exchange_requests) == 1
    assert len(api_requests) == 2
    assert isinstance(exchange_requests[0], httpx2.Request)
    assert str(exchange_requests[0].url) == "https://auth.openai.com/oauth/token"
    assert json.loads(exchange_requests[0].content) == {
        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
        "subject_token": "subject-token",
        "subject_token_type": "urn:ietf:params:oauth:token-type:jwt",
        "identity_provider_id": "idp_123",
        "service_account_id": "sa_123",
    }
    assert all(isinstance(request, httpx2.Request) for request in api_requests)
    assert [request.headers["authorization"] for request in api_requests] == ["Bearer access-token"] * 2


async def test_async_httpx2_workload_401_reexchanges_with_sync_native_client(monkeypatch: pytest.MonkeyPatch) -> None:
    exchange_requests: list[Any] = []
    api_requests: list[Any] = []
    api_authorizations: list[str] = []
    tokens = iter(["access-token-1", "access-token-2"])

    def exchange_handler(request: Any) -> Any:
        exchange_requests.append(request)
        return httpx2.Response(200, request=request, json=exchange_payload(next(tokens)))

    def exchange_client(**kwargs: Any) -> Any:
        assert kwargs == {"follow_redirects": False}
        return httpx2.Client(transport=httpx2.MockTransport(exchange_handler), trust_env=False)

    async def api_handler(request: Any) -> Any:
        api_requests.append(request)
        api_authorizations.append(request.headers["authorization"])
        status_code = 401 if len(api_requests) == 1 else 200
        return httpx2.Response(status_code, request=request, json={"object": "list", "data": []})

    monkeypatch.setattr(workload, "DefaultHttpx2Client", exchange_client)
    monkeypatch.setattr(httpx.Client, "send", forbidden_httpx_send)
    monkeypatch.setattr(httpx.AsyncClient, "send", forbidden_httpx_send)

    async with AsyncOpenAI(
        workload_identity=workload_identity(),
        base_url="https://api.example.test/v1",
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(api_handler), trust_env=False),
        max_retries=0,
    ) as client:
        assert (await client.models.list()).object == "list"

    assert len(exchange_requests) == 2
    assert all(isinstance(request, httpx2.Request) for request in exchange_requests)
    assert len(api_requests) == 2
    assert all(isinstance(request, httpx2.Request) for request in api_requests)
    assert api_authorizations == ["Bearer access-token-1", "Bearer access-token-2"]


def test_httpx2_workload_oauth_error_preserves_native_response(monkeypatch: pytest.MonkeyPatch) -> None:
    api_calls = 0

    def exchange_handler(request: Any) -> Any:
        return httpx2.Response(
            401,
            request=request,
            json={"error": "invalid_grant", "error_description": "invalid workload identity"},
        )

    def exchange_client(**kwargs: Any) -> Any:
        assert kwargs == {"follow_redirects": False}
        return httpx2.Client(transport=httpx2.MockTransport(exchange_handler), trust_env=False)

    def api_handler(request: Any) -> Any:
        nonlocal api_calls
        api_calls += 1
        return httpx2.Response(200, request=request, json={"object": "list", "data": []})

    monkeypatch.setattr(workload, "DefaultHttpx2Client", exchange_client)

    with OpenAI(
        workload_identity=workload_identity(),
        base_url="https://api.example.test/v1",
        http_client=httpx2.Client(transport=httpx2.MockTransport(api_handler), trust_env=False),
        max_retries=0,
    ) as client:
        with pytest.raises(OAuthError) as exc_info:
            client.models.list()

    assert exc_info.value.message == "invalid workload identity"
    assert isinstance(exc_info.value.response, httpx2.Response)
    assert isinstance(exc_info.value.request, httpx2.Request)
    assert api_calls == 0


@pytest.mark.parametrize(
    ("failure", "expected"),
    [("timeout", APITimeoutError), ("connection", APIConnectionError)],
)
def test_httpx2_workload_exchange_transport_failure(
    failure: str, expected: type[Exception], monkeypatch: pytest.MonkeyPatch
) -> None:
    def exchange_handler(request: Any) -> Any:
        if failure == "timeout":
            raise httpx2.ReadTimeout("exchange timeout", request=request)
        raise httpx2.ConnectError("exchange unavailable", request=request)

    def exchange_client(**kwargs: Any) -> Any:
        assert kwargs == {"follow_redirects": False}
        return httpx2.Client(transport=httpx2.MockTransport(exchange_handler), trust_env=False)

    def api_handler(request: Any) -> Any:
        return httpx2.Response(200, request=request)

    monkeypatch.setattr(workload, "DefaultHttpx2Client", exchange_client)

    with OpenAI(
        workload_identity=workload_identity(),
        base_url="https://api.example.test/v1",
        http_client=httpx2.Client(transport=httpx2.MockTransport(api_handler)),
        max_retries=0,
    ) as client:
        with pytest.raises(expected) as exc_info:
            client.models.list()

    assert type(exc_info.value.__cause__).__module__ == "httpx2"


def test_httpx_workload_exchange_stays_httpx_when_httpx2_is_installed(monkeypatch: pytest.MonkeyPatch) -> None:
    api_requests: list[httpx.Request] = []

    def forbidden_httpx2(**_kwargs: Any) -> Any:
        pytest.fail("HTTPX2 unexpectedly created a workload exchange client")

    def api_handler(request: httpx.Request) -> httpx.Response:
        api_requests.append(request)
        return httpx.Response(200, request=request, json={"object": "list", "data": []})

    monkeypatch.setattr(workload, "DefaultHttpx2Client", forbidden_httpx2)

    with respx.mock(assert_all_mocked=False) as router:
        exchange = router.post("https://auth.openai.com/oauth/token").mock(
            return_value=httpx.Response(200, json=exchange_payload("access-token"))
        )
        with OpenAI(
            workload_identity=workload_identity(),
            base_url="https://api.example.test/v1",
            http_client=httpx.Client(transport=httpx.MockTransport(api_handler), trust_env=False),
            max_retries=0,
        ) as client:
            assert client.models.list().object == "list"

    assert exchange.call_count == 1
    assert len(api_requests) == 1
    assert isinstance(cast(Call, exchange.calls[0]).request, httpx.Request)
    assert isinstance(api_requests[0], httpx.Request)
