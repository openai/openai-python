import os
import sys
import json
import asyncio
from pathlib import Path

import pytest
from websockets.asyncio.server import ServerConnection, serve


@pytest.mark.asyncio
async def test_interactive_realtime_example_answers_ping_while_waiting_for_input() -> None:
    root = Path(__file__).resolve().parents[2]
    connected: asyncio.Future[ServerConnection] = asyncio.get_running_loop().create_future()

    async def accept(socket: ServerConnection) -> None:
        connected.set_result(socket)
        await socket.wait_closed()

    async with serve(accept, "127.0.0.1", 0, ping_interval=None) as server:
        port = server.sockets[0].getsockname()[1]
        env = {
            **os.environ,
            "OPENAI_API_KEY": "example-test-key",
            "OPENAI_BASE_URL": f"http://127.0.0.1:{port}/v1",
            "PYTHONPATH": str(root / "src"),
            "PYTHONUNBUFFERED": "1",
        }
        # This subprocess only connects to the local test peer.
        for name in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"):
            env.pop(name, None)

        process = await asyncio.create_subprocess_exec(
            sys.executable,
            str(root / "examples" / "realtime" / "realtime.py"),
            env=env,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        assert process.stdin is not None
        assert process.stdout is not None
        try:
            socket = await asyncio.wait_for(connected, timeout=10)
            event = json.loads(await asyncio.wait_for(socket.recv(), timeout=10))
            assert event["type"] == "session.update"
            prompt = b"Enter a message: "
            assert await asyncio.wait_for(process.stdout.readexactly(len(prompt)), timeout=10) == prompt
            pong = await socket.ping()
            await asyncio.wait_for(pong, timeout=2)
        finally:
            if process.returncode is None:
                process.stdin.write(b"q\n")
                await process.stdin.drain()
            _, stderr = await asyncio.wait_for(process.communicate(), timeout=10)
        assert process.returncode == 0, stderr.decode()
