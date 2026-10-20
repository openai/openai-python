import asyncio
from typing import Literal, Iterator
from threading import Event, Thread

import pytest
from websockets.exceptions import ConnectionClosed
from websockets.sync.server import ServerConnection, serve

from openai import OpenAI, AsyncOpenAI, AzureOpenAI, AsyncAzureOpenAI, omit
from openai._types import Headers


@pytest.fixture
def header_peer(monkeypatch: pytest.MonkeyPatch) -> Iterator[tuple[str, list[dict[str, list[str]]]]]:
    for name in (
        "OPENAI_CUSTOM_HEADERS",
        "OPENAI_ORG_ID",
        "OPENAI_PROJECT_ID",
        "OPENAI_API_KEY",
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_AD_TOKEN",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("NO_PROXY", "*")
    monkeypatch.setenv("no_proxy", "*")
    observed: list[dict[str, list[str]]] = []
    finished: list[Event] = []
    failures: list[Exception] = []

    def accept(socket: ServerConnection) -> None:
        done = Event()
        finished.append(done)
        try:
            assert socket.request is not None
            observed.append(
                {
                    name: socket.request.headers.get_all(name)
                    for name in (
                        "authorization",
                        "openai-organization",
                        "openai-project",
                        "x-probe-route",
                        "openai-beta",
                        "user-agent",
                    )
                }
            )
            socket.send(b'{"type":"future.event","text":"ok"}')
            try:
                socket.recv(timeout=5)
            except ConnectionClosed:
                # Each client closes after receiving the small test event.
                pass
        except Exception as error:
            failures.append(error)
        finally:
            done.set()

    with serve(accept, "127.0.0.1", 0) as server:
        thread = Thread(target=server.serve_forever)
        thread.start()
        try:
            yield f"ws://127.0.0.1:{server.socket.getsockname()[1]}/v1", observed
        finally:
            server.shutdown()
            thread.join(5)
            assert not thread.is_alive()
            assert all(done.wait(5) for done in finished)
            assert not failures, failures


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("provider", ["openai", "azure"])
@pytest.mark.parametrize(
    "choice",
    [
        "provider",
        "client-authorization",
        "lowercase-extra",
        "lowercase-omit",
        "feature-default",
        "feature-override",
        "feature-omit",
    ],
)
async def test_beta_realtime_forwards_effective_client_and_connection_headers(
    header_peer: tuple[str, list[dict[str, list[str]]]],
    mode: Literal["sync", "async"],
    provider: Literal["openai", "azure"],
    choice: Literal[
        "provider",
        "client-authorization",
        "lowercase-extra",
        "lowercase-omit",
        "feature-default",
        "feature-override",
        "feature-omit",
    ],
) -> None:
    url, observed = header_peer
    issued: list[str] = []

    def token() -> str:
        result = f"fake-{provider}-{len(issued) + 1}"
        issued.append(result)
        return result

    async def async_token() -> str:
        await asyncio.sleep(0)
        return token()

    headers = {"x-probe-route": "fake-client-route", "User-Agent": "fake-client-agent"}
    extras: Headers = {}
    if choice == "client-authorization":
        headers["authorization"] = "Bearer fake-client-override"
    elif choice == "lowercase-extra":
        extras = {"authorization": "Bearer fake-connection-override"}
    elif choice == "lowercase-omit":
        extras = {"authorization": omit}
    elif choice in ("feature-default", "feature-override", "feature-omit"):
        headers["openai-beta"] = "assistants=v2"
        if choice == "feature-override":
            extras = {"OPENAI-BETA": "realtime=future"}
        elif choice == "feature-omit":
            extras = {"OPENAI-BETA": omit}
    original_headers = headers.copy()
    original_extras = dict(extras)

    if mode == "sync":

        def receive() -> None:
            if provider == "openai":
                client = OpenAI(api_key=token, websocket_base_url=url, default_headers=headers)
            else:
                client = AzureOpenAI(
                    azure_endpoint="https://azure.example.invalid",
                    api_version="2025-04-01-preview",
                    azure_ad_token_provider=token,
                    websocket_base_url=url,
                    default_headers=headers,
                )
            with client:
                manager = client.beta.realtime.connect(model="fake", extra_headers=extras)
                client.organization = "org-fake-current"
                client.project = "project-fake-current"
                with manager as conn:
                    assert conn.recv_bytes() == b'{"type":"future.event","text":"ok"}'

        await asyncio.wait_for(asyncio.to_thread(receive), 10)
    else:
        if provider == "openai":
            async_client = AsyncOpenAI(api_key=async_token, websocket_base_url=url, default_headers=headers)
        else:
            async_client = AsyncAzureOpenAI(
                azure_endpoint="https://azure.example.invalid",
                api_version="2025-04-01-preview",
                azure_ad_token_provider=async_token,
                websocket_base_url=url,
                default_headers=headers,
            )
        async with async_client:
            manager = async_client.beta.realtime.connect(model="fake", extra_headers=extras)
            async_client.organization = "org-fake-current"
            async_client.project = "project-fake-current"
            async with manager as conn:
                assert await asyncio.wait_for(conn.recv_bytes(), 10) == b'{"type":"future.event","text":"ok"}'

    assert len(issued) == 1
    expected_auth = {
        "client-authorization": ["Bearer fake-client-override"],
        "lowercase-extra": ["Bearer fake-connection-override"],
        "lowercase-omit": [],
    }.get(choice, [f"Bearer {issued[0]}"])
    expected_beta = {
        "feature-override": ["realtime=future"],
        "feature-omit": [],
    }.get(choice, ["realtime=v1"])
    assert observed == [
        {
            "authorization": expected_auth,
            "openai-organization": ["org-fake-current"],
            "openai-project": ["project-fake-current"],
            "x-probe-route": ["fake-client-route"],
            "openai-beta": expected_beta,
            "user-agent": ["fake-client-agent"],
        }
    ]
    assert headers == original_headers
    assert extras == original_extras
