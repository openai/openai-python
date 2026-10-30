"""Record both Azure upgrades completely, then compare SDK-key policy or caller override."""

import json
import asyncio
from typing import Any
from contextlib import AsyncExitStack

import httpx2
import pytest

import openai
from tests.lib.responses.test_websocket_session import script_server


@pytest.mark.parametrize("mode", ["sync", "async"])
@pytest.mark.parametrize("beta", [False, True])
@pytest.mark.parametrize("caller_authorization", ["absent", "present", "omit"])
async def test_azure_key_policy_survives_complete_responses_replacement(mode, beta, caller_authorization):
    observed = []
    restores = []

    def peer(socket):
        headers = socket.request.headers
        observed.append(
            {
                "api-key": headers.get_all("api-key"),
                "Authorization": headers.get_all("Authorization"),
                "X-Caller": headers.get_all("X-Caller"),
            }
        )
        if len(observed) == 1:
            socket.send('{"type":"response.fixture","generation":1}')
            assert json.loads(socket.recv(timeout=4)) == {"type": "response.fixture", "permit": "replacement"}
            socket.close(1011, "fixture")
        else:
            socket.send('{"type":"response.fixture","generation":2}')
            assert json.loads(socket.recv(timeout=4)) == {"type": "response.fixture", "received": 2}

    def restore(event):
        restores.append(event.close_code)

    headers: dict[str, Any] = {"X-Caller": "retained"}
    if caller_authorization == "present":
        headers["aUtHoRiZaTiOn"] = "Bearer caller-selected-fixture"
    elif caller_authorization == "omit":
        headers["authorization"] = openai.omit
    with script_server(peer, expected_connections=2) as url:
        async with AsyncExitStack() as stack:
            if mode == "sync":
                cli = stack.enter_context(
                    openai.AzureOpenAI(
                        api_key="fake-azure-sdk-key",
                        api_version="fixture",
                        base_url=url,
                        default_headers=headers,
                        http_client=httpx2.Client(trust_env=False),
                    )
                )
                resource = cli.beta.responses if beta else cli.responses
                conn = stack.enter_context(resource.connect(on_reconnecting=restore, initial_delay=0, max_retries=1))
                sync_iterator = iter(conn)

                async def advance():
                    return await asyncio.to_thread(lambda: next(sync_iterator))
            else:
                cli = await stack.enter_async_context(
                    openai.AsyncAzureOpenAI(
                        api_key="fake-azure-sdk-key",
                        api_version="fixture",
                        base_url=url,
                        default_headers=headers,
                        http_client=httpx2.AsyncClient(trust_env=False),
                    )
                )
                resource = cli.beta.responses if beta else cli.responses
                conn = await stack.enter_async_context(
                    resource.connect(on_reconnecting=restore, initial_delay=0, max_retries=1)
                )
                async_iterator = aiter(conn)

                async def advance():
                    return await anext(async_iterator)

            async def send(connection: Any, msg: dict[str, Any]):
                if mode == "sync":
                    await asyncio.to_thread(connection.send, msg)
                else:
                    await connection.send(msg)

            assert (await asyncio.wait_for(advance(), 4)).generation == 1
            await send(conn, {"type": "response.fixture", "permit": "replacement"})
            assert (await asyncio.wait_for(advance(), 4)).generation == 2
            await send(conn, {"type": "response.fixture", "received": 2})
    assert restores == [1011]
    # The peer completed both exchanges. A failure here cannot hide under the
    # server helper's initial/expected-count cleanup assertion.
    expected = {
        "api-key": ["fake-azure-sdk-key"],
        "Authorization": ["Bearer caller-selected-fixture"] if caller_authorization == "present" else [],
        "X-Caller": ["retained"],
    }
    assert observed == [expected, expected]
