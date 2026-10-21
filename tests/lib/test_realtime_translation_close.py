from __future__ import annotations

import time
import threading
from typing_extensions import override

import httpx2
import pytest
from websockets.exceptions import ConnectionClosed
from websockets.sync.server import ServerConnection, serve

from openai import OpenAI, OpenAIError
from openai.lib.realtime_translation import TranslationSession
from openai.resources.realtime.translations.translations import TranslationsConnection

from .responses.test_websocket_session import script_server


@pytest.mark.parametrize(
    "terminal,delay,timeout",
    [
        pytest.param(True, 0.35, 0.075, id="timed-terminal-delayed-close"),
        pytest.param(True, 0.0, 0.075, id="timed-terminal-normal-close"),
        pytest.param(False, 0.35, 0.075, id="timed-output-delayed-close"),
        pytest.param(True, 0.35, None, id="untimed-terminal-delayed-close"),
    ],
)
def test_managed_translation_receive_close_deadline(
    terminal: bool, delay: float, timeout: float | None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("NO_PROXY", "127.0.0.1")
    monkeypatch.setenv("no_proxy", "127.0.0.1")
    sent = threading.Event()
    replied = threading.Event()
    finished = threading.Event()
    received: list[str | bytes] = []
    errors: list[Exception] = []
    event = (
        '{"type":"session.closed","event_id":"done"}'
        if terminal
        else '{"type":"session.output_audio.delta","event_id":"audio","delta":"AA=="}'
    )

    class ReplyConnection(ServerConnection):
        @override
        def send_data(self) -> None:
            if self.protocol.close_rcvd is not None and not replied.is_set():
                replied.set()
                time.sleep(delay)
            super().send_data()

    def handler(ws: ServerConnection) -> None:
        try:
            ws.send(event)
            sent.set()
            try:
                while True:
                    received.append(ws.recv(timeout=5))
            except ConnectionClosed:
                # The managed connection owns and closes this socket.
                pass
        except Exception as exc:
            errors.append(exc)
        finally:
            finished.set()

    with serve(handler, "127.0.0.1", 0, create_connection=ReplyConnection) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            url = f"http://127.0.0.1:{server.socket.getsockname()[1]}/v1"
            with OpenAI(api_key="local-test-key", base_url=url, http_client=httpx2.Client(trust_env=False)) as client:
                with TranslationSession(client.realtime.translations, model="gpt-realtime-translate") as connection:
                    assert sent.wait(5), "fixture did not send its event"
                    start = time.monotonic()
                    result = connection.recv(timeout=timeout)
                    elapsed = time.monotonic() - start
                    assert result.type == ("session.closed" if terminal else "session.output_audio.delta")
                    if timeout is not None:
                        assert elapsed < timeout * 2, f"receive took {elapsed:.3f}s for a {timeout:.3f}s wait"
                    elif terminal and delay:
                        assert elapsed >= delay * 0.8, "untimed receive must still complete cleanup synchronously"
                    if terminal:
                        with pytest.raises(OpenAIError, match="input is closed"):
                            connection.send({"type": "session.input_audio_buffer.append", "audio": "AA=="})
                assert finished.wait(5), "context exit did not finish native close"
        finally:
            server.shutdown()
            thread.join(timeout=5)
            assert not thread.is_alive()
    assert not errors, errors
    assert received == []


def test_concurrent_explicit_closes_wait_for_one_timed_terminal_close(monkeypatch: pytest.MonkeyPatch) -> None:
    entered = threading.Event()
    release = threading.Event()
    completed = [threading.Event(), threading.Event()]
    failures: list[BaseException] = []
    calls = 0
    original_close = TranslationsConnection.close

    def blocking_close(raw: TranslationsConnection, *, code: int = 1000, reason: str = "") -> None:
        nonlocal calls
        calls += 1
        entered.set()
        assert release.wait(5), "test did not release native close"
        original_close(raw, code=code, reason=reason)

    def handler(ws: ServerConnection) -> None:
        ws.send('{"type":"session.closed","event_id":"done"}')
        with pytest.raises(ConnectionClosed):
            ws.recv(timeout=5)

    with (
        script_server(handler) as url,
        OpenAI(api_key="local-test-key", base_url=url, http_client=httpx2.Client(trust_env=False)) as client,
    ):
        with TranslationSession(client.realtime.translations, model="gpt-realtime-translate") as connection:
            monkeypatch.setattr(TranslationsConnection, "close", blocking_close)
            threads: list[threading.Thread] = []
            try:
                assert connection.recv(timeout=0.25).type == "session.closed"
                assert entered.wait(5), "owned close did not start"
                with pytest.raises(OpenAIError, match="input is closed"):
                    connection.send({"type": "session.input_audio_buffer.append", "audio": "AA=="})

                def close(index: int) -> None:
                    try:
                        connection.close()
                    except Exception as exc:
                        failures.append(exc)
                    finally:
                        completed[index].set()

                for index in range(2):
                    thread = threading.Thread(target=close, args=(index,))
                    threads.append(thread)
                    thread.start()
                assert not completed[0].wait(0.05), "first explicit close didn't wait"
                assert not completed[1].wait(0.05), "second explicit close didn't wait"
            finally:
                release.set()
                for thread in threads:
                    thread.join(timeout=5)
                    assert not thread.is_alive()
        assert all(done.is_set() for done in completed)
        assert failures == []
        assert calls == 1, "timed, concurrent and context closes must share one native close"


@pytest.mark.parametrize("body_failure", [False, True], ids=["close-error", "block-error"])
def test_timed_terminal_close_error_reaches_context_exit(monkeypatch: pytest.MonkeyPatch, body_failure: bool) -> None:
    original_close = TranslationsConnection.close
    closing = RuntimeError("fixture close failure")
    body = ValueError("fixture block failure")
    calls = 0

    def fail_close(raw: TranslationsConnection, *, code: int = 1000, reason: str = "") -> None:
        nonlocal calls
        calls += 1
        original_close(raw, code=code, reason=reason)
        raise closing

    def handler(ws: ServerConnection) -> None:
        ws.send('{"type":"session.closed","event_id":"done"}')
        with pytest.raises(ConnectionClosed):
            ws.recv(timeout=5)

    with (
        script_server(handler) as url,
        OpenAI(api_key="local-test-key", base_url=url, http_client=httpx2.Client(trust_env=False)) as client,
    ):
        expected = body if body_failure else closing
        with pytest.raises(type(expected)) as caught:
            with TranslationSession(client.realtime.translations, model="gpt-realtime-translate") as connection:
                monkeypatch.setattr(TranslationsConnection, "close", fail_close)
                assert connection.recv(timeout=0.25).type == "session.closed"
                if body_failure:
                    raise body
        if body_failure:
            assert caught.value is body
            assert caught.value.__cause__ is closing
        else:
            assert caught.value is closing
        assert calls == 1


@pytest.mark.parametrize("timeout", [0.25, None], ids=["timed-worker", "untimed-owner"])
def test_interrupted_native_close_reaches_translation_owner(
    monkeypatch: pytest.MonkeyPatch, timeout: float | None
) -> None:
    original_close = TranslationsConnection.close
    closing = KeyboardInterrupt("fixture close interrupted")
    caught: list[KeyboardInterrupt] = []
    calls = 0

    def fail_close(raw: TranslationsConnection, *, code: int = 1000, reason: str = "") -> None:
        nonlocal calls
        calls += 1
        original_close(raw, code=code, reason=reason)
        raise closing

    def handler(ws: ServerConnection) -> None:
        ws.send('{"type":"session.closed","event_id":"done"}')
        with pytest.raises(ConnectionClosed):
            ws.recv(timeout=5)

    with (
        script_server(handler) as url,
        OpenAI(api_key="local-test-key", base_url=url, http_client=httpx2.Client(trust_env=False)) as client,
    ):
        monkeypatch.setattr(TranslationsConnection, "close", fail_close)

        def receive_and_close() -> None:
            try:
                with TranslationSession(client.realtime.translations, model="gpt-realtime-translate") as connection:
                    assert connection.recv(timeout=timeout).type == "session.closed"
            except KeyboardInterrupt as exc:
                caught.append(exc)

        # Bound even a broken Future completion: a stranded owner must fail this
        # test without preventing the test process from shutting down.
        owner = threading.Thread(target=receive_and_close, daemon=True)
        owner.start()
        owner.join(timeout=5)
        assert not owner.is_alive(), "Translation owner stayed blocked after close was interrupted"
        assert caught == [closing]
        assert calls == 1


def test_failed_close_worker_start_still_closes_owned_translation(monkeypatch: pytest.MonkeyPatch) -> None:
    original_close = TranslationsConnection.close
    starting = RuntimeError("fixture worker could not start")
    server_ready = threading.Event()
    calls = 0

    def counted_close(raw: TranslationsConnection, *, code: int = 1000, reason: str = "") -> None:
        nonlocal calls
        calls += 1
        original_close(raw, code=code, reason=reason)

    def fail_start(_thread: threading.Thread) -> None:
        raise starting

    def handler(ws: ServerConnection) -> None:
        server_ready.set()
        ws.send('{"type":"session.closed","event_id":"done"}')
        with pytest.raises(ConnectionClosed):
            ws.recv(timeout=5)

    with (
        script_server(handler) as url,
        OpenAI(api_key="local-test-key", base_url=url, http_client=httpx2.Client(trust_env=False)) as client,
    ):
        with TranslationSession(client.realtime.translations, model="gpt-realtime-translate") as connection:
            # Only inject failure after server and client transport workers exist.
            assert server_ready.wait(5), "fixture server did not finish starting transport workers"
            with monkeypatch.context() as patch:
                patch.setattr(TranslationsConnection, "close", counted_close)
                patch.setattr(threading.Thread, "start", fail_start)
                with pytest.raises(RuntimeError) as caught:
                    connection.recv(timeout=0.25)
                assert caught.value is starting
                with pytest.raises(OpenAIError, match="input is closed"):
                    connection.send({"type": "session.input_audio_buffer.append", "audio": "AA=="})
                connection.close()
        assert calls == 1
