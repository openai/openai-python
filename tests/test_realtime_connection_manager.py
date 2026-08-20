from __future__ import annotations

import json
from unittest import mock

from openai.resources.realtime.realtime import AsyncRealtimeConnectionManager, RealtimeConnectionManager
from openai._types import omit


def _manager_kwargs() -> dict[str, object]:
    return {
        "client": mock.Mock(),
        "extra_query": {},
        "extra_headers": {},
        "websocket_connection_options": {},
    }


def test_sync_manager_send_strips_omit_values() -> None:
    manager = RealtimeConnectionManager(**_manager_kwargs())

    manager.send({"type": "response.cancel", "event_id": omit})

    payload = json.loads(manager._RealtimeConnectionManager__send_queue.drain()[0])
    assert payload == {"type": "response.cancel"}


def test_async_manager_send_strips_omit_values() -> None:
    manager = AsyncRealtimeConnectionManager(**_manager_kwargs())

    manager.send({"type": "response.cancel", "event_id": omit})

    payload = json.loads(manager._AsyncRealtimeConnectionManager__send_queue.drain()[0])
    assert payload == {"type": "response.cancel"}
