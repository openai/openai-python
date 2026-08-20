from __future__ import annotations

import inspect
from typing import Any, NoReturn

import httpx2
import pytest

from openai import AzureOpenAI, OpenAIError, AsyncAzureOpenAI
from openai.lib.azure import API_KEY_SENTINEL, MutuallyExclusiveAuthError


@pytest.fixture(autouse=True)
def azure_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "fake-ambient-key")
    monkeypatch.setenv("AZURE_OPENAI_AD_TOKEN", "fake-ambient-token")
    monkeypatch.setenv("OPENAI_API_KEY", "fake-unrelated-openai-key")


def make_client(asynchronous: bool, requests: list[httpx2.Request], **kwargs: Any) -> Any:
    def send(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, json={"data": []})

    transport = httpx2.MockTransport(send)
    http_client = httpx2.AsyncClient(transport=transport) if asynchronous else httpx2.Client(transport=transport)
    cls: Any = AsyncAzureOpenAI if asynchronous else AzureOpenAI
    return cls(
        azure_endpoint="https://azure.test",
        api_version="2024-02-01",
        http_client=http_client,
        **kwargs,
    )


async def resolve(value: Any) -> Any:
    return await value if inspect.isawaitable(value) else value


def auth(headers: Any) -> dict[str, str]:
    return {key.lower(): value for key, value in headers.items() if key.lower() in {"authorization", "api-key"}}


def credentials(mode: str, value: str = "fake-selected") -> dict[str, Any]:
    if mode == "api_key":
        return {"api_key": value}
    if mode == "azure_ad_token":
        return {"azure_ad_token": value}
    return {"azure_ad_token_provider": lambda: value}


def expected_auth(mode: str, value: str = "fake-selected") -> dict[str, str]:
    return {"api-key": value} if mode == "api_key" else {"authorization": f"Bearer {value}"}


