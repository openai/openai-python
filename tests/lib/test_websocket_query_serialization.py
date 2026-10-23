from __future__ import annotations

import asyncio
from typing import Any, Literal
from threading import Event, Thread
from urllib.parse import parse_qs, urlsplit

import httpx2
import pytest
from websockets.exceptions import ConnectionClosed
from websockets.sync.server import ServerConnection, serve

from openai import OpenAI, AsyncOpenAI, AzureOpenAI, AsyncAzureOpenAI, omit
from openai._types import Query
from openai.lib.realtime_translation import TranslationSession, AsyncTranslationSession
from tests.lib.test_realtime_translation import script_server
from tests.lib.test_websocket_entry_cleanup import PRODUCTS


def connect(client: Any, product: str, query: Query) -> Any:
    if product == "realtime":
        return client.realtime.connect(model="test", extra_query=query)
    if product == "transcription":
        return client.realtime.connect(extra_query={"intent": "transcription", **query})
    if product == "sideband":
        return client.realtime.connect(call_id="call_1", extra_query=query)
    if product == "responses":
        return client.responses.connect(extra_query=query)
    if product == "beta.responses":
        return client.beta.responses.connect(extra_query=query)
    if product == "live":
        return client.live.connect(extra_query=query)
    if product == "live-sideband":
        return client.live.sideband.connect(session_id="live_1", extra_query=query)
    if product == "live-forks":
        return client.live.forks.connect(session_id="live_1", extra_query=query)
    if product == "translation":
        return client.realtime.translations.connect("test", extra_query=query)
    assert product == "beta-realtime"
    return client.beta.realtime.connect(model="test", extra_query=query)


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize(
    ("provider", "product"),
    [("openai", product) for product in (*PRODUCTS, "beta-realtime")]
    + [("azure", product) for product in ("realtime", "beta-realtime")],
)
@pytest.mark.parametrize(
    ("query", "expected"),
    [
        pytest.param(
            {"route": "connection", "filter": "plain"},
            {"route": ["connection"], "filter": ["plain"]},
            id="primitive",
        ),
        pytest.param(
            {"route": omit, "filter": omit, "repeat": omit},
            {},
            id="omit",
        ),
        pytest.param(
            {"route": None, "filter": {"language": "fr", "empty": None}, "repeat": ["new", None, "last"]},
            {"route": [""], "filter[language]": ["fr"], "repeat": ["new", "", "last"]},
            id="structured",
        ),
    ],
)
def test_websocket_query_tiers(
    mode: Literal["sync", "async"],
    provider: Literal["openai", "azure"],
    product: str,
    query: Query,
    expected: dict[str, list[str]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("NO_PROXY", "*")
    monkeypatch.setenv("no_proxy", "*")
    wire = b'{"type":"future.event","value":"received"}'
    observations: list[dict[str, list[str]]] = []
    failures: list[Exception] = []
    done = Event()
    original = dict(query)

    def accept(socket: ServerConnection) -> None:
        try:
            assert socket.request is not None
            observations.append(parse_qs(urlsplit(socket.request.path).query, keep_blank_values=True))
            socket.send(wire)
            try:
                socket.recv(timeout=5)
            except ConnectionClosed:
                # The client has received the event and is closing normally.
                pass
        except Exception as exc:
            failures.append(exc)
        finally:
            done.set()

    with serve(accept, "127.0.0.1", 0, close_timeout=1) as server:
        thread = Thread(target=server.serve_forever)
        thread.start()
        try:
            address = server.socket.getsockname()[1]
            common: dict[str, Any] = {
                "api_key": "fake",
                "websocket_base_url": (
                    f"ws://127.0.0.1:{address}/v1?route=url&repeat=first&repeat=second&keep=one&keep=two"
                ),
                "default_query": {
                    "route": "default",
                    "filter": {"old": "discarded"},
                    "global": "kept",
                    "default_list": ["alpha", "beta"],
                    "default_absent": None,
                },
            }
            if provider == "azure":
                common.update(azure_endpoint="https://example.invalid/", api_version="test-version")
                # Azure's required fields win even if omitted by this request.
                actual_query: Query = {**query, "api-version": omit, "deployment": "wrong"}
            else:
                actual_query = query
            if mode == "sync":
                cls = OpenAI if provider == "openai" else AzureOpenAI
                with cls(**common) as client:
                    with connect(client, product, actual_query) as connection:
                        assert connection.recv_bytes() == wire
            else:

                async def run() -> None:
                    cls = AsyncOpenAI if provider == "openai" else AsyncAzureOpenAI
                    async with cls(**common) as client:
                        async with connect(client, product, actual_query) as connection:
                            assert await connection.recv_bytes() == wire

                asyncio.run(run())
            assert done.wait(5), "WebSocket peer did not finish after the client closed"
            assert not failures, failures
        finally:
            server.shutdown()
            thread.join(5)
            assert not thread.is_alive()
    assert len(observations) == 1
    actual = observations[0]
    endpoint: dict[str, list[str]] = {}
    if provider == "azure":
        endpoint = {"api-version": ["test-version"], "deployment": ["test"]}
    elif product in {"realtime", "beta-realtime", "translation"}:
        endpoint = {"model": ["test"]}
    elif product == "sideband":
        endpoint = {"call_id": ["call_1"]}
    elif product == "transcription":
        endpoint = {"intent": ["transcription"]}
    repeat = {"repeat": ["first", "second"]} if "repeat" not in query else {}
    assert actual == {
        "global": ["kept"],
        "default_list[]": ["alpha", "beta"],
        "keep": ["one", "two"],
        **repeat,
        **endpoint,
        **expected,
    }
    assert dict(query) == original


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("managed", [True, False])
def test_translation_native_query_params_preserve_repeats_and_default_model(mode: str, managed: bool) -> None:
    observations: list[dict[str, list[str]]] = []

    def script(socket: ServerConnection) -> None:
        assert socket.request is not None
        observations.append(parse_qs(urlsplit(socket.request.path).query))
        socket.send('{"type":"session.closed","event_id":"done"}')

    with script_server(script) as url:
        query = httpx2.QueryParams("route=x&route=y")
        if mode == "sync":
            with OpenAI(
                api_key="fake",
                base_url=url,
                default_query={"inherited": "tenant"},
                http_client=httpx2.Client(trust_env=False),
            ) as client:
                if managed:
                    with TranslationSession(client.realtime.translations, model="fixture", extra_query=query) as conn:
                        assert conn.recv().event_id == "done"
                else:
                    with client.realtime.translations.connect("fixture", extra_query=query) as raw:
                        assert raw.recv().event_id == "done"
        else:

            async def run() -> None:
                async with AsyncOpenAI(
                    api_key="fake",
                    base_url=url,
                    default_query={"inherited": "tenant"},
                    http_client=httpx2.AsyncClient(trust_env=False),
                ) as client:
                    if managed:
                        async with AsyncTranslationSession(
                            client.realtime.translations, model="fixture", extra_query=query
                        ) as conn:
                            assert (await asyncio.wait_for(conn.recv(), 5)).event_id == "done"
                    else:
                        async with client.realtime.translations.connect("fixture", extra_query=query) as raw:
                            assert (await asyncio.wait_for(raw.recv(), 5)).event_id == "done"

            asyncio.run(run())
    assert observations == [{"route": ["x", "y"], "model": ["fixture"], "inherited": ["tenant"]}]
    assert query.multi_items() == [("route", "x"), ("route", "y")]


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize(
    ("query", "expected"),
    [
        pytest.param(
            {"language": "fr"},
            {"filter[old]": ["discardable"], "route": ["x", "y"], "language": ["fr"]},
            id="untouched",
        ),
        pytest.param({"route": omit, "filter": omit}, {}, id="omit"),
        pytest.param(
            {"route": None, "filter": {"new": "value", "empty": None}, "list": ("one", None, "two")},
            {"route": [""], "filter[new]": ["value"], "list": ["one", "", "two"]},
            id="structured",
        ),
    ],
)
def test_managed_translation_composes_logical_query_without_losing_url_values(
    mode: str, query: Query, expected: dict[str, list[str]]
) -> None:
    observations: list[dict[str, list[str]]] = []

    def script(socket: ServerConnection) -> None:
        assert socket.request is not None
        observations.append(parse_qs(urlsplit(socket.request.path).query, keep_blank_values=True))
        socket.send('{"type":"session.closed","event_id":"done"}')

    original = dict(query)
    with script_server(script) as url:
        options: dict[str, Any] = {
            "api_key": "fake",
            "base_url": "https://base.example.invalid/v1?from_http=a&from_http=b&priority=http",
            "websocket_base_url": url.replace("http://", "ws://") + "?route=x&route=y&priority=gateway",
            "default_query": {"filter": {"old": "discardable"}, "priority": "default"},
        }
        if mode == "sync":
            with OpenAI(**options) as client:
                with TranslationSession(client.realtime.translations, model="fixture", extra_query=query) as conn:
                    assert conn.recv().event_id == "done"
        else:

            async def run() -> None:
                async with AsyncOpenAI(**options) as client:
                    async with AsyncTranslationSession(
                        client.realtime.translations, model="fixture", extra_query=query
                    ) as conn:
                        assert (await asyncio.wait_for(conn.recv(), 5)).event_id == "done"

            asyncio.run(run())
    assert observations == [{"from_http": ["a", "b"], "priority": ["gateway"], "model": ["fixture"], **expected}]
    assert dict(query) == original
