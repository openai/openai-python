from __future__ import annotations

from typing import Any, Callable
from importlib import import_module
from unittest.mock import AsyncMock, MagicMock

import httpx2
import pytest

from openai import AzureOpenAI, AsyncAzureOpenAI, DefaultHttpxClient, DefaultAioHttpClient, DefaultAsyncHttpxClient
from openai._models import FinalRequestOptions
from openai.lib.azure import API_KEY_SENTINEL

ORIGIN = "https://origin.test"
FAKE_KEY = "fake-azure-redirect-key"
SYNC_BACKENDS = ["httpx", "httpx2", "default"]
ASYNC_BACKENDS = [*SYNC_BACKENDS, "aiohttp"]
TARGETS = [
    ("/final", True),
    ("https://ORIGIN.test:443/final", True),
    ("https://other.test/final", False),
    ("//other.test/final", False),
    ("https://origin.test:444/final", False),
    ("http://origin.test/final", False),
    ("https://origin.test@other.test/final", False),
]


def http_module(backend: str) -> Any:
    return pytest.importorskip("httpx") if backend == "httpx" else httpx2


def azure_options() -> dict[str, Any]:
    return dict(api_key=FAKE_KEY, azure_endpoint=ORIGIN, api_version="2024-01-01", max_retries=0)


def mock_aiohttp(monkeypatch: pytest.MonkeyPatch, handler: Callable[[Any], Any]) -> None:
    # Exercise the real vendored adapter, but never open a network connection.
    aiohttp = import_module("aiohttp")

    def request(_session: Any, method: str, url: str, **kwargs: Any) -> Any:
        assert kwargs["allow_redirects"] is False
        result = handler(httpx2.Request(method, url, headers=kwargs["headers"], content=kwargs["data"]))

        async def chunks(_size: int) -> Any:
            yield result.content

        response = MagicMock(spec=aiohttp.ClientResponse)
        response.status = result.status_code
        response.reason = result.reason_phrase
        response.raw_headers = result.headers.raw
        response.content.iter_chunked.side_effect = chunks
        response.__aexit__ = AsyncMock()
        context = MagicMock()
        context.__aenter__ = AsyncMock(return_value=response)
        return context

    monkeypatch.setattr(aiohttp.ClientSession, "request", request)


def make_http_client(
    backend: str,
    handler: Callable[[Any], Any],
    *,
    asynchronous: bool = False,
    monkeypatch: pytest.MonkeyPatch | None = None,
    **kwargs: Any,
) -> Any:
    module = http_module(backend)
    if backend == "aiohttp":
        assert monkeypatch is not None
        mock_aiohttp(monkeypatch, handler)
        return DefaultAioHttpClient(trust_env=False, **kwargs)
    if backend == "default":
        cls = DefaultAsyncHttpxClient if asynchronous else DefaultHttpxClient
    else:
        cls = module.AsyncClient if asynchronous else module.Client
        kwargs.setdefault("follow_redirects", True)
    return cls(transport=module.MockTransport(handler), trust_env=False, **kwargs)


def redirect_handler(backend: str, targets: list[str], seen: list[Any], status: int = 307) -> Callable[[Any], Any]:
    module = http_module(backend)

    def handler(request: Any) -> Any:
        seen.append(request)
        if len(seen) <= len(targets):
            return module.Response(status, headers={"location": targets[len(seen) - 1]}, content=b"redirect")
        return module.Response(200, json={"object": "list", "data": []})

    return handler


@pytest.mark.parametrize("backend", SYNC_BACKENDS)
@pytest.mark.parametrize("status", [301, 302, 303, 307, 308])
@pytest.mark.parametrize("target,retained", TARGETS)
def test_sync_redirect_origin(backend: str, status: int, target: str, retained: bool) -> None:
    seen: list[Any] = []
    transport = make_http_client(backend, redirect_handler(backend, [target], seen, status))
    with AzureOpenAI(**azure_options(), http_client=transport) as client:
        result = client.models.with_raw_response.list(extra_headers={"Authorization": "Bearer fake-token"})
        assert len(result.http_response.history) == 1
    assert len(seen) == 2
    assert seen[0].headers["api-key"] == FAKE_KEY
    assert seen[1].headers.get("api-key") == (FAKE_KEY if retained else None)
    assert ("authorization" in seen[1].headers) == retained


