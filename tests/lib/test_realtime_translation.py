from __future__ import annotations

import json
import asyncio
from urllib.parse import parse_qs, urlsplit
from typing_extensions import override

import httpx2
import pytest
from pydantic import ValidationError
from websockets.exceptions import ConnectionClosedError
from websockets.sync.server import ServerConnection

from openai import OpenAI, AsyncOpenAI
from openai.types.realtime import (
    RealtimeErrorEvent,
    RealtimeTranslationClientEventParam,
    RealtimeTranslationSessionClosedEvent,
    RealtimeTranslationSessionCreatedEvent,
    RealtimeTranslationSessionUpdatedEvent,
    RealtimeTranslationOutputAudioDeltaEvent,
    RealtimeTranslationInputTranscriptDeltaEvent,
    RealtimeTranslationOutputTranscriptDeltaEvent,
)
from openai.lib.realtime_translation import TranslationSession, AsyncTranslationSession
from openai.types.websocket_reconnection import ReconnectingEvent, ReconnectingOverrides
from openai.types.websocket_connection_options import WebSocketConnectionOptions

from .responses.test_websocket_session import script_server


@pytest.fixture(autouse=True)
def loopback_proxy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NO_PROXY", "127.0.0.1")
    monkeypatch.setenv("no_proxy", "127.0.0.1")


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_translation_routing_all_typed_events_and_caller_close(mode: str) -> None:
    session = {
        "type": "translation",
        "id": "trans_test",
        "model": "gpt-realtime-translate",
        "expires_at": 2000000000,
        "audio": {"output": {"language": "fr"}},
    }
    frames = [
        (RealtimeTranslationSessionCreatedEvent, {"type": "session.created", "session": session}),
        (RealtimeTranslationSessionUpdatedEvent, {"type": "session.updated", "session": session}),
        (
            RealtimeTranslationInputTranscriptDeltaEvent,
            {"type": "session.input_transcript.delta", "delta": "こんにちは"},
        ),
        (
            RealtimeTranslationOutputTranscriptDeltaEvent,
            {"type": "session.output_transcript.delta", "delta": "Bonjour"},
        ),
        (RealtimeTranslationOutputAudioDeltaEvent, {"type": "session.output_audio.delta", "delta": "AA=="}),
        (
            RealtimeErrorEvent,
            {"type": "error", "error": {"type": "invalid_request_error", "message": "synthetic", "code": None}},
        ),
    ]
    sent: list[RealtimeTranslationClientEventParam] = [
        {"type": "session.update", "session": {"audio": {"output": {"language": "fr"}}}},
        {"type": "session.input_audio_buffer.append", "audio": "AA=="},
        {"type": "session.close"},
    ]

    def script(socket: ServerConnection) -> None:
        assert socket.request is not None
        url = urlsplit(socket.request.path)
        assert url.path == "/v1/customer/realtime/translations"
        assert parse_qs(url.query) == {"tenant": ["fixture"], "model": ["gpt-realtime-translate"], "routing": ["test"]}
        assert socket.request.headers.get_all("Authorization") == ["Bearer ek_fake_translation"]
        assert socket.request.headers["X-Translation-Test"] == "caller"
        assert socket.request.headers["X-Client-Only"] == "present"
        assert socket.request.headers.get("Sec-WebSocket-Extensions") is None
        assert json.loads(socket.recv(timeout=5)) == sent[0]
        assert json.loads(socket.recv(timeout=5)) == sent[1]
        for _, frame in frames:
            socket.send(json.dumps({"event_id": "fixture", "future_field": {"present": True}, **frame}))
        assert json.loads(socket.recv(timeout=5)) == sent[2]
        # An incomplete terminal envelope must not end the session or lose the final audio.
        socket.send('{"type":"session.closed"}')
        socket.send('{"type":"session.output_audio.delta","event_id":"final-audio","delta":"AQ=="}')
        socket.send('{"type":"session.closed","event_id":"done"}')

    client_headers = {"X-Translation-Test": "default", "X-Client-Only": "present"}
    with script_server(script) as url:
        base = f"{url}/customer?tenant=fixture"
        options: WebSocketConnectionOptions = {"compression": None}
        if mode == "sync":
            with OpenAI(
                api_key="ek_fake_translation",
                base_url=base,
                default_headers=client_headers,
                http_client=httpx2.Client(trust_env=False),
            ) as client:
                with TranslationSession(
                    client.realtime.translations,
                    model="gpt-realtime-translate",
                    extra_headers={"X-Translation-Test": "caller"},
                    extra_query={"routing": "test"},
                    websocket_connection_options=options,
                ) as conn:
                    conn.send(sent[0])
                    conn.send(sent[1])
                    for expected, frame in frames:
                        event = conn.recv()
                        assert type(event) is expected
                        assert event.to_dict(exclude_unset=True) == {
                            "event_id": "fixture",
                            "future_field": {"present": True},
                            **frame,
                        }
                    conn.send(sent[2])
                    with pytest.raises(ValidationError):
                        conn.recv()
                    assert conn.recv().event_id == "final-audio"
                    terminal = conn.recv()
                    assert isinstance(terminal, RealtimeTranslationSessionClosedEvent)
                    assert terminal.event_id == "done"
        else:
            async with AsyncOpenAI(
                api_key="ek_fake_translation",
                base_url=base,
                default_headers=client_headers,
                http_client=httpx2.AsyncClient(trust_env=False),
            ) as client:
                async with AsyncTranslationSession(
                    client.realtime.translations,
                    model="gpt-realtime-translate",
                    extra_headers={"X-Translation-Test": "caller"},
                    extra_query={"routing": "test"},
                    websocket_connection_options=options,
                ) as conn:
                    await conn.send(sent[0])
                    await conn.send(sent[1])
                    for expected, frame in frames:
                        event = await asyncio.wait_for(conn.recv(), 5)
                        assert type(event) is expected
                        assert event.to_dict(exclude_unset=True) == {
                            "event_id": "fixture",
                            "future_field": {"present": True},
                            **frame,
                        }
                    await conn.send(sent[2])
                    with pytest.raises(ValidationError):
                        await asyncio.wait_for(conn.recv(), 5)
                    assert (await asyncio.wait_for(conn.recv(), 5)).event_id == "final-audio"
                    terminal = await asyncio.wait_for(conn.recv(), 5)
                    assert isinstance(terminal, RealtimeTranslationSessionClosedEvent)
                    assert terminal.event_id == "done"


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("origin", ["base", "default", "connection", "websocket"])
async def test_intent_rejects_before_lazy_credentials(mode: str, origin: str) -> None:
    calls = 0

    def key() -> str:
        nonlocal calls
        calls += 1
        return "ek_fake_unreached"

    async def async_key() -> str:
        return key()

    extra = {"intent": "translation"} if origin == "connection" else {}
    base_url = "https://example.invalid/v1?intent=translation" if origin == "base" else "https://example.invalid/v1"
    default_query = {"intent": "translation"} if origin == "default" else {}
    websocket_base_url = "wss://example.invalid/v1?intent=translation" if origin == "websocket" else None
    if mode == "sync":
        with OpenAI(
            api_key=key,
            http_client=httpx2.Client(trust_env=False),
            base_url=base_url,
            default_query=default_query,
            websocket_base_url=websocket_base_url,
        ) as client:
            with pytest.raises(ValueError, match="intent"):
                with TranslationSession(
                    client.realtime.translations, model="gpt-realtime-translate", extra_query=extra
                ):
                    pytest.fail("unexpected connection")
    else:
        async with AsyncOpenAI(
            api_key=async_key,
            http_client=httpx2.AsyncClient(trust_env=False),
            base_url=base_url,
            default_query=default_query,
            websocket_base_url=websocket_base_url,
        ) as client:
            with pytest.raises(ValueError, match="intent"):
                async with AsyncTranslationSession(
                    client.realtime.translations, model="gpt-realtime-translate", extra_query=extra
                ):
                    pytest.fail("unexpected connection")
    assert calls == 0


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("provider", ["azure", "bedrock"])
async def test_unsupported_provider_never_fetches_credentials(mode: str, provider: str) -> None:
    from openai import AzureOpenAI, OpenAIError, AsyncAzureOpenAI
    from openai.providers import bedrock

    calls = 0

    def token() -> str:
        nonlocal calls
        calls += 1
        return "fake_forbidden_provider_token"

    if mode == "sync":
        if provider == "azure":
            client = AzureOpenAI(
                azure_endpoint="https://azure.example.invalid",
                api_version="fake-version",
                azure_ad_token_provider=token,
                http_client=httpx2.Client(trust_env=False),
            )
        else:
            client = OpenAI(
                provider=bedrock(base_url="https://bedrock.example.invalid/openai/v1", token_provider=token),
                http_client=httpx2.Client(trust_env=False),
            )
        with client:
            with pytest.raises(OpenAIError, match="not available through this provider"):
                with TranslationSession(client.realtime.translations, model="gpt-realtime-translate"):
                    pytest.fail("unexpected provider connection")
    else:
        if provider == "azure":
            async_client = AsyncAzureOpenAI(
                azure_endpoint="https://azure.example.invalid",
                api_version="fake-version",
                azure_ad_token_provider=token,
                http_client=httpx2.AsyncClient(trust_env=False),
            )
        else:
            async_client = AsyncOpenAI(
                provider=bedrock(base_url="https://bedrock.example.invalid/openai/v1", token_provider=token),
                http_client=httpx2.AsyncClient(trust_env=False),
            )
        async with async_client:
            with pytest.raises(OpenAIError, match="not available through this provider"):
                async with AsyncTranslationSession(async_client.realtime.translations, model="gpt-realtime-translate"):
                    pytest.fail("unexpected provider connection")
    assert calls == 0


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("entrypoint", ["session", "direct"])
async def test_translation_large_audio_has_no_new_default_limit(mode: str, entrypoint: str) -> None:
    audio = "a" * (5 << 20)

    def script(socket: ServerConnection) -> None:
        assert socket.request is not None
        assert parse_qs(urlsplit(socket.request.path).query)["model"] == ["gpt-realtime-translate"]
        socket.send(json.dumps({"type": "session.output_audio.delta", "event_id": "large", "delta": audio}))
        socket.send('{"type":"session.closed","event_id":"finished"}')

    with script_server(script) as url:
        if mode == "sync":
            with OpenAI(
                api_key="ek_fake_translation", base_url=url, http_client=httpx2.Client(trust_env=False)
            ) as client:
                manager = (
                    TranslationSession(client.realtime.translations, model="gpt-realtime-translate")
                    if entrypoint == "session"
                    else client.realtime.translations.connect(model="gpt-realtime-translate")
                )
                with manager as conn:
                    event = conn.recv()
                    assert isinstance(event, RealtimeTranslationOutputAudioDeltaEvent)
                    assert event.delta == audio
                    assert conn.recv().event_id == "finished"
        else:
            async with AsyncOpenAI(
                api_key="ek_fake_translation", base_url=url, http_client=httpx2.AsyncClient(trust_env=False)
            ) as client:
                async_manager = (
                    AsyncTranslationSession(client.realtime.translations, model="gpt-realtime-translate")
                    if entrypoint == "session"
                    else client.realtime.translations.connect(model="gpt-realtime-translate")
                )
                async with async_manager as conn:
                    event = await asyncio.wait_for(conn.recv(), 10)
                    assert isinstance(event, RealtimeTranslationOutputAudioDeltaEvent)
                    assert event.delta == audio
                    assert (await asyncio.wait_for(conn.recv(), 5)).event_id == "finished"


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_direct_translation_respects_explicit_receive_limit(mode: str) -> None:
    def script(socket: ServerConnection) -> None:
        socket.send(json.dumps({"type": "session.output_audio.delta", "event_id": "large", "delta": "a" * 2048}))
        with pytest.raises(ConnectionClosedError):
            socket.recv(timeout=5)

    with script_server(script) as url:
        if mode == "sync":
            with OpenAI(
                api_key="ek_fake_translation", base_url=url, http_client=httpx2.Client(trust_env=False)
            ) as client:
                with client.realtime.translations.connect(
                    model="gpt-realtime-translate", websocket_connection_options={"max_size": 1024}
                ) as conn:
                    with pytest.raises(ConnectionClosedError) as error:
                        conn.recv()
        else:
            async with AsyncOpenAI(
                api_key="ek_fake_translation", base_url=url, http_client=httpx2.AsyncClient(trust_env=False)
            ) as client:
                async with client.realtime.translations.connect(
                    model="gpt-realtime-translate", websocket_connection_options={"max_size": 1024}
                ) as conn:
                    with pytest.raises(ConnectionClosedError) as error:
                        await asyncio.wait_for(conn.recv(), 5)
        assert error.value.sent is not None
        assert error.value.sent.code == 1009


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_direct_translation_retains_model_when_reconnect_replaces_query(mode: str) -> None:
    routes: list[str] = []

    def script(socket: ServerConnection) -> None:
        assert socket.request is not None
        query = parse_qs(urlsplit(socket.request.path).query)
        assert query["model"] == ["gpt-realtime-translate"]
        routes.append(query["route"][0])
        if len(routes) == 1:
            socket.close(1011, "synthetic close")
        else:
            socket.send('{"type":"session.closed","event_id":"done"}')

    def on_retry(event: ReconnectingEvent) -> ReconnectingOverrides:
        assert event.attempt == 1
        return {"extra_query": {"route": "retry"}}

    with script_server(script, expected_connections=2) as url:
        if mode == "sync":
            with OpenAI(
                api_key="ek_fake_translation", base_url=url, http_client=httpx2.Client(trust_env=False)
            ) as client:
                with client.realtime.translations.connect(
                    model="gpt-realtime-translate",
                    extra_query={"route": "initial"},
                    on_reconnecting=on_retry,
                    max_retries=1,
                    initial_delay=0,
                ) as conn:
                    assert next(iter(conn)).event_id == "done"
        else:
            async with AsyncOpenAI(
                api_key="ek_fake_translation", base_url=url, http_client=httpx2.AsyncClient(trust_env=False)
            ) as async_client:
                async with async_client.realtime.translations.connect(
                    model="gpt-realtime-translate",
                    extra_query={"route": "initial"},
                    on_reconnecting=on_retry,
                    max_retries=1,
                    initial_delay=0,
                ) as async_conn:
                    assert (await asyncio.wait_for(async_conn.__aiter__().__anext__(), 5)).event_id == "done"
    assert routes == ["initial", "retry"]


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_selected_websocket_base_and_default_query_are_retained(mode: str) -> None:
    def script(socket: ServerConnection) -> None:
        assert socket.request is not None
        url = urlsplit(socket.request.path)
        assert url.path == "/v1/ws-gateway/realtime/translations"
        assert parse_qs(url.query) == {
            "http-only": ["baseline"],
            "default-only": ["tenant"],
            "gateway-only": ["regional"],
            "model": ["gpt-realtime-translate"],
            "priority": ["per-connection"],
        }
        socket.send('{"type":"session.closed","event_id":"done"}')

    with script_server(script) as url:
        selected = url.replace("http://", "ws://") + "/ws-gateway?gateway-only=regional&priority=gateway&model=old"
        base = "https://base.example.invalid/v1?http-only=baseline&priority=base"
        defaults = {"default-only": "tenant", "priority": "default", "model": "older"}
        if mode == "sync":
            with OpenAI(
                api_key="ek_fake_translation",
                base_url=base,
                websocket_base_url=selected,
                default_query=defaults,
                http_client=httpx2.Client(trust_env=False),
            ) as client:
                with TranslationSession(
                    client.realtime.translations,
                    model="gpt-realtime-translate",
                    extra_query={"priority": "per-connection"},
                ) as conn:
                    assert conn.recv().event_id == "done"
        else:
            async with AsyncOpenAI(
                api_key="ek_fake_translation",
                base_url=base,
                websocket_base_url=selected,
                default_query=defaults,
                http_client=httpx2.AsyncClient(trust_env=False),
            ) as client:
                async with AsyncTranslationSession(
                    client.realtime.translations,
                    model="gpt-realtime-translate",
                    extra_query={"priority": "per-connection"},
                ) as conn:
                    assert (await asyncio.wait_for(conn.recv(), 5)).event_id == "done"


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("body_fails", [True, False])
async def test_context_close_never_replaces_the_body_error(
    monkeypatch: pytest.MonkeyPatch, mode: str, body_fails: bool
) -> None:
    from openai.lib.realtime_translation import TranslationConnection, AsyncTranslationConnection

    def script(socket: ServerConnection) -> None:
        socket.send('{"type":"session.created","event_id":"ready"}')
        from websockets.exceptions import ConnectionClosed

        with pytest.raises(ConnectionClosed):
            socket.recv(timeout=5)

    if mode == "sync":
        original = TranslationConnection.close

        def sync_close(conn: TranslationConnection) -> None:
            original(conn)
            raise OSError("translation cleanup failed")

        monkeypatch.setattr(TranslationConnection, "close", sync_close)
    else:
        async_original = AsyncTranslationConnection.close

        async def async_close(conn: AsyncTranslationConnection) -> None:
            await async_original(conn)
            raise OSError("translation cleanup failed")

        monkeypatch.setattr(AsyncTranslationConnection, "close", async_close)

    expected = ValueError if body_fails else OSError
    message = "application failure" if body_fails else "translation cleanup failed"
    with script_server(script) as url:
        if mode == "sync":
            with OpenAI(
                api_key="ek_fake_translation", base_url=url, http_client=httpx2.Client(trust_env=False)
            ) as client:
                with pytest.raises(expected, match=message):
                    with TranslationSession(client.realtime.translations, model="gpt-realtime-translate") as conn:
                        assert conn.recv().event_id == "ready"
                        if body_fails:
                            raise ValueError("application failure")
        else:
            async with AsyncOpenAI(
                api_key="ek_fake_translation", base_url=url, http_client=httpx2.AsyncClient(trust_env=False)
            ) as client:
                with pytest.raises(expected, match=message):
                    async with AsyncTranslationSession(
                        client.realtime.translations, model="gpt-realtime-translate"
                    ) as conn:
                        assert (await asyncio.wait_for(conn.recv(), 5)).event_id == "ready"
                        if body_fails:
                            raise ValueError("application failure")


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_finish_once_rejects_late_input_while_draining(mode: str) -> None:
    from openai import OpenAIError

    def script(socket: ServerConnection) -> None:
        assert json.loads(socket.recv(timeout=5)) == {"type": "session.close"}
        with pytest.raises(TimeoutError):
            socket.recv(timeout=0.15)
        socket.send('{"type":"session.output_audio.delta","event_id":"final","delta":"AQ=="}')
        socket.send('{"type":"session.closed","event_id":"done"}')

    with script_server(script) as url:
        if mode == "sync":
            with OpenAI(
                api_key="ek_fake_translation", base_url=url, http_client=httpx2.Client(trust_env=False)
            ) as client:
                with TranslationSession(client.realtime.translations, model="gpt-realtime-translate") as conn:
                    conn.send({"type": "session.close"})
                    conn.send({"type": "session.close"})
                    with pytest.raises(OpenAIError, match="input is closed"):
                        conn.send({"type": "session.input_audio_buffer.append", "audio": "AA=="})
                    assert conn.recv().event_id == "final"
                    assert conn.recv().event_id == "done"
        else:
            async with AsyncOpenAI(
                api_key="ek_fake_translation", base_url=url, http_client=httpx2.AsyncClient(trust_env=False)
            ) as client:
                async with AsyncTranslationSession(
                    client.realtime.translations, model="gpt-realtime-translate"
                ) as conn:
                    await conn.send({"type": "session.close"})
                    await conn.send({"type": "session.close"})
                    with pytest.raises(OpenAIError, match="input is closed"):
                        await conn.send({"type": "session.input_audio_buffer.append", "audio": "AA=="})
                    assert (await asyncio.wait_for(conn.recv(), 5)).event_id == "final"
                    assert (await asyncio.wait_for(conn.recv(), 5)).event_id == "done"


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_early_eof_is_not_translation_completion(mode: str) -> None:
    from websockets.exceptions import ConnectionClosed

    def script(socket: ServerConnection) -> None:
        assert json.loads(socket.recv(timeout=5)) == {"type": "session.close"}
        socket.send('{"type":"session.output_audio.delta","event_id":"partial","delta":"AQ=="}')
        socket.close()

    with script_server(script) as url:
        if mode == "sync":
            with OpenAI(
                api_key="ek_fake_translation", base_url=url, http_client=httpx2.Client(trust_env=False)
            ) as client:
                with TranslationSession(client.realtime.translations, model="gpt-realtime-translate") as conn:
                    conn.send({"type": "session.close"})
                    assert conn.recv().event_id == "partial"
                    with pytest.raises(ConnectionClosed):
                        conn.recv()
        else:
            async with AsyncOpenAI(
                api_key="ek_fake_translation", base_url=url, http_client=httpx2.AsyncClient(trust_env=False)
            ) as client:
                async with AsyncTranslationSession(
                    client.realtime.translations, model="gpt-realtime-translate"
                ) as conn:
                    await conn.send({"type": "session.close"})
                    assert (await asyncio.wait_for(conn.recv(), 5)).event_id == "partial"
                    with pytest.raises(ConnectionClosed):
                        await asyncio.wait_for(conn.recv(), 5)


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_missing_terminal_times_out_and_cleans_up(mode: str) -> None:
    from websockets.exceptions import ConnectionClosed

    def script(socket: ServerConnection) -> None:
        assert json.loads(socket.recv(timeout=5)) == {"type": "session.close"}
        with pytest.raises(ConnectionClosed):
            socket.recv(timeout=5)

    with script_server(script) as url:
        if mode == "sync":
            with OpenAI(
                api_key="ek_fake_translation", base_url=url, http_client=httpx2.Client(trust_env=False)
            ) as client:
                with pytest.raises(TimeoutError):
                    with TranslationSession(client.realtime.translations, model="gpt-realtime-translate") as conn:
                        conn.send({"type": "session.close"})
                        conn.recv(timeout=0.1)
        else:
            async with AsyncOpenAI(
                api_key="ek_fake_translation", base_url=url, http_client=httpx2.AsyncClient(trust_env=False)
            ) as client:
                with pytest.raises(asyncio.TimeoutError):
                    async with AsyncTranslationSession(
                        client.realtime.translations, model="gpt-realtime-translate"
                    ) as conn:
                        await conn.send({"type": "session.close"})
                        await asyncio.wait_for(conn.recv(), 0.1)


