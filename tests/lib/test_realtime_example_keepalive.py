import os
import sys
import json
import signal
import asyncio
from typing import Iterator
from pathlib import Path

import pytest
from websockets.asyncio.server import ServerConnection, serve


@pytest.fixture
def signal_pipe() -> Iterator[tuple[int, int]]:
    read_fd, write_fd = os.pipe()
    try:
        yield read_fd, write_fd
    finally:
        os.close(read_fd)
        os.close(write_fd)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exit_action",
    [
        "conversation_then_q",
        "eof",
        "q_eof",
        "unicode_then_q",
        "preloaded_then_q",
        pytest.param(
            "partial_input_sigint",
            marks=pytest.mark.skipif(sys.platform == "win32", reason="Requires POSIX SIGINT"),
        ),
        pytest.param(
            "sigint",
            marks=pytest.mark.skipif(
                sys.platform == "win32", reason="Windows uses console events instead of POSIX SIGINT"
            ),
        ),
        pytest.param(
            "sigint_worker",
            marks=pytest.mark.skipif(
                not hasattr(signal, "pthread_kill"), reason="Requires POSIX thread-directed signals"
            ),
        ),
    ],
)
async def test_interactive_realtime_example_remains_responsive_at_input(
    exit_action: str, signal_pipe: tuple[int, int]
) -> None:
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

        arguments = [sys.executable, str(root / "examples" / "realtime" / "realtime.py")]
        if exit_action == "sigint_worker":
            # Reproduce SIGINT reaching a worker while the example awaits stdin.
            # Python still has to run its handler on the main thread.
            bootstrap = """
import os, runpy, signal, sys, threading
def interrupt():
    if os.read(int(sys.argv[2]), 1):
        signal.pthread_kill(threading.get_ident(), signal.SIGINT)
threading.Thread(target=interrupt, daemon=True).start()
runpy.run_path(sys.argv[1], run_name="__main__")
"""
            arguments = [sys.executable, "-c", bootstrap, arguments[1], str(signal_pipe[0])]

        process = await asyncio.create_subprocess_exec(
            *arguments,
            env=env,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            pass_fds=(signal_pipe[0],) if exit_action == "sigint_worker" else (),
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

            if exit_action in {"conversation_then_q", "unicode_then_q", "preloaded_then_q"}:
                message = "Hello café 🌍" if exit_action == "unicode_then_q" else "Hello from the example test"
                if exit_action == "unicode_then_q":
                    # Split inside a UTF-8 character, with no complete line yet.
                    encoded = (message + "\r\n").encode()
                    split = encoded.index(b"\xc3") + 1
                    process.stdin.write(encoded[:split])
                    await process.stdin.drain()
                    pong = await socket.ping()
                    await asyncio.wait_for(pong, timeout=2)
                    process.stdin.write(encoded[split:])
                else:
                    suffix = b"q\n" if exit_action == "preloaded_then_q" else b""
                    process.stdin.write(message.encode() + b"\n" + suffix)
                await process.stdin.drain()
                item_event = json.loads(await asyncio.wait_for(socket.recv(), timeout=10))
                assert item_event["type"] == "conversation.item.create"
                assert item_event["item"]["content"] == [{"type": "input_text", "text": message}]
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
                if exit_action != "preloaded_then_q":
                    pong = await socket.ping()
                    await asyncio.wait_for(pong, timeout=2)
                    process.stdin.write(b"q\n")
                    await process.stdin.drain()
            elif exit_action == "q_eof":
                process.stdin.write(b"q")
                await process.stdin.drain()
                process.stdin.close()
            elif exit_action == "eof":
                process.stdin.close()
            elif exit_action == "sigint_worker":
                os.write(signal_pipe[1], b"interrupt")
            else:
                if exit_action == "partial_input_sigint":
                    process.stdin.write(b"unfinished line")
                    await process.stdin.drain()
                    pong = await socket.ping()
                    await asyncio.wait_for(pong, timeout=2)
                process.send_signal(signal.SIGINT)

            try:
                await asyncio.wait_for(process.wait(), timeout=2)
            except asyncio.TimeoutError:
                diagnostics = []
                if sys.platform == "linux":
                    proc = Path("/proc") / str(process.pid)
                    try:
                        diagnostics.extend(
                            line
                            for line in (proc / "status").read_text().splitlines()
                            if line.split(":", 1)[0]
                            in {"State", "Threads", "SigPnd", "ShdPnd", "SigBlk", "SigIgn", "SigCgt"}
                        )
                        diagnostics.append(f"wait channel: {(proc / 'wchan').read_text().strip()}")
                    except OSError as exc:
                        diagnostics.append(f"Process state unavailable: {exc}")
                if process.returncode is None:
                    process.kill()
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=2)
                pytest.fail(
                    "Example did not exit within two seconds.\n"
                    + "\n".join(diagnostics)
                    + f"\nstdout: {stdout.decode(errors='replace')}\nstderr: {stderr.decode(errors='replace')}"
                )
            _, stderr = await process.communicate()
            assert b"Fatal Python error" not in stderr, stderr.decode()
            if exit_action in {"conversation_then_q", "unicode_then_q", "preloaded_then_q", "q_eof"}:
                assert process.returncode == 0, stderr.decode()
            elif exit_action == "eof":
                assert process.returncode != 0
                assert b"EOFError" in stderr
            else:
                assert process.returncode in {1, -signal.SIGINT, 128 + signal.SIGINT}, stderr.decode()
                assert b"KeyboardInterrupt" in stderr
        finally:
            if process.returncode is None:
                process.kill()
                await process.communicate()
