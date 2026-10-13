"""Interrupt a CLI during a local API call or approval and verify its receipt."""

from __future__ import annotations

import os
import sys
import json
import signal
import asyncio
import tempfile
from typing import Any
from pathlib import Path


async def exercise(stage: str) -> None:
    received = asyncio.Event()
    requests = 0

    async def hold_request(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        nonlocal requests
        try:
            headers = await reader.readuntil(b"\r\n\r\n")
            assert headers.startswith(b"POST /v1/responses "), headers.split(b"\r\n")[0]
            body: dict[str, Any] = {}
            for line in headers.split(b"\r\n"):
                if line.lower().startswith(b"content-length:"):
                    body = json.loads(await reader.readexactly(int(line.split(b":", 1)[1])))
            requests += 1
            if stage == "approval":
                args: dict[str, object] = {"tab_id": None, "filter": "all"}
                member = "read_page"
                if requests > 1:
                    last = body["input"][-1]
                    observed = json.loads(last["output"][0]["text"])
                    element = observed["result"]["elements"][0]
                    args = {"tab_id": None, "target": element["ref"]}
                    member = "click"
                result = json.dumps(
                    {
                        "id": f"resp_{requests}",
                        "object": "response",
                        "created_at": 0,
                        "status": "completed",
                        "model": "",
                        "output": [
                            {
                                "type": "function_call",
                                "id": f"fc_{requests}",
                                "call_id": f"call_{requests}",
                                "name": f"browser_{member}",
                                "arguments": json.dumps(args),
                                "status": "completed",
                            }
                        ],
                    }
                ).encode()
                writer.write(
                    b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nConnection: close\r\nContent-Length: "
                    + str(len(result)).encode()
                    + b"\r\n\r\n"
                    + result
                )
                await writer.drain()
                return
            received.set()
            await reader.read()
        finally:
            writer.close()
            await writer.wait_closed()

    server = await asyncio.start_server(hold_request, "127.0.0.1", 0)
    async with server:
        with tempfile.TemporaryDirectory(prefix="workflow-cancel-") as directory:
            receipt = Path(directory) / "cancelled.json"
            port = server.sockets[0].getsockname()[1]
            env = {key: value for key, value in os.environ.items() if not key.startswith("OPENAI_")}
            env.pop("PYTHONPATH", None)
            env.pop("PYTHONSAFEPATH", None)
            env.update(
                OPENAI_API_KEY="synthetic-local-not-a-key",
                OPENAI_MODEL="synthetic-local",
                OPENAI_BASE_URL=f"http://127.0.0.1:{port}/v1",
            )
            child = await asyncio.create_subprocess_exec(
                sys.executable,
                str(Path(__file__).with_name("run.py")),
                "--receipt",
                str(receipt),
                env=env,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                if stage == "approval":
                    assert child.stdout is not None
                    prompt = await asyncio.wait_for(child.stdout.readuntil(b"? [y/N] "), timeout=15)
                    assert b"button" in prompt and b"Requests" in prompt, prompt
                else:
                    await asyncio.wait_for(received.wait(), timeout=15)
                child.send_signal(signal.SIGINT)
                try:
                    # Do not close stdin early: a blocked approval must also exit on Ctrl+C.
                    await asyncio.wait_for(child.wait(), timeout=15)
                except asyncio.TimeoutError as exc:
                    saved_state = receipt.read_text() if receipt.exists() else "No receipt was written."
                    raise AssertionError(f"SIGINT did not exit. {saved_state}") from exc
                stdout, stderr = await child.communicate()
                assert child.returncode == 1, stderr.decode()
                assert json.loads(stdout) == {"status": "stopped"}, stdout.decode()
                saved = json.loads(receipt.read_bytes())
                assert saved["status"] == "stopped"
                assert saved["cleanup"] is True
                assert saved["stored"] == {"bookings": {}, "correspondence": {}}
                assert receipt.stat().st_mode & 0o777 == 0o600
                assert "synthetic-local" not in receipt.read_text()
            finally:
                if child.returncode is None:
                    child.kill()
                    await child.communicate()
    print(f"PASS SIGINT during CLI {stage} records stopped, cleans up, preserves empty stores, and exits.")


async def main() -> None:
    await exercise("request")
    await exercise("approval")


if __name__ == "__main__":
    asyncio.run(main())
