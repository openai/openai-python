"""Opt-in hosted Live fixture checks.

Run with OPENAI_LIVE_FIXTURE_TEST=1 and OPENAI_API_KEY set for a project
eligible to store Live sessions. The normal OPENAI_BASE_URL and OPENAI_PROJECT_ID
client settings apply. Nothing is stored except the synthetic silence made here.

To also check sideband, supply OPENAI_LIVE_SIGNALING_SESSION_ID for an active
synthetic WebRTC/SIP session owned by that same project/key. Run with -s and
watch for the new synthetic event ID printed after attachment. Within 120s,
have the fixture's owner send this command through its controlling connection:

    {"type":"session.instructions.append", "event_id":"<printed ID>",
     "content":"Continue the synthetic fixture.", "delegation_id":null}

The sideband itself only observes; it does not start, change, or close the
session. Replayed or terminal events never prove a post-attachment command.
Without the supplied fixture the test skips, never passes.

    uv run --locked --all-extras pytest -n 0 -q -s tests/lib/live/test_hosted_fixtures.py
"""

from __future__ import annotations

import os
import base64
import asyncio
import logging
from uuid import uuid4
from typing import Iterator

import pytest

from openai import AsyncOpenAI
from openai.types.live import ServerEvent, ForkServerEvent
from openai.resources.live.live import AsyncLiveConnection
from openai.resources.live.forks import AsyncForksConnection
from openai.resources.live.sideband import AsyncSidebandConnection

pytestmark = pytest.mark.skipif(
    os.environ.get("OPENAI_LIVE_FIXTURE_TEST") != "1" or not os.environ.get("OPENAI_API_KEY"),
    reason="Hosted Live requires explicit opt-in and an eligible project's OPENAI_API_KEY",
)


@pytest.fixture(autouse=True)
def no_hosted_payload_logging() -> Iterator[None]:
    # Debug HTTP/WebSocket logs can contain credentials, session IDs or media.
    previous = logging.root.manager.disable
    logging.disable(logging.CRITICAL)
    try:
        yield
    finally:
        logging.disable(previous)


async def _until(
    connection: AsyncLiveConnection | AsyncForksConnection | AsyncSidebandConnection,
    expected: str,
    *,
    require_stored: bool = False,
    client_event_id: str | None = None,
) -> ServerEvent | ForkServerEvent:
    async def receive() -> ServerEvent | ForkServerEvent:
        while True:
            event = await connection.recv()
            if event.type in {"error", "transport.failed"}:
                pytest.fail("Hosted Live returned an error (including possible storage failure)", pytrace=False)
            if client_event_id is not None and event.type == "session.closed":
                pytest.fail("The signaling session closed before the post-attachment command", pytrace=False)
            # Every snapshot of the session we will fork must remain eligible.
            if require_stored and (
                event.type == "session.started" or event.type == "session.updated" or event.type == "session.closed"
            ):
                if event.session.store is not True:
                    pytest.fail("Hosted Live did not retain store=true; no fork is allowed", pytrace=False)
            if event.type == expected:
                if client_event_id is None or (
                    event.type == "session.instructions.appended" and event.client_event_id == client_event_id
                ):
                    return event

    return await asyncio.wait_for(receive(), timeout=120 if client_event_id is not None else 20)


async def test_hosted_stored_primary_and_same_key_fork() -> None:
    try:
        async with AsyncOpenAI(max_retries=0) as client:
            async with client.live.connect(max_retries=0) as primary:
                await primary.session.start(
                    session={
                        "model": "gpt-live-1",
                        "store": True,
                        "audio": {"format": {"type": "audio/pcm", "rate": 24000}},
                    }
                )
                await _until(primary, "session.started", require_stored=True)
                # 3 x 20 ms of PCM16 mono silence at 24 kHz; no user media.
                frame = base64.b64encode(bytes(960)).decode("ascii")
                for _ in range(3):
                    await primary.session.input_audio.append(audio=frame)
                await primary.session.close()
                terminal = await _until(primary, "session.closed", require_stored=True)
                if terminal.type != "session.closed" or terminal.reason != "close_requested":
                    pytest.fail("Stored primary did not finalize after its close request", pytrace=False)

            # Only fork our own newly finalized, verified-stored session, with the same client.
            async with client.live.forks.connect(session_id=terminal.session.id, max_retries=0) as fork:
                await fork.session.start(session={"store": False})
                await _until(fork, "session.started")
                await fork.session.close()
                terminal = await _until(fork, "session.closed")
                if terminal.type != "session.closed" or terminal.reason != "close_requested":
                    pytest.fail("Stored fork did not finalize after its close request", pytrace=False)
    except Exception as exc:
        # Never include remote messages, URLs, IDs, response bodies or tracebacks.
        raise pytest.fail.Exception(f"Hosted Live primary/fork failed ({type(exc).__name__})", pytrace=False) from None


async def test_hosted_signaling_sideband_observes_fixture() -> None:
    session_id = os.environ.get("OPENAI_LIVE_SIGNALING_SESSION_ID")
    if not session_id:
        pytest.skip("Provide a same-project synthetic signaling session; no arbitrary session ID is used")
    try:
        async with AsyncOpenAI(max_retries=0) as client:
            async with client.live.sideband.connect(session_id=session_id, max_retries=0) as sideband:
                # This test-generated ID is public and cannot exist in the attachment replay.
                nonce = f"live-fixture-{uuid4().hex}"
                print(f"Post-attachment synthetic event_id: {nonce}", flush=True)
                await _until(sideband, "session.instructions.appended", client_event_id=nonce)
    except Exception as exc:
        raise pytest.fail.Exception(f"Hosted Live sideband failed ({type(exc).__name__})", pytrace=False) from None
