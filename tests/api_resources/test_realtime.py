# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
import json

import pytest

from openai import OpenAI, AsyncOpenAI, omit

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRealtime:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_connection_manager_send_strips_omit_values(self, client: OpenAI) -> None:
        manager = client.realtime.connect(model="gpt-4o-realtime-preview")

        manager.send({"type": "response.cancel", "event_id": omit})

        queued = manager._RealtimeConnectionManager__send_queue.drain()
        assert len(queued) == 1
        assert json.loads(queued[0]) == {"type": "response.cancel"}


class TestAsyncRealtime:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_connection_manager_send_strips_omit_values(self, async_client: AsyncOpenAI) -> None:
        manager = async_client.realtime.connect(model="gpt-4o-realtime-preview")

        manager.send({"type": "response.cancel", "event_id": omit})

        queued = manager._AsyncRealtimeConnectionManager__send_queue.drain()
        assert len(queued) == 1
        assert json.loads(queued[0]) == {"type": "response.cancel"}
