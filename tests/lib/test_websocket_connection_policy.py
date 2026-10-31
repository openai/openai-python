from __future__ import annotations

import asyncio
import logging
from typing import Any
from unittest.mock import Mock, AsyncMock

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from openai._types import omit
from openai._websocket_connection import (
    _exit_websocket,
    _connect_websocket,
    _async_exit_websocket,
    _websocket_entry_guard,
    _async_connect_websocket,
    _record_websocket_progress,
    _async_websocket_entry_guard,
)
from openai.resources.responses.responses import ResponsesConnection, AsyncResponsesConnection

LOG = logging.getLogger(__name__)


@pytest.mark.parametrize("is_async", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("key", [None, "additional_headers", "user_agent_header"])
@pytest.mark.asyncio
async def test_connect_keeps_prepared_policy_and_explicit_kwargs(
    client: OpenAI, async_client: AsyncOpenAI, monkeypatch: pytest.MonkeyPatch, is_async: bool, key: str | None
) -> None:
    connector = AsyncMock() if is_async else Mock()
    path = "openai.lib._websocket._WebSocketConnect" if is_async else "websockets.sync.client.connect"
    monkeypatch.setattr(path, connector)

    def prepare(options: Any) -> Any:
        options.headers = {**options.headers, "X-Prepared": "kept"}
        return options

    sdk = async_client if is_async else client
    monkeypatch.setattr(
        sdk, "_prepare_options", AsyncMock(side_effect=prepare) if is_async else Mock(side_effect=prepare)
    )
    options = {} if key is None else {key: "caller"}

    async def connect() -> None:
        args: Any = (
            lambda: httpx2.URL("https://example.test/v1/responses"),
            {},
            {"Authorization": omit},
            options,
            {},
            LOG,
        )
        if is_async:
            await _async_connect_websocket(async_client, *args)
        else:
            _connect_websocket(client, *args)

    if key is not None:
        with pytest.raises(TypeError, match="multiple values"):
            await connect()
        connector.assert_not_called()
        return
    await connect()
    connector.assert_called_once()
    assert connector.call_args.args == ("wss://example.test/v1/responses",)
    kwargs = connector.call_args.kwargs
    assert kwargs["additional_headers"]["X-Prepared"] == "kept"
    assert "authorization" not in {header.lower() for header in kwargs["additional_headers"]}
    assert kwargs["max_size"] is None and kwargs["compression"] is None
    assert options == {}


@pytest.mark.parametrize("is_async", [False, True], ids=["sync", "async"])
@pytest.mark.asyncio
async def test_iterator_keeps_dynamic_recv_and_generator_controls(
    monkeypatch: pytest.MonkeyPatch, is_async: bool
) -> None:
    connection = AsyncResponsesConnection(Mock()) if is_async else ResponsesConnection(Mock())
    monkeypatch.setattr(connection, "recv", AsyncMock(return_value="first") if is_async else Mock(return_value="first"))
    events: Any = connection._iter_events()
    assert (await anext(events) if is_async else next(events)) == "first"
    monkeypatch.setattr(
        connection, "recv", AsyncMock(return_value="second") if is_async else Mock(return_value="second")
    )
    assert (await anext(events) if is_async else next(events)) == "second"
    error = ValueError("caller")
    with pytest.raises(ValueError) as caught:
        if is_async:
            await events.athrow(error)
        else:
            events.throw(error)
    assert caught.value is error
    closing_events: Any = connection._iter_events()
    assert (await anext(closing_events) if is_async else next(closing_events)) == "second"
    if is_async:
        await closing_events.aclose()
        with pytest.raises(StopAsyncIteration):
            await anext(closing_events)
    else:
        closing_events.close()
        with pytest.raises(StopIteration):
            next(closing_events)


@pytest.mark.parametrize("is_async", [False, True], ids=["sync", "async"])
@pytest.mark.asyncio
async def test_entry_clears_before_cleanup_and_preserves_initiating_error(is_async: bool) -> None:
    slot = [object()]
    socket = Mock()

    def close() -> None:
        assert not slot
        raise RuntimeError("secondary cleanup")

    socket.close = AsyncMock(side_effect=close) if is_async else Mock(side_effect=close)
    error = asyncio.CancelledError("initial flush") if is_async else KeyboardInterrupt("initial flush")
    with pytest.raises(type(error)) as caught:
        if is_async:
            async with _async_websocket_entry_guard(socket, slot.clear):
                raise error
        else:
            with _websocket_entry_guard(socket, slot.clear):
                raise error
    assert caught.value is error
    socket.close.assert_called_once()


@pytest.mark.parametrize("is_async", [False, True], ids=["sync", "async"])
@pytest.mark.asyncio
async def test_exit_preserves_body_error_over_ordinary_close_error(is_async: bool) -> None:
    socket = Mock()
    socket.close = AsyncMock(side_effect=RuntimeError("close")) if is_async else Mock(side_effect=RuntimeError("close"))
    if is_async:
        await _async_exit_websocket(socket, ValueError("body"))
    else:
        _exit_websocket(socket, ValueError("body"))
    socket.close.assert_called_once()


@pytest.mark.parametrize(
    "event,raw,resets",
    [
        ({"type": "progress"}, False, True),
        ({"type": "error"}, False, False),
        (b'{"type":"progress"}', True, True),
        (b'{"type":"error"}', True, False),
        (b"invalid", True, False),
        (b"[1]", True, False),
    ],
)
def test_progress_requires_nonerror_event(event: Any, raw: bool, resets: bool) -> None:
    connection = ResponsesConnection(Mock())
    connection._reconnect_attempt = 3
    _record_websocket_progress(connection, event, raw=raw)
    assert connection._reconnect_attempt == (0 if resets else 3)
