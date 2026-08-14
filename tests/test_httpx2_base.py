from __future__ import annotations

import sys
import asyncio
import warnings
import threading
import subprocess
import importlib.util
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing_extensions import override

import httpx2
import pytest

import openai
from openai import OpenAI, AsyncOpenAI
from tests.respx2 import MockRouter


def test_base_import_does_not_load_legacy_httpx() -> None:
    subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; import openai; assert 'httpx2' in sys.modules; assert 'httpx' not in sys.modules",
        ],
        check=True,
    )


@pytest.mark.respx2(base_url="https://example.test/v1")
def test_default_client_and_respx_use_httpx2(respx2_mock: MockRouter) -> None:
    route = respx2_mock.get("/models").mock(return_value=httpx2.Response(200, json={"object": "list", "data": []}))

    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        with OpenAI(api_key="test", base_url="https://example.test/v1") as client:
            response = client.models.with_raw_response.list()

    assert route.called
    assert captured == []
    assert isinstance(response.http_response, httpx2.Response)
    assert isinstance(response.http_request, httpx2.Request)


async def test_existing_http_client_helpers_default_to_httpx2() -> None:
    class SyncHttpClient(openai.DefaultHttpxClient):
        pass

    class AsyncHttpClient(openai.DefaultAsyncHttpxClient):
        pass

    def handler(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(200, json={"object": "list", "data": []}, request=request)

    with SyncHttpClient(transport=httpx2.MockTransport(handler), trust_env=False) as http_client:
        with OpenAI(api_key="test", base_url="https://example.test/v1", http_client=http_client) as client:
            response = client.models.with_raw_response.list()
            assert isinstance(response.http_response, httpx2.Response)

    async with AsyncHttpClient(transport=httpx2.MockTransport(handler), trust_env=False) as http_client:
        async with AsyncOpenAI(api_key="test", base_url="https://example.test/v1", http_client=http_client) as client:
            response = await client.models.with_raw_response.list()
            assert isinstance(response.http_response, httpx2.Response)


@pytest.mark.skipif(importlib.util.find_spec("aiohttp") is None, reason="the aiohttp extra is not installed")
async def test_default_aiohttp_client_uses_httpx2() -> None:
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
            http_client=openai.DefaultAioHttpClient(),
            max_retries=0,
        ) as client:
            assert isinstance(client._client, httpx2.AsyncClient)
            response = await client.models.with_raw_response.list()
    finally:
        await asyncio.to_thread(server.shutdown)
        thread.join()
        server.server_close()

    assert isinstance(response.http_response, httpx2.Response)
