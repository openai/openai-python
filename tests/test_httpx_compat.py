from __future__ import annotations

import os
import asyncio
import importlib
import threading
from typing import Any, cast
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing_extensions import override

import pytest

from openai import OpenAI, AsyncOpenAI

pytestmark = pytest.mark.skipif(
    os.environ.get("OPENAI_TEST_LEGACY_HTTPX") != "1", reason="requires the dedicated legacy HTTPX compatibility lane"
)


def test_external_legacy_httpx_client_is_supported() -> None:
    httpx = cast(Any, importlib.import_module("httpx"))

    def handler(request: Any) -> Any:
        return httpx.Response(200, request=request, json={"object": "list", "data": []})

    with OpenAI(
        api_key="test",
        base_url="https://example.test/v1",
        http_client=httpx.Client(transport=httpx.MockTransport(handler), trust_env=False),
        max_retries=0,
    ) as client:
        assert isinstance(client._client, httpx.Client)
        response = client.models.list()

    assert response.data is not None


async def test_external_legacy_async_httpx_client_is_supported() -> None:
    httpx = cast(Any, importlib.import_module("httpx"))

    async def handler(request: Any) -> Any:
        return httpx.Response(200, request=request, json={"object": "list", "data": []})

    async with AsyncOpenAI(
        api_key="test",
        base_url="https://example.test/v1",
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handler), trust_env=False),
        max_retries=0,
    ) as client:
        assert isinstance(client._client, httpx.AsyncClient)
        response = await client.models.list()

    assert response.data is not None


async def test_external_legacy_aiohttp_client_is_supported() -> None:
    httpx = cast(Any, importlib.import_module("httpx"))
    HttpxAiohttpClient = cast(Any, importlib.import_module("httpx_aiohttp")).HttpxAiohttpClient

    class ModelsHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"object":"list","data":[]}')

        @override
        def log_message(self, format: str, *_args: object) -> None:  # noqa: A002
            return None

    server = ThreadingHTTPServer(("127.0.0.1", 0), ModelsHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        async with AsyncOpenAI(
            api_key="test",
            base_url=f"http://127.0.0.1:{server.server_port}/v1",
            http_client=HttpxAiohttpClient(),
            max_retries=0,
        ) as client:
            assert isinstance(client._client, httpx.AsyncClient)
            response = await client.models.list()
    finally:
        await asyncio.to_thread(server.shutdown)
        thread.join()
        server.server_close()

    assert response.data is not None
