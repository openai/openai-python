import json

from openai import OpenAI
from openai._types import omit


def test_preconnect_manager_send_strips_omit() -> None:
    client = OpenAI(api_key="sk-test", base_url="http://127.0.0.1:4010")
    manager = client.realtime.connect(model="gpt-4o-realtime-preview")
    manager.send({"type": "response.cancel", "event_id": omit})
    queued = manager._RealtimeConnectionManager__send_queue.drain()  # type: ignore[attr-defined]
    assert len(queued) == 1
    payload = json.loads(queued[0])
    assert payload == {"type": "response.cancel"}
    assert "event_id" not in payload
