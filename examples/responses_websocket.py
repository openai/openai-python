#!/usr/bin/env python
"""Run with OPENAI_API_KEY configured and the openai[realtime] extra installed."""

from openai import OpenAI
from openai.lib.responses_websocket import ResponsesWebSocketLimits, ResponsesWebSocketSession


def main() -> None:
    # These are application budgets, not service limits. Increase them if your
    # responses contain large images or tool results.
    limits = ResponsesWebSocketLimits(
        max_lanes=8,
        max_events_per_lane=128,
        max_events=512,
        max_bytes_per_lane=16 * 1024 * 1024,
        max_bytes=32 * 1024 * 1024,
        max_response_bytes=None,  # Default: no cumulative response accumulation cap.
    )
    with (
        OpenAI() as client,
        client.responses.connect(websocket_connection_options={"max_size": None}) as connection,
        ResponsesWebSocketSession(connection, limits=limits) as session,
    ):
        lane = session.lane("example")
        lane.send({"type": "response.create", "model": "gpt-4o-mini", "input": "Say hello."})
        response = lane.get_final_response(timeout=60)
        print(response.id, response.status)
        lane.send(
            {
                "type": "response.create",
                "model": "gpt-4o-mini",
                "previous_response_id": response.id,
                "input": "Now say goodbye.",
            }
        )
        response = lane.get_final_response(timeout=60)
        print(response.id, response.status)
        lane.close()


if __name__ == "__main__":
    main()
