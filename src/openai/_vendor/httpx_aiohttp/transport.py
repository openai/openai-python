from __future__ import annotations

import contextlib
import ssl
import typing
import typing as t
from importlib import metadata
from logging import warning

import aiohttp
import httpx2 as httpx
from aiohttp import BasicAuth, ClientTimeout
from aiohttp.client import ClientResponse, ClientSession

AIOHTTP_EXC_MAP = {
    aiohttp.ServerTimeoutError: httpx.TimeoutException,
    aiohttp.SocketTimeoutError: httpx.ReadTimeout,
    aiohttp.ClientConnectionError: httpx.ConnectTimeout,
    aiohttp.ClientConnectorError: httpx.ConnectError,
    aiohttp.ClientPayloadError: httpx.ReadError,
    aiohttp.ClientProxyConnectionError: httpx.ProxyError,
    aiohttp.ClientHttpProxyError: httpx.ProxyError,
}

if metadata.version("aiohttp") >= "3.10.0":
    AIOHTTP_EXC_MAP.update(
        {
            aiohttp.client_exceptions.NonHttpUrlClientError: httpx.UnsupportedProtocol,  # type: ignore[reportAttributeAccessIssue]
            aiohttp.client_exceptions.InvalidUrlClientError: httpx.UnsupportedProtocol,  # type: ignore[reportAttributeAccessIssue]
        }
    )

SOCKET_OPTION = t.Union[
    t.Tuple[int, int, int],
    t.Tuple[int, int, t.Union[bytes, bytearray]],
    t.Tuple[int, int, None, int],
]


@contextlib.contextmanager
def map_aiohttp_exceptions() -> typing.Iterator[None]:
    try:
        yield
    except Exception as exc:
        mapped_exc = None

        for from_exc, to_exc in AIOHTTP_EXC_MAP.items():
            if not isinstance(exc, from_exc):  # type: ignore
                continue
            if mapped_exc is None or issubclass(to_exc, mapped_exc):
                mapped_exc = to_exc

        if mapped_exc is None:  # pragma: no cover
            raise

        message = str(exc)
        raise mapped_exc(message) from exc


class AiohttpResponseStream(httpx.AsyncByteStream):
    CHUNK_SIZE = 1024 * 16

    def __init__(self, aiohttp_response: ClientResponse) -> None:
        self._aiohttp_response = aiohttp_response

    async def __aiter__(self) -> typing.AsyncIterator[bytes]:
        with map_aiohttp_exceptions():
            async for chunk in self._aiohttp_response.content.iter_chunked(self.CHUNK_SIZE):
                yield chunk

    async def aclose(self) -> None:
        with map_aiohttp_exceptions():
            await self._aiohttp_response.__aexit__(None, None, None)


class AiohttpTransport(httpx.AsyncBaseTransport):
    def __init__(
        self,
        verify: ssl.SSLContext | str | bool = True,
        cert: t.Union[str, t.Tuple[str, str], t.Tuple[str, str, str], None] = None,
        trust_env: bool = True,
        http1: bool = True,
        http2: bool = False,
        limits: httpx.Limits = httpx.Limits(max_connections=100, max_keepalive_connections=20),
        proxy: httpx.Proxy | None = None,
        uds: str | None = None,
        local_address: str | None = None,
        retries: int = 0,
        socket_options: typing.Iterable[SOCKET_OPTION] | None = None,
        client: ClientSession | t.Callable[[], ClientSession] | None = None,
        # Additional keyword arguments for future compatibility
        # If httpx decides to add one, we won't break the API
        **kwargs: t.Dict[str, t.Any],
    ) -> None:
        if http2:
            if not http1:
                raise httpx.UnsupportedProtocol("HTTP/2 is not supported by aiohttp transport, use HTTP/1.1 instead.")
            warning("HTTP/2 is not supported by aiohttp transport, using HTTP/1.1 instead.")

        ssl_context = httpx.create_ssl_context(
            verify=verify,
            cert=cert,
            trust_env=trust_env,
        )

        self.ssl_context = ssl_context
        self.proxy = proxy
        self.limits = limits
        self.retries = retries
        self.socket_options = socket_options or []
        self.uds = uds
        self.local_address = local_address

        self.client = client

    def get_client(self) -> ClientSession:
        if callable(self.client):
            return self.client()
        elif isinstance(self.client, ClientSession):
            return self.client
        else:
            limit_kwarg = (
                {
                    "limit": self.limits.max_connections,
                }
                if self.limits.max_connections is not None
                else {}
            )
            if self.uds:
                connector = aiohttp.UnixConnector(
                    path=self.uds,
                    keepalive_timeout=self.limits.keepalive_expiry,
                    **limit_kwarg,  # type: ignore
                )
            else:
                connector = aiohttp.TCPConnector(
                    keepalive_timeout=self.limits.keepalive_expiry,
                    ssl=self.ssl_context,
                    local_addr=(self.local_address, 0) if self.local_address else None,
                    **limit_kwarg,  # type: ignore
                )
            return ClientSession(connector=connector)

    async def handle_async_request(
        self,
        request: httpx.Request,
    ) -> httpx.Response:
        if not isinstance(self.client, ClientSession):
            self.client = self.get_client()

        timeout = request.extensions.get("timeout", {})
        sni_hostname = request.extensions.get("sni_hostname")

        with map_aiohttp_exceptions():
            data: t.Union[bytes, httpx.AsyncByteStream, None]
            try:
                data = request.content
                if data == b"":
                    data = None

            except httpx.RequestNotRead:
                data = request.stream  # type: ignore
                request.headers.pop("transfer-encoding", None)  # handled by aiohttp

            response = await self.client.request(
                method=request.method,
                url=str(request.url) if request.url else "https://127.0.0.1:8000/",
                headers=request.headers,
                data=data,
                allow_redirects=False,
                auto_decompress=False,
                compress=False,
                timeout=ClientTimeout(
                    sock_connect=timeout.get("connect"),
                    sock_read=timeout.get("read"),
                    connect=timeout.get("pool"),
                ),
                server_hostname=sni_hostname,
                proxy=str(self.proxy.url) if self.proxy else None,
                proxy_auth=BasicAuth(self.proxy.auth[0], self.proxy.auth[1])
                if self.proxy and self.proxy.auth
                else None,
                proxy_headers=self.proxy.headers if self.proxy else None,
            ).__aenter__()

        extensions = {"http_version": b"HTTP/1.1"}

        if response.reason:
            extensions["reason_phrase"] = response.reason.encode()

        return httpx.Response(
            status_code=response.status,
            headers=response.raw_headers,
            stream=AiohttpResponseStream(response),
            request=request,
            extensions=extensions,
        )

    async def aclose(self) -> None:
        if isinstance(self.client, ClientSession):
            await self.client.close()
