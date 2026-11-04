from __future__ import annotations

import json
import asyncio
import threading
from typing import Any, Generator, TypedDict
from pathlib import Path
from contextlib import contextmanager
from typing_extensions import NotRequired

import httpx2
import pytest
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError
from websockets.sync.server import ServerConnection, serve

from openai import OpenAI, AsyncOpenAI
from openai.types.responses import responses_server_event as events


class Turn(TypedDict):
    request: dict[str, Any]
    frames: list[dict[str, Any] | str]


class Scenario(TypedDict):
    id: str
    turns: list[Turn]
    close_code: NotRequired[int]


SCENARIOS: list[Scenario] = json.loads((Path(__file__).parent / "fixtures" / "websocket_scenarios.json").read_text())[
    "scenarios"
]
EVENT_TYPES = {
    "response.created": events.ResponseWsCreated,
    "response.completed": events.ResponseWsCompleted,
    "response.failed": events.ResponseWsFailed,
    "response.incomplete": events.ResponseWsIncomplete,
    "response.output_text.delta": events.ResponseTextWsDelta,
    "error": events.ResponseWsError,
}


@pytest.fixture(autouse=True)
def bypass_loopback_proxy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NO_PROXY", "127.0.0.1")
    monkeypatch.setenv("no_proxy", "127.0.0.1")


@contextmanager
def scenario_server(scenario: Scenario) -> Generator[str, None, None]:
    """Exercise the SDK over a real socket; surface failures from the server thread."""
    failures: list[Exception] = []
    connections: list[ServerConnection] = []
    finished = threading.Event()

    def handle(connection: ServerConnection) -> None:
        connections.append(connection)
        try:
            assert connection.request is not None
            assert connection.request.path == "/v1/responses?contract=1"
            assert connection.request.headers["Authorization"] == "Bearer fake-contract-key"
            assert connection.request.headers["X-Contract-Test"] == "synthetic"
            for turn in scenario["turns"]:
                assert json.loads(connection.recv(timeout=5)) == turn["request"]
                for frame in turn["frames"]:
                    connection.send(frame if isinstance(frame, str) else json.dumps(frame))
            if "close_code" in scenario:
                connection.close(code=scenario["close_code"])
            else:
                # Terminal responses and API errors leave the connection open until
                # the caller closes it. No extra request or automatic replay is expected.
                try:
                    connection.recv(timeout=5)
                except ConnectionClosedOK:
                    pass
                else:
                    raise AssertionError("Unexpected request after the last turn")
        except Exception as exc:
            failures.append(exc)
        finally:
            connection.close()
            finished.set()

    with serve(handle, "127.0.0.1", 0, open_timeout=5, close_timeout=1) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            yield f"http://127.0.0.1:{server.socket.getsockname()[1]}/v1"
        finally:
            for connection in connections:
                connection.close()
            server.shutdown()
            thread.join(timeout=5)
            assert not thread.is_alive(), "WebSocket server did not stop"
            if connections:
                assert finished.wait(timeout=5), "WebSocket handler did not stop"
        assert len(connections) == 1, "Expected one connection with no reconnects"
        assert not failures, failures


def assert_event(actual: events.ResponsesServerEvent, expected: dict[str, Any]) -> None:
    known_type = EVENT_TYPES.get(expected["type"])
    if known_type is not None:
        assert isinstance(actual, known_type)
    # Preserve routing identity, unknown events, and unknown fields at both levels.
    assert actual.to_dict(exclude_unset=True) == expected
    if expected["type"] == "error":
        assert isinstance(actual, events.ResponseWsError)
        assert actual.error.code == "invalid_value"
        assert actual.error.param == "input"
        assert actual.error.message == "Synthetic invalid input"


@pytest.mark.parametrize("scenario", SCENARIOS, ids=lambda scenario: scenario["id"])
def test_responses_websocket_contract(scenario: Scenario) -> None:
    with (
        scenario_server(scenario) as base_url,
        OpenAI(api_key="fake-contract-key", base_url=base_url, http_client=httpx2.Client(trust_env=False)) as client,
    ):
        with client.responses.connect(
            extra_query={"contract": "1"}, extra_headers={"X-Contract-Test": "synthetic"}
        ) as connection:
            for turn in scenario["turns"]:
                connection.response.create(**{key: value for key, value in turn["request"].items() if key != "type"})
                for frame in turn["frames"]:
                    if isinstance(frame, str):
                        with pytest.raises(json.JSONDecodeError):
                            connection.recv()
                    else:
                        assert_event(connection.recv(), frame)
            if "close_code" in scenario:
                # recv() exposes clean EOF even without a response terminal event.
                # Python's iterator instead ends normally on close code 1000.
                error = ConnectionClosedOK if scenario["close_code"] == 1000 else ConnectionClosedError
                with pytest.raises(error) as raised:
                    connection.recv()
                assert raised.value.rcvd is not None
                assert raised.value.rcvd.code == scenario["close_code"]
            connection.close()
            connection.close()


@pytest.mark.parametrize("scenario", SCENARIOS, ids=lambda scenario: scenario["id"])
async def test_async_responses_websocket_contract(scenario: Scenario) -> None:
    with scenario_server(scenario) as base_url:
        async with AsyncOpenAI(
            api_key="fake-contract-key", base_url=base_url, http_client=httpx2.AsyncClient(trust_env=False)
        ) as client:
            async with client.responses.connect(
                extra_query={"contract": "1"}, extra_headers={"X-Contract-Test": "synthetic"}
            ) as connection:
                for turn in scenario["turns"]:
                    await connection.response.create(
                        **{key: value for key, value in turn["request"].items() if key != "type"}
                    )
                    for frame in turn["frames"]:
                        if isinstance(frame, str):
                            with pytest.raises(json.JSONDecodeError):
                                await asyncio.wait_for(connection.recv(), timeout=5)
                        else:
                            assert_event(await asyncio.wait_for(connection.recv(), timeout=5), frame)
                if "close_code" in scenario:
                    error = ConnectionClosedOK if scenario["close_code"] == 1000 else ConnectionClosedError
                    with pytest.raises(error) as raised:
                        await asyncio.wait_for(connection.recv(), timeout=5)
                    assert raised.value.rcvd is not None
                    assert raised.value.rcvd.code == scenario["close_code"]
                await connection.close()
                await connection.close()