async def test_cancel_translation_drain_closes_original_connection() -> None:
    from websockets.exceptions import ConnectionClosed

    accepted_finish = asyncio.Event()
    loop = asyncio.get_running_loop()

    def script(socket: ServerConnection) -> None:
        assert json.loads(socket.recv(timeout=5)) == {"type": "session.close"}
        loop.call_soon_threadsafe(accepted_finish.set)
        with pytest.raises(ConnectionClosed):
            socket.recv(timeout=5)

    with script_server(script) as url:
        async with AsyncOpenAI(
            api_key="ek_fake_translation", base_url=url, http_client=httpx2.AsyncClient(trust_env=False)
        ) as client:

            async def task() -> None:
                async with AsyncTranslationSession(
                    client.realtime.translations, model="gpt-realtime-translate"
                ) as conn:
                    await conn.send({"type": "session.close"})
                    await conn.recv()

            receiver = asyncio.create_task(task())
            await asyncio.wait_for(accepted_finish.wait(), 5)
            receiver.cancel()
            with pytest.raises(asyncio.CancelledError):
                await receiver


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_translation_prepares_each_attempt_and_refreshes_credentials(mode: str) -> None:
    from openai._utils import is_given
    from openai._models import FinalRequestOptions

    tokens: list[str] = []
    received: list[str] = []
    prepared: list[str] = []

    def credential() -> str:
        token = f"synthetic-translation-{len(tokens) + 1}"
        tokens.append(token)
        return token

    async def async_credential() -> str:
        return credential()

    def prepare(options: FinalRequestOptions) -> FinalRequestOptions:
        assert options.security == {"bearer_auth": True}
        prepared.append(options.url)
        options.headers = {"X-Request-Hook": "called", **(options.headers if is_given(options.headers) else {})}
        return options

    class HookedClient(OpenAI):
        @override
        def _prepare_options(self, options: FinalRequestOptions) -> FinalRequestOptions:
            return prepare(super()._prepare_options(options))

    class AsyncHookedClient(AsyncOpenAI):
        @override
        async def _prepare_options(self, options: FinalRequestOptions) -> FinalRequestOptions:
            return prepare(await super()._prepare_options(options))

    def script(socket: ServerConnection) -> None:
        assert socket.request is not None
        received.append(socket.request.headers["Authorization"])
        assert socket.request.headers["X-Request-Hook"] == "called"
        socket.send('{"type":"session.closed","event_id":"done"}')

    with script_server(script, expected_connections=3) as url:
        if mode == "sync":
            with HookedClient(api_key=credential, base_url=url, http_client=httpx2.Client(trust_env=False)) as client:
                for attempt in range(3):
                    headers = {"authorization": "Bearer synthetic-explicit"} if attempt == 2 else {}
                    with TranslationSession(
                        client.realtime.translations, model="test-model", extra_headers=headers
                    ) as conn:
                        assert conn.recv().type == "session.closed"
        else:
            async with AsyncHookedClient(
                api_key=async_credential, base_url=url, http_client=httpx2.AsyncClient(trust_env=False)
            ) as client:
                for attempt in range(3):
                    headers = {"authorization": "Bearer synthetic-explicit"} if attempt == 2 else {}
                    async with AsyncTranslationSession(
                        client.realtime.translations, model="test-model", extra_headers=headers
                    ) as conn:
                        assert (await conn.recv()).type == "session.closed"
    assert received == ["Bearer synthetic-translation-1", "Bearer synthetic-translation-2", "Bearer synthetic-explicit"]
    assert len(prepared) == 3


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_translation_cross_origin_redirect_keeps_credentials_on_source(mode: str) -> None:
    import threading
    from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

    from websockets.exceptions import InvalidHandshake

    source_headers: list[str | None] = []
    target_headers: list[str | None] = []

    class Target(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def do_GET(self) -> None:
            target_headers.append(self.headers.get("Authorization"))
            self.send_response(400)
            self.send_header("Content-Length", "0")
            self.send_header("Connection", "close")
            self.end_headers()

        @override
        def log_message(self, format: str, *args: object) -> None:
            pass

    target = ThreadingHTTPServer(("127.0.0.1", 0), Target)

    class Source(Target):
        @override
        def do_GET(self) -> None:
            source_headers.append(self.headers.get("Authorization"))
            self.send_response(302)
            self.send_header("Location", f"ws://127.0.0.1:{target.server_port}/target")
            self.send_header("Content-Length", "0")
            self.send_header("Connection", "close")
            self.end_headers()

    source = ThreadingHTTPServer(("127.0.0.1", 0), Source)
    threads = [threading.Thread(target=server.serve_forever) for server in (source, target)]
    for thread in threads:
        thread.start()
    try:
        url = f"http://127.0.0.1:{source.server_port}/v1"
        with pytest.raises(InvalidHandshake):
            if mode == "sync":
                with OpenAI(
                    api_key="synthetic-translation-secret", base_url=url, http_client=httpx2.Client(trust_env=False)
                ) as client:
                    with TranslationSession(client.realtime.translations, model="test-model"):
                        pytest.fail("Cross-origin redirect connected")
            else:
                async with AsyncOpenAI(
                    api_key="synthetic-translation-secret",
                    base_url=url,
                    http_client=httpx2.AsyncClient(trust_env=False),
                ) as client:
                    async with AsyncTranslationSession(client.realtime.translations, model="test-model"):
                        pytest.fail("Cross-origin redirect connected")
    finally:
        for server in (source, target):
            server.shutdown()
            server.server_close()
        for thread in threads:
            thread.join(timeout=5)
            assert not thread.is_alive()
    assert source_headers == ["Bearer synthetic-translation-secret"]
    assert target_headers == []


@pytest.mark.parametrize("mode", ["sync", "async"])
async def test_translation_session_enters_only_once(mode: str) -> None:
    import threading

    from websockets.exceptions import ConnectionClosedOK

    connected = threading.Event()

    def script(socket: ServerConnection) -> None:
        connected.set()
        with pytest.raises(ConnectionClosedOK):
            socket.recv(timeout=5)

    with script_server(script, expected_connections=1) as url:
        if mode == "sync":
            with OpenAI(api_key="synthetic", base_url=url, http_client=httpx2.Client(trust_env=False)) as client:
                session = TranslationSession(client.realtime.translations, model="test")
                with session:
                    assert connected.wait(5)
                    with pytest.raises(RuntimeError, match="only be entered once"):
                        session.enter()
        else:
            async with AsyncOpenAI(
                api_key="synthetic", base_url=url, http_client=httpx2.AsyncClient(trust_env=False)
            ) as client:
                session = AsyncTranslationSession(client.realtime.translations, model="test")
                try:
                    results = await asyncio.wait_for(
                        asyncio.gather(session.enter(), session.enter(), return_exceptions=True), 5
                    )
                    assert sum(isinstance(result, RuntimeError) for result in results) == 1
                    assert sum(not isinstance(result, BaseException) for result in results) == 1
                    assert await asyncio.to_thread(connected.wait, 5)
                finally:
                    await session.__aexit__(None, None, None)
