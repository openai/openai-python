from __future__ import annotations

import json

from openai import OpenAI, AsyncOpenAI
from openai._types import Omit


def test_pre_connect_send_strips_omit(client: OpenAI) -> None:
    manager = client.realtime.connect()
    manager.send({"type": "response.cancel", "event_id": Omit()})

    queued = manager._RealtimeConnectionManager__send_queue.drain()
    assert len(queued) == 1
    assert json.loads(queued[0]) == {"type": "response.cancel"}


async def test_pre_connect_send_strips_omit_async(async_client: AsyncOpenAI) -> None:
    manager = async_client.realtime.connect()
    manager.send({"type": "response.cancel", "event_id": Omit()})

    queued = manager._AsyncRealtimeConnectionManager__send_queue.drain()
    assert len(queued) == 1
    assert json.loads(queued[0]) == {"type": "response.cancel"}