MODES = ["api_key", "azure_ad_token", "azure_ad_token_provider"]


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("mode", MODES)
@pytest.mark.parametrize("ambient_token", [False, True])
async def test_explicit_mode_wins(
    asynchronous: bool, mode: str, ambient_token: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    if not ambient_token:
        monkeypatch.delenv("AZURE_OPENAI_AD_TOKEN")
    requests: list[httpx2.Request] = []
    client = make_client(asynchronous, requests, **credentials(mode))
    try:
        for selected in (client, client.copy(), client.with_options(timeout=20)):
            await resolve(selected.models.list())
            _, headers = await resolve(selected._configure_realtime("test-model", {}))
            assert auth(headers) == expected_auth(mode)
        assert [auth(request.headers) for request in requests] == [expected_auth(mode)] * 3
    finally:
        await resolve(client.close())


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("mode", ["none", "key", "token", "both"])
async def test_environment_fallback(asynchronous: bool, mode: str, monkeypatch: pytest.MonkeyPatch) -> None:
    if mode not in {"key", "both"}:
        monkeypatch.delenv("AZURE_OPENAI_API_KEY")
    if mode not in {"token", "both"}:
        monkeypatch.delenv("AZURE_OPENAI_AD_TOKEN")
    if mode == "none":
        cls: Any = AsyncAzureOpenAI if asynchronous else AzureOpenAI
        with pytest.raises(OpenAIError, match="Missing credentials"):
            cls(azure_endpoint="https://azure.test", api_version="2024-02-01")
        return

    expected = (
        expected_auth("api_key", "fake-ambient-key")
        if mode == "key"
        else expected_auth("azure_ad_token", "fake-ambient-token")
    )
    requests: list[httpx2.Request] = []
    client = make_client(asynchronous, requests)
    try:
        # Copies retain the resolved credential, even after environment changes.
        monkeypatch.setenv("AZURE_OPENAI_API_KEY", "fake-new-key")
        monkeypatch.setenv("AZURE_OPENAI_AD_TOKEN", "fake-new-token")
        for selected in (client, client.copy(), client.with_options()):
            await resolve(selected.models.list())
            _, headers = await resolve(selected._configure_realtime("test-model", {}))
            assert auth(headers) == expected
        assert [auth(request.headers) for request in requests] == [expected] * 3
    finally:
        await resolve(client.close())


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("source", MODES)
@pytest.mark.parametrize("target", MODES)
@pytest.mark.parametrize("method", ["copy", "with_options"])
async def test_copy_replaces_auth_mode(asynchronous: bool, source: str, target: str, method: str) -> None:
    requests: list[httpx2.Request] = []
    client = make_client(asynchronous, requests, **credentials(source, "fake-original"))
    try:
        copied = getattr(client, method)(**credentials(target))
        await resolve(copied.models.list())
        _, headers = await resolve(copied._configure_realtime("test-model", {}))
        assert auth(headers) == expected_auth(target)
        await resolve(client.models.list())
        assert [auth(request.headers) for request in requests] == [
            expected_auth(target),
            expected_auth(source, "fake-original"),
        ]
    finally:
        await resolve(client.close())


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("modes", [(MODES[0], MODES[1]), (MODES[0], MODES[2]), (MODES[1], MODES[2]), tuple(MODES)])
async def test_conflicting_explicit_credentials(asynchronous: bool, modes: tuple[str, ...]) -> None:
    kwargs = {key: value for mode in modes for key, value in credentials(mode).items()}
    cls: Any = AsyncAzureOpenAI if asynchronous else AzureOpenAI
    with pytest.raises(MutuallyExclusiveAuthError):
        cls(azure_endpoint="https://azure.test", api_version="2024-02-01", **kwargs)
    client = make_client(asynchronous, [], api_key="fake-original")
    try:
        for method in (client.copy, client.with_options):
            with pytest.raises(MutuallyExclusiveAuthError):
                method(**kwargs)
    finally:
        await resolve(client.close())


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("awaitable_provider", [False, True])
async def test_provider_refresh_on_retry(asynchronous: bool, awaitable_provider: bool) -> None:
    if awaitable_provider and not asynchronous:
        pytest.skip("Synchronous clients require synchronous providers")
    requests: list[httpx2.Request] = []
    calls = 0

    def token() -> str:
        nonlocal calls
        calls += 1
        return f"fake-token-{calls}"

    async def async_token() -> str:
        return token()

    def send(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(500 if len(requests) == 1 else 200, json={"data": []}, headers={"retry-after-ms": "1"})

    cls: Any = AsyncAzureOpenAI if asynchronous else AzureOpenAI
    transport = httpx2.MockTransport(send)
    http_client = httpx2.AsyncClient(transport=transport) if asynchronous else httpx2.Client(transport=transport)
    client = cls(
        azure_endpoint="https://azure.test",
        api_version="2024-02-01",
        http_client=http_client,
        azure_ad_token_provider=async_token if awaitable_provider else token,
        max_retries=1,
    )
    try:
        await resolve(client.with_options().models.list())
        assert [auth(request.headers) for request in requests] == [
            expected_auth("azure_ad_token", "fake-token-1"),
            expected_auth("azure_ad_token", "fake-token-2"),
        ]
        _, headers = await resolve(client._configure_realtime("test-model", {}))
        assert auth(headers) == expected_auth("azure_ad_token", "fake-token-3")
        assert calls == 3
    finally:
        await resolve(client.close())


@pytest.mark.parametrize("asynchronous", [False, True])
async def test_internal_sentinel_is_not_a_conflicting_credential(asynchronous: bool) -> None:
    requests: list[httpx2.Request] = []
    client = make_client(
        asynchronous, requests, api_key=API_KEY_SENTINEL, azure_ad_token_provider=lambda: "fake-selected"
    )
    try:
        await resolve(client.models.list())
        assert auth(requests[0].headers) == expected_auth("azure_ad_token")
    finally:
        await resolve(client.close())


@pytest.mark.parametrize("asynchronous", [False, True])
async def test_callable_api_key_refresh_and_copy(asynchronous: bool, monkeypatch: pytest.MonkeyPatch) -> None:
    def unexpected_connection(*_args: Any, **_kwargs: Any) -> NoReturn:
        pytest.fail("The callable API-key test must not open a network connection")

    monkeypatch.setattr("socket.socket.connect", unexpected_connection)
    monkeypatch.setattr("socket.socket.connect_ex", unexpected_connection)
    requests: list[httpx2.Request] = []
    calls = 0

    def key() -> str:
        nonlocal calls
        calls += 1
        return f"fake-key-{calls}"

    async def async_key() -> str:
        return key()

    def send(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(
            500 if len(requests) == 1 else 200,
            json={"data": []},
            headers={"retry-after-ms": "1"},
        )

    cls: Any = AsyncAzureOpenAI if asynchronous else AzureOpenAI
    transport = httpx2.MockTransport(send)
    http_client = httpx2.AsyncClient(transport=transport) if asynchronous else httpx2.Client(transport=transport)
    provider = async_key if asynchronous else key
    client = cls(
        azure_endpoint="https://azure.test",
        api_version="2024-02-01",
        http_client=http_client,
        api_key=provider,
        max_retries=1,
    )
    try:
        # Retry, a copy after refresh, and a realtime connection all refresh.
        await resolve(client.models.list())
        copied = client.copy()
        await resolve(copied.models.list())
        websocket_headers: list[dict[str, str]] = []

        def connect(*_args: Any, **kwargs: Any) -> Any:
            websocket_headers.append(auth(kwargs["additional_headers"]))
            return None

        async def async_connect(*args: Any, **kwargs: Any) -> Any:
            return connect(*args, **kwargs)

        monkeypatch.setattr("websockets.sync.client.connect", connect)
        # Azure uses its own async connector. Patching its base class misses
        # already-imported subclasses and makes the test depend on import order.
        monkeypatch.setattr("openai.lib._azure_websocket._AzureWebSocketConnect", async_connect)
        for resource in (copied.realtime, copied.beta.realtime):
            await resolve(resource.connect(model="test-model").enter())
        assert websocket_headers == [expected_auth("api_key", f"fake-key-{i}") for i in (4, 5)]
        assert [auth(request.headers) for request in requests] == [
            expected_auth("api_key", f"fake-key-{i}") for i in (1, 2, 3)
        ]
        assert calls == 5

        # Replacing a refreshed callable key must discard both its cached value
        # and provider. Switching back must retain the callable, not that cache.
        calls_before_ad_request = calls
        ad_client = copied.with_options(azure_ad_token="fake-selected")
        await resolve(ad_client.models.list())
        assert auth(requests[-1].headers) == expected_auth("azure_ad_token")
        assert calls == calls_before_ad_request
        restored = ad_client.with_options(api_key=provider)
        await resolve(restored.models.list())
        assert auth(requests[-1].headers) == expected_auth("api_key", "fake-key-6")
    finally:
        await resolve(client.close())
