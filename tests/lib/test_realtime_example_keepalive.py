import os
import sys
import json
import signal
import asyncio
from pathlib import Path

import pytest
from websockets.asyncio.server import ServerConnection, serve


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exit_action",
    [
        "conversation_then_q",
        "eof",
        pytest.param(
            "sigint",
            marks=pytest.mark.skipif(
                sys.platform == "win32", reason="Windows uses console events instead of POSIX SIGINT"
            ),
        ),
    ],
)
async def test_interactive_realtime_example_remains_responsive_at_input(exit_action: str) -> None:
    root = Path(__file__).resolve().parents[2]
    connected: asyncio.Future[ServerConnection] = asyncio.get_running_loop().create_future()

    async def accept(socket: ServerConnection) -> None:
        connected.set_result(socket)
        await socket.wait_closed()

    async with serve(accept, "127.0.0.1", 0, ping_interval=None) as server:
        port = next(iter(server.sockets)).getsockname()[1]
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

            if exit_action == "conversation_then_q":
                process.stdin.write(b"Hello from the example test\n")
                await process.stdin.drain()
                item_event = json.loads(await asyncio.wait_for(socket.recv(), timeout=10))
                assert item_event["type"] == "conversation.item.create"
                assert item_event["item"]["content"] == [{"type": "input_text", "text": "Hello from the example test"}]
                response_event = json.loads(await asyncio.wait_for(socket.recv(), timeout=10))
                assert response_event["type"] == "response.create"
                await socket.send(
                    json.dumps(
                        {
                            "type": "response.output_text.delta",
                            "event_id": "event_delta",
                            "response_id": "resp_example",
                            "item_id": "item_example",
                            "output_index": 0,
                            "content_index": 0,
                            "delta": "Hello back",
                        }
                    )
                )
                await socket.send(
                    json.dumps(
                        {
                            "type": "response.output_text.done",
                            "event_id": "event_text_done",
                            "response_id": "resp_example",
                            "item_id": "item_example",
                            "output_index": 0,
                            "content_index": 0,
                            "text": "Hello back",
                        }
                    )
                )
                await socket.send(
                    json.dumps(
                        {
                            "type": "response.done",
                            "event_id": "event_response_done",
                            "response": {
                                "id": "resp_example",
                                "object": "realtime.response",
                                "status": "completed",
                                "status_details": None,
                                "output": [
                                    {
                                        "id": "item_example",
                                        "object": "realtime.item",
                                        "type": "message",
                                        "status": "completed",
                                        "role": "assistant",
                                        "content": [{"type": "output_text", "text": "Hello back"}],
                                    }
                                ],
                            },
                        }
                    )
                )
                output = await asyncio.wait_for(process.stdout.readuntil(prompt), timeout=10)
                assert output == b"Hello back" + os.linesep.encode() + prompt
                pong = await socket.ping()
                await asyncio.wait_for(pong, timeout=2)
                process.stdin.write(b"q\n")
                await process.stdin.drain()
            elif exit_action == "eof":
                process.stdin.close()
            else:
                process.send_signal(signal.SIGINT)

            await asyncio.wait_for(process.wait(), timeout=2)
            _, stderr = await process.communicate()
            if exit_action == "conversation_then_q":
                assert process.returncode == 0, stderr.decode()
            elif exit_action == "eof":
                assert process.returncode != 0
                assert b"EOFError" in stderr
            else:
                assert process.returncode != 0
                assert b"KeyboardInterrupt" in stderr
        finally:
            if process.returncode is None:
                process.kill()
                await process.communicate()
