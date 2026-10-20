import json
import asyncio
from typing import Literal, Iterator, Optional
from threading import Thread

import pytest
from websockets.exceptions import ConnectionClosed, ConnectionClosedError
from websockets.sync.server import ServerConnection, serve

from openai import OpenAI, AsyncOpenAI
from openai.types.websocket_connection_options import WebSocketConnectionOptions


@pytest.fixture(autouse=True)
def bypass_loopback_proxy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NO_PROXY", "*")
    monkeypatch.setenv("no_proxy", "*")


@pytest.fixture
def realtime_peer(payload_size: int) -> Iterator[tuple[str, bytes]]:
    wire = json.dumps({"type": "future.event", "text": "x" * payload_size}).encode()

    def accept(socket: ServerConnection) -> None:
        socket.send(wire)
        try:
            socket.recv()
        except ConnectionClosed:
            # The client closes after consuming or rejecting the test event.
            pass

    with serve(accept, "127.0.0.1", 0) as server:
        thread = Thread(target=server.serve_forever)
        thread.start()
        try:
            yield f"ws://127.0.0.1:{server.socket.getsockname()[1]}", wire
        finally:
            server.shutdown()
            thread.join(3)
            assert not thread.is_alive()


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize(
    ("payload_size", "max_size", "reject"),
    [
        pytest.param(128, "default", False, id="default-small"),
        pytest.param(2**20 + 32, "default", False, id="default-over-native"),
        pytest.param(2**20 + 32, None, False, id="explicit-unlimited"),
        pytest.param(128, 512, False, id="explicit-limit-under"),
        pytest.param(900, 512, True, id="explicit-limit-over"),
        pytest.param(1, 0, True, id="explicit-zero"),
    ],
)
async def test_beta_realtime_preserves_receive_limit_choice(
    realtime_peer: tuple[str, bytes], mode: Literal["sync", "async"], max_size: Optional[int | str], reject: bool
) -> None:
    url, expected = realtime_peer
    options: WebSocketConnectionOptions = {}
    if isinstance(max_size, int) or max_size is None:
        options["max_size"] = max_size

    if mode == "sync":

        def receive() -> bytes:
            with OpenAI(api_key="local", websocket_base_url=url) as client:
                with client.beta.realtime.connect(model="test", websocket_connection_options=options) as conn:
                    return conn.recv_bytes()

        if reject:
            with pytest.raises(ConnectionClosedError) as exc:
                await asyncio.wait_for(asyncio.to_thread(receive), 10)
            assert exc.value.sent is not None and exc.value.sent.code == 1009
        else:
            assert await asyncio.wait_for(asyncio.to_thread(receive), 10) == expected
    else:
        async with AsyncOpenAI(api_key="local", websocket_base_url=url) as client:
            async with client.beta.realtime.connect(model="test", websocket_connection_options=options) as conn:
                if reject:
                    with pytest.raises(ConnectionClosedError) as exc:
                        await asyncio.wait_for(conn.recv_bytes(), 10)
                    assert exc.value.sent is not None and exc.value.sent.code == 1009
                else:
                    assert await asyncio.wait_for(conn.recv_bytes(), 10) == expected
