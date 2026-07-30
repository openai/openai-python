from __future__ import annotations

import os
import ssl
import sys
import threading
import subprocess
from typing import Any, cast
from pathlib import Path
from contextlib import contextmanager
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from collections.abc import Iterator
from typing_extensions import override

import pytest

ROOT = Path(__file__).parent.parent
FIXTURES = Path(__file__).parent / "fixtures" / "mtls"
CERTIFICATE_CHAIN = FIXTURES / "client-chain.pem"
PRIVATE_KEY = FIXTURES / "client.key"
ROOT_CERTIFICATE = FIXTURES / "root.pem"
SERVER_CERTIFICATE_CHAIN = FIXTURES / "server-chain.pem"
SERVER_PRIVATE_KEY = FIXTURES / "server.key"


class _Handler(BaseHTTPRequestHandler):
    peer_certificates: list[dict[str, Any]] = []
    request_paths: list[str] = []

    def do_GET(self) -> None:
        peer_certificate = cast(ssl.SSLSocket, self.connection).getpeercert()
        assert peer_certificate is not None
        self.peer_certificates.append(cast(dict[str, Any], peer_certificate))
        self.request_paths.append(self.path)
        body = b'{"object":"list","data":[]}'
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    @override
    def log_message(self, format: str, *args: object) -> None:
        pass


@contextmanager
def _mtls_server() -> Iterator[ThreadingHTTPServer]:
    _Handler.peer_certificates = []
    _Handler.request_paths = []
    server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    server_context.minimum_version = ssl.TLSVersion.TLSv1_2
    server_context.load_cert_chain(
        certfile=SERVER_CERTIFICATE_CHAIN,
        keyfile=SERVER_PRIVATE_KEY,
    )
    server_context.load_verify_locations(cafile=ROOT_CERTIFICATE)
    server_context.verify_mode = ssl.CERT_REQUIRED

    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    server.socket = server_context.wrap_socket(server.socket, server_side=True)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


@pytest.mark.parametrize(
    "example",
    [
        "mtls_httpx.py",
        "mtls_httpx_async.py",
        "mtls_httpx2.py",
        "mtls_httpx2_async.py",
    ],
)
def test_mtls_example_presents_full_client_chain(example: str) -> None:
    assert CERTIFICATE_CHAIN.read_text().count("-----BEGIN CERTIFICATE-----") == 2

    with _mtls_server() as server:
        proxy_variables = {
            "ALL_PROXY",
            "HTTPS_PROXY",
            "HTTP_PROXY",
            "NO_PROXY",
            "all_proxy",
            "https_proxy",
            "http_proxy",
            "no_proxy",
        }
        environment = {
            **{name: value for name, value in os.environ.items() if name not in proxy_variables},
            "OPENAI_API_KEY": "test-api-key",
            "OPENAI_BASE_URL": f"https://127.0.0.1:{server.server_port}/v1",
            "OPENAI_MTLS_CA_BUNDLE": str(ROOT_CERTIFICATE),
            "OPENAI_MTLS_CERTIFICATE_CHAIN": str(CERTIFICATE_CHAIN),
            "OPENAI_MTLS_PRIVATE_KEY": str(PRIVATE_KEY),
        }
        result = subprocess.run(
            [sys.executable, str(ROOT / "examples" / example)],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )

    assert result.returncode == 0, result.stderr
    assert "data=[]" in result.stdout
    assert _Handler.request_paths == ["/v1/files"]
    assert _Handler.peer_certificates[0]["subject"] == ((("commonName", "openai-python-mtls-test-client"),),)