@pytest.mark.parametrize("backend", ASYNC_BACKENDS)
@pytest.mark.parametrize("status", [301, 302, 303, 307, 308])
@pytest.mark.parametrize("target,retained", TARGETS)
async def test_async_redirect_origin(
    backend: str, status: int, target: str, retained: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen: list[Any] = []
    transport = make_http_client(
        backend, redirect_handler(backend, [target], seen, status), asynchronous=True, monkeypatch=monkeypatch
    )
    async with AsyncAzureOpenAI(**azure_options(), http_client=transport) as client:
        result = await client.models.with_raw_response.list(extra_headers={"Authorization": "Bearer fake-token"})
        assert len(result.http_response.history) == 1
    assert len(seen) == 2
    assert seen[0].headers["api-key"] == FAKE_KEY
    assert seen[1].headers.get("api-key") == (FAKE_KEY if retained else None)
    assert ("authorization" in seen[1].headers) == retained


@pytest.mark.parametrize("backend", SYNC_BACKENDS)
@pytest.mark.parametrize("follow", [False, True])
def test_sync_redirect_options_and_chain(backend: str, follow: bool) -> None:
    seen: list[Any] = []
    targets = ["/same", "https://other.test/final", ORIGIN + "/return"]
    transport = make_http_client(backend, redirect_handler(backend, targets, seen), follow_redirects=not follow)
    with AzureOpenAI(**azure_options(), http_client=transport) as client:
        response = client._send_request(
            client._build_request(FinalRequestOptions(method="get", url="/start")),
            stream=True,
            follow_redirects=follow,
        )
        assert response.status_code == (200 if follow else 307)
        assert len(response.history) == (3 if follow else 0)
        response.close()
    assert [r.headers.get("api-key") for r in seen] == ([FAKE_KEY, FAKE_KEY, None, None] if follow else [FAKE_KEY])


@pytest.mark.parametrize("backend", ASYNC_BACKENDS)
@pytest.mark.parametrize("follow", [False, True])
async def test_async_redirect_options_and_chain(backend: str, follow: bool, monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[Any] = []
    targets = ["/same", "https://other.test/final", ORIGIN + "/return"]
    transport = make_http_client(
        backend,
        redirect_handler(backend, targets, seen),
        asynchronous=True,
        monkeypatch=monkeypatch,
        follow_redirects=not follow,
    )
    async with AsyncAzureOpenAI(**azure_options(), http_client=transport) as client:
        response = await client._send_request(
            client._build_request(FinalRequestOptions(method="get", url="/start")),
            stream=True,
            follow_redirects=follow,
        )
        assert response.status_code == (200 if follow else 307)
        assert len(response.history) == (3 if follow else 0)
        await response.aclose()
    assert [r.headers.get("api-key") for r in seen] == ([FAKE_KEY, FAKE_KEY, None, None] if follow else [FAKE_KEY])


@pytest.mark.parametrize("backend", SYNC_BACKENDS)
def test_sync_shared_client_and_explicit_credentials(backend: str) -> None:
    seen: list[Any] = []
    transport = make_http_client(backend, redirect_handler(backend, ["https://other.test/final"], seen))
    with AzureOpenAI(**azure_options(), http_client=transport) as client:
        copy = client.copy()
        assert len(transport.event_hooks["request"]) == 1
        copy.models.list(extra_headers={"API-KEY": "fake-explicit-key"})
        assert "fake-explicit-key" in seen[0].headers.get_list("api-key")
        assert "api-key" not in seen[1].headers
        transport.get("https://other.test/direct", headers={"api-key": "fake-unrelated-key"})
        assert seen[-1].headers["api-key"] == "fake-unrelated-key"


@pytest.mark.parametrize("backend", ASYNC_BACKENDS)
async def test_async_shared_client_and_explicit_credentials(backend: str, monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[Any] = []
    transport = make_http_client(
        backend,
        redirect_handler(backend, ["https://other.test/final"], seen),
        asynchronous=True,
        monkeypatch=monkeypatch,
    )
    async with AsyncAzureOpenAI(**azure_options(), http_client=transport) as client:
        copy = client.copy()
        assert len(transport.event_hooks["request"]) == 1
        await copy.models.list(extra_headers={"API-KEY": "fake-explicit-key"})
        assert "fake-explicit-key" in seen[0].headers.get_list("api-key")
        assert "api-key" not in seen[1].headers
        await transport.get("https://other.test/direct", headers={"api-key": "fake-unrelated-key"})
        assert seen[-1].headers["api-key"] == "fake-unrelated-key"


@pytest.mark.parametrize("backend", SYNC_BACKENDS)
@pytest.mark.parametrize("target,retained", TARGETS[:3])
def test_sync_bearer_authentication(backend: str, target: str, retained: bool) -> None:
    seen: list[Any] = []
    transport = make_http_client(backend, redirect_handler(backend, [target], seen))
    options = azure_options()
    options["api_key"] = API_KEY_SENTINEL
    with AzureOpenAI(**options, azure_ad_token_provider=lambda: "fake-ad-token", http_client=transport) as client:
        client.models.list()
    assert seen[0].headers["authorization"] == "Bearer fake-ad-token"
    assert seen[1].headers.get("authorization") == ("Bearer fake-ad-token" if retained else None)
    assert all("api-key" not in request.headers for request in seen)


@pytest.mark.parametrize("backend", ASYNC_BACKENDS)
@pytest.mark.parametrize("target,retained", TARGETS[:3])
async def test_async_bearer_authentication(
    backend: str, target: str, retained: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen: list[Any] = []
    transport = make_http_client(
        backend, redirect_handler(backend, [target], seen), asynchronous=True, monkeypatch=monkeypatch
    )
    options = azure_options()
    options["api_key"] = API_KEY_SENTINEL

    async def token() -> str:
        return "fake-ad-token"

    async with AsyncAzureOpenAI(**options, azure_ad_token_provider=token, http_client=transport) as client:
        await client.models.list()
    assert seen[0].headers["authorization"] == "Bearer fake-ad-token"
    assert seen[1].headers.get("authorization") == ("Bearer fake-ad-token" if retained else None)
    assert all("api-key" not in request.headers for request in seen)
