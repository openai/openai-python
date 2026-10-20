from __future__ import annotations

import ssl
import socket
import datetime
import importlib
import threading
import importlib.util
from typing import Any, cast
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from collections.abc import Iterator
from typing_extensions import override

import pytest

from openai import OpenAI, AsyncOpenAI, APIConnectionError, DefaultAioHttpClient
from openai.auth import x509_workload_identity

HOSTS = ["sdk-host.test", "sdk_host.test", "sub_name.sdk_host.test"]
HTTP_LIBRARIES = ["httpx2", "httpx"]


def http_library(name: str) -> Any:
    if importlib.util.find_spec(name) is None:
        pytest.skip(f"{name} is not installed")
    return cast(Any, importlib.import_module(name))


@pytest.mark.parametrize("library", HTTP_LIBRARIES)
@pytest.mark.parametrize("host", HOSTS)
@pytest.mark.parametrize("explicit_sni", [None, "private-pki.test"])
@pytest.mark.parametrize("x509", [False, True])
def test_sync_request_preserves_tls_hostname(library: str, host: str, explicit_sni: str | None, x509: bool) -> None:
    http = http_library(library)
    requests: list[Any] = []

    def handler(request: Any) -> Any:
        if request.url.host == "mtls.auth.openai.com":
            return http.Response(200, json={"access_token": "fake-token", "expires_in": 3600})
        requests.append(request)
        return http.Response(200, json={"object": "list", "data": []})

    def hook(request: Any) -> None:
        if explicit_sni is not None:
            request.extensions["sni_hostname"] = explicit_sni

    identity = x509_workload_identity(identity_provider_id="fake-provider", service_account_id="fake-account")
    with OpenAI(
        api_key=None if x509 else "fake-api-key",
        workload_identity=identity if x509 else None,
        base_url=f"https://{host}/v1",
        http_client=http.Client(
            transport=http.MockTransport(handler), event_hooks={"request": [hook]}, trust_env=False
        ),
        max_retries=0,
    ) as client:
        response = client.get(
            f"https://{host}/v1/models?configured=1", cast_to=http.Response, options={"params": {"request": "2"}}
        )
        assert response.json()["object"] == "list"

    assert len(requests) == 1
    assert requests[0].url.host == host
    assert requests[0].headers["host"] == host
    assert requests[0].url.params["configured"] == "1"
    assert requests[0].url.params["request"] == "2"
    assert requests[0].extensions.get("sni_hostname") == explicit_sni
    assert "timeout" in requests[0].extensions


@pytest.mark.parametrize("library", HTTP_LIBRARIES)
@pytest.mark.parametrize("host", HOSTS)
@pytest.mark.parametrize("explicit_sni", [None, "private-pki.test"])
@pytest.mark.parametrize("x509", [False, True])
async def test_async_request_preserves_tls_hostname(
    library: str, host: str, explicit_sni: str | None, x509: bool
) -> None:
    http = http_library(library)
    requests: list[Any] = []

    async def handler(request: Any) -> Any:
        if request.url.host == "mtls.auth.openai.com":
            return http.Response(200, json={"access_token": "fake-token", "expires_in": 3600})
        requests.append(request)
        return http.Response(200, json={"object": "list", "data": []})

    async def hook(request: Any) -> None:
        if explicit_sni is not None:
            request.extensions["sni_hostname"] = explicit_sni

    identity = x509_workload_identity(identity_provider_id="fake-provider", service_account_id="fake-account")
    async with AsyncOpenAI(
        api_key=None if x509 else "fake-api-key",
        workload_identity=identity if x509 else None,
        base_url=f"https://{host}/v1",
        http_client=http.AsyncClient(
            transport=http.MockTransport(handler), event_hooks={"request": [hook]}, trust_env=False
        ),
        max_retries=0,
    ) as client:
        response = await client.get(
            f"https://{host}/v1/models?configured=1", cast_to=http.Response, options={"params": {"request": "2"}}
        )
        assert response.json()["object"] == "list"

    assert len(requests) == 1
    assert requests[0].url.host == host
    assert requests[0].headers["host"] == host
    assert requests[0].url.params["configured"] == "1"
    assert requests[0].url.params["request"] == "2"
    assert requests[0].extensions.get("sni_hostname") == explicit_sni
    assert "timeout" in requests[0].extensions


