from __future__ import annotations

from typing import Any, cast
from unittest.mock import Mock

import pytest

from openai._exceptions import WebSocketQueueFullError
from openai._send_queue import SendQueue
from openai.resources.realtime.realtime import RealtimeConnection, AsyncRealtimeConnection
from openai.resources.responses.responses import (
    ResponsesConnection,
    AsyncResponsesConnection,
)
from openai.resources.beta.responses.responses import (
    ResponsesConnection as BetaResponsesConnection,
    AsyncResponsesConnection as AsyncBetaResponsesConnection,
)


@pytest.mark.parametrize(
    "connection_type",
    [
        AsyncRealtimeConnection,
        RealtimeConnection,
        AsyncResponsesConnection,
        ResponsesConnection,
        AsyncBetaResponsesConnection,
        BetaResponsesConnection,
    ],
)
def test_connections_preserve_an_explicit_empty_send_queue(connection_type: Any) -> None:
    send_queue = SendQueue(max_bytes=0)
    connection = connection_type(cast(Any, Mock()), send_queue=send_queue)

    assert connection._send_queue is send_queue
    with pytest.raises(WebSocketQueueFullError):
        connection._send_queue.enqueue("message")
