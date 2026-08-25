from __future__ import annotations

from typing import Any

import pytest

from openai.resources.realtime.realtime import AsyncRealtimeConnection


def _connection_closed_error(code: int = 1011) -> Exception:
    from websockets.frames import Close
    from websockets.exceptions import ConnectionClosedError

    return ConnectionClosedError(Close(code=code, reason=""), None)


class _DeadConnection:
    """A connection whose send() always fails, simulating a dropped socket."""

    async def send(self, _data: bytes | str) -> None:
        raise _connection_closed_error()

    async def close(self, *, code: int = 1000, reason: str = "") -> None:
        pass


class _RecordingConnection:
    """The connection returned after a successful reconnect."""

    def __init__(self) -> None:
        self.sent: list[bytes | str] = []

    async def send(self, data: bytes | str) -> None:
        self.sent.append(data)


def _make_connection(new_conn: _RecordingConnection) -> AsyncRealtimeConnection:
    async def make_ws(_extra_query: Any, _extra_headers: Any) -> Any:
        return new_conn

    return AsyncRealtimeConnection(
        _DeadConnection(),  # type: ignore[arg-type]
        make_ws=make_ws,
        on_reconnecting=lambda _event: None,
        max_retries=1,
        initial_delay=0.0,
        max_delay=0.0,
    )


@pytest.mark.asyncio
async def test_reconnect_resends_binary_payload_unchanged() -> None:
    """End-to-end: a binary send_raw() that fails mid-send is queued and
    replayed byte-for-byte after reconnect, without UTF-8 corruption."""
    from websockets.exceptions import ConnectionClosedError

    new_conn = _RecordingConnection()
    conn = _make_connection(new_conn)

    binary = b"\xff\xfe\x00audio"  # not valid UTF-8 (would crash on decode)

    # send fails on the dead socket -> the original connection error must
    # surface (NOT a UnicodeDecodeError from decoding the binary payload),
    # and the payload must be queued for replay.
    with pytest.raises(ConnectionClosedError):
        await conn.send_raw(binary)

    # Drive the real reconnect path, which flushes the queue to the new socket.
    reconnected = await conn._reconnect(_connection_closed_error())
    assert reconnected is True

    assert new_conn.sent == [binary]
    assert isinstance(new_conn.sent[0], bytes)


@pytest.mark.asyncio
async def test_reconnect_resends_text_payload() -> None:
    """A str send_raw() is replayed as text after reconnect."""
    from websockets.exceptions import ConnectionClosedError

    new_conn = _RecordingConnection()
    conn = _make_connection(new_conn)

    with pytest.raises(ConnectionClosedError):
        await conn.send_raw('{"type": "input_audio_buffer.append"}')

    assert await conn._reconnect(_connection_closed_error()) is True
    assert new_conn.sent == ['{"type": "input_audio_buffer.append"}']
    assert isinstance(new_conn.sent[0], str)