@pytest.fixture
def tls_server(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[tuple[int, ssl.SSLContext, list[str]]]:
    # Generate a short-lived, test-only certificate and key; never check in private keys.
    pytest.importorskip("cryptography")
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, HOSTS[0])])
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(minutes=1))
        .not_valid_after(now + datetime.timedelta(days=1))
        .add_extension(x509.SubjectAlternativeName([x509.DNSName(HOSTS[0])]), critical=False)
        .sign(key, hashes.SHA256())
    )
    cert_path = tmp_path / "server.pem"
    key_path = tmp_path / "server.key"
    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    key_path.write_bytes(
        key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    )
    server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    server_context.minimum_version = ssl.TLSVersion.TLSv1_2
    server_context.load_cert_chain(cert_path, key_path)
    client_context = ssl.create_default_context(cafile=str(cert_path))
    requests: list[str] = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            requests.append(self.headers["Host"])
            body = b'{"object":"list","data":[]}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        @override
        def log_message(self, *_args: object, **_kwargs: object) -> None:
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.socket = server_context.wrap_socket(server.socket, server_side=True)
    original_getaddrinfo = socket.getaddrinfo

    def getaddrinfo(host: Any, port: Any, *args: Any, **kwargs: Any) -> Any:
        # Never resolve or connect to an external endpoint, even if the client regresses.
        assert host in (HOSTS[0], HOSTS[1], HOSTS[0].encode(), HOSTS[1].encode(), "127.0.0.1", b"127.0.0.1")
        assert int(port) == server.server_port
        return original_getaddrinfo("127.0.0.1", port, *args, **kwargs)

    monkeypatch.setattr(socket, "getaddrinfo", getaddrinfo)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server.server_port, client_context, requests
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def assert_certificate_error(error: BaseException) -> None:
    cause: BaseException | None = error
    while cause is not None:
        if isinstance(cause, ssl.SSLCertVerificationError):
            return
        cause = cause.__cause__ or cause.__context__
    pytest.fail("Expected certificate hostname verification to fail")


@pytest.mark.parametrize("explicit_sni", [False, True])
@pytest.mark.parametrize("library", HTTP_LIBRARIES)
def test_sync_tls_verifies_configured_hostname(
    library: str, explicit_sni: bool, tls_server: tuple[int, ssl.SSLContext, list[str]]
) -> None:
    http = http_library(library)
    port, context, requests = tls_server

    def hook(request: Any) -> None:
        if explicit_sni:
            request.extensions["sni_hostname"] = HOSTS[0]

    for host in HOSTS[:2]:
        with OpenAI(
            api_key="fake-api-key",
            base_url=f"https://{host}:{port}/v1",
            http_client=http.Client(verify=context, trust_env=False, event_hooks={"request": [hook]}),
            max_retries=0,
        ) as client:
            if host == HOSTS[0] or explicit_sni:
                assert client.models.list().object == "list"
            else:
                with pytest.raises(APIConnectionError) as exc:
                    client.models.list()
                assert_certificate_error(exc.value)
    assert requests == [f"{host}:{port}" for host in HOSTS[: 2 if explicit_sni else 1]]


@pytest.mark.parametrize("explicit_sni", [False, True])
@pytest.mark.parametrize("library", [*HTTP_LIBRARIES, "aiohttp", "httpx_aiohttp"])
async def test_async_tls_verifies_configured_hostname(
    library: str, explicit_sni: bool, tls_server: tuple[int, ssl.SSLContext, list[str]]
) -> None:
    port, context, requests = tls_server

    async def hook(request: Any) -> None:
        if explicit_sni:
            request.extensions["sni_hostname"] = HOSTS[0]

    for host in HOSTS[:2]:
        if library == "aiohttp":
            pytest.importorskip("aiohttp")
            http_client = DefaultAioHttpClient(verify=context, trust_env=False, event_hooks={"request": [hook]})
        elif library == "httpx_aiohttp":
            http_client = http_library(library).HttpxAiohttpClient(
                verify=context, trust_env=False, event_hooks={"request": [hook]}
            )
        else:
            http_client = http_library(library).AsyncClient(
                verify=context, trust_env=False, event_hooks={"request": [hook]}
            )
        async with AsyncOpenAI(
            api_key="fake-api-key",
            base_url=f"https://{host}:{port}/v1",
            http_client=http_client,
            max_retries=0,
        ) as client:
            if host == HOSTS[0] or explicit_sni:
                assert (await client.models.list()).object == "list"
            else:
                with pytest.raises(APIConnectionError) as exc:
                    await client.models.list()
                assert_certificate_error(exc.value)
    assert requests == [f"{host}:{port}" for host in HOSTS[: 2 if explicit_sni else 1]]
