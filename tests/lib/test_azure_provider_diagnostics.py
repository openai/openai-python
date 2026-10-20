from __future__ import annotations

import asyncio
import inspect
import traceback
from typing import Any, Callable, NoReturn, NamedTuple
from typing_extensions import override

import httpx2
import pytest

from openai import AzureOpenAI, AsyncAzureOpenAI

FAKE_TOKEN = "fake-azure-provider-token"
ERROR_MESSAGE = "Expected `azure_ad_token_provider` argument to return a non-empty string."
PROVIDER_MODES = ["sync", "async-direct", "async-coroutine", "async-awaitable"]


class FakeAccessToken(NamedTuple):
    token: str
    expires_on: int


class UninspectableToken:
    def __bool__(self) -> NoReturn:
        raise TypeError(FAKE_TOKEN)

    @override
    def __str__(self) -> NoReturn:
        raise AssertionError(FAKE_TOKEN)

    @override
    def __repr__(self) -> NoReturn:
        raise AssertionError(FAKE_TOKEN)


class OrdinaryToken(str):
    pass


class ReformattedToken(str):
    @override
    def __format__(self, format_spec: str) -> str:
        return "fake-altered-token"


class UnformattableToken(str):
    @override
    def __format__(self, format_spec: str) -> NoReturn:
        raise TypeError(FAKE_TOKEN)


class UninspectableString(UnformattableToken):
    def __bool__(self) -> NoReturn:
        raise TypeError(FAKE_TOKEN)

    @override
    def __len__(self) -> NoReturn:
        raise TypeError(FAKE_TOKEN)

    @override
    def __str__(self) -> NoReturn:
        raise TypeError(FAKE_TOKEN)


class WebSocketConnectReached(Exception):
    pass


@pytest.fixture(autouse=True)
def offline_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("AZURE_OPENAI_API_KEY", "AZURE_OPENAI_AD_TOKEN", "OPENAI_API_KEY"):
        monkeypatch.delenv(name, raising=False)

    def unexpected_connection(*_args: Any, **_kwargs: Any) -> NoReturn:
        pytest.fail("Azure provider diagnostics must not open a network connection")

    monkeypatch.setattr("socket.socket.connect", unexpected_connection)
    monkeypatch.setattr("socket.socket.connect_ex", unexpected_connection)


def make_provider(mode: str, value: object) -> Callable[[], Any]:
    async def coroutine() -> object:
        return value

    def awaitable() -> asyncio.Future[object]:
        future: asyncio.Future[object] = asyncio.get_running_loop().create_future()
        future.set_result(value)
        return future

    if mode == "async-coroutine":
        return coroutine
    if mode == "async-awaitable":
        return awaitable
    return lambda: value


def make_client(mode: str, value: object, requests: list[httpx2.Request]) -> Any:
    def send(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return httpx2.Response(200, json={"data": []})

    transport = httpx2.MockTransport(send)
    http_client = httpx2.Client(transport=transport) if mode == "sync" else httpx2.AsyncClient(transport=transport)
    cls: Any = AzureOpenAI if mode == "sync" else AsyncAzureOpenAI
    return cls(
        azure_endpoint="https://azure.test",
        api_version="2024-02-01",
        azure_ad_token_provider=make_provider(mode, value),
        http_client=http_client,
        max_retries=0,
    )


async def resolve(value: Any) -> Any:
    return await value if inspect.isawaitable(value) else value


@pytest.mark.parametrize("mode", PROVIDER_MODES)
@pytest.mark.parametrize("entrypoint", ["http", "realtime-config", "realtime", "beta-realtime"])
@pytest.mark.parametrize(
    "value",
    [
        pytest.param({"access_token": FAKE_TOKEN}, id="dict"),
        pytest.param(FakeAccessToken(FAKE_TOKEN, 0), id="access-token"),
        pytest.param(UninspectableToken(), id="uninspectable-object"),
        pytest.param("", id="empty-string"),
        pytest.param(UninspectableString(""), id="empty-string-subclass"),
        pytest.param(None, id="none"),
    ],
)
async def test_invalid_provider_result_is_value_free(mode: str, entrypoint: str, value: object) -> None:
    requests: list[httpx2.Request] = []
    client = make_client(mode, value, requests)
    try:
        with pytest.raises(ValueError) as exc_info:
            if entrypoint == "http":
                await resolve(client.models.list())
            elif entrypoint == "realtime-config":
                await resolve(client._configure_realtime("test-model", {}))
            else:
                resource = client.realtime if entrypoint == "realtime" else client.beta.realtime
                await resolve(resource.connect(model="test-model").enter())

        error = exc_info.value
        assert str(error) == ERROR_MESSAGE
        assert FAKE_TOKEN not in repr(error)
        assert FAKE_TOKEN not in "".join(traceback.format_exception(type(error), error, error.__traceback__))
        assert error.__cause__ is None
        assert error.__context__ is None
        assert requests == []
    finally:
        await resolve(client.close())


@pytest.mark.parametrize("mode", PROVIDER_MODES)
@pytest.mark.parametrize(
    "value",
    [
        pytest.param(FAKE_TOKEN, id="string"),
        pytest.param(OrdinaryToken(FAKE_TOKEN), id="ordinary-subclass"),
        pytest.param(ReformattedToken(FAKE_TOKEN), id="reformatted-subclass"),
        pytest.param(UnformattableToken(FAKE_TOKEN), id="unformattable-subclass"),
        pytest.param(UninspectableString(FAKE_TOKEN), id="uninspectable-subclass"),
    ],
)
async def test_nonempty_provider_result_remains_usable(mode: str, value: str, monkeypatch: pytest.MonkeyPatch) -> None:
    websocket_headers: list[dict[str, str]] = []

    def connect(_url: str, **kwargs: Any) -> NoReturn:
        websocket_headers.append(kwargs["additional_headers"])
        raise WebSocketConnectReached

    monkeypatch.setattr("websockets.sync.client.connect", connect)
    monkeypatch.setattr("openai.lib._azure_websocket._AzureWebSocketConnect", connect)
    requests: list[httpx2.Request] = []
    client = make_client(mode, value, requests)
    try:
        await resolve(client.models.list())
        assert len(requests) == 1
        assert requests[0].headers["Authorization"] == f"Bearer {FAKE_TOKEN}"
        _, headers = await resolve(client._configure_realtime("test-model", {}))
        assert headers == {"Authorization": f"Bearer {FAKE_TOKEN}"}
        token = await resolve(client._get_azure_ad_token())
        assert type(token) is str
        assert token == FAKE_TOKEN
        for resource in (client.realtime, client.beta.realtime):
            with pytest.raises(WebSocketConnectReached):
                await resolve(resource.connect(model="test-model").enter())
        assert [headers["Authorization"] for headers in websocket_headers] == [f"Bearer {FAKE_TOKEN}"] * 2
    finally:
        await resolve(client.close())
