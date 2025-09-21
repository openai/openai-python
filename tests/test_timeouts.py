import pytest
import httpx
import asyncio

@pytest.mark.anyio
async def test_asyncclient_raises_read_timeout_immediately():
    async def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("forced timeout", request=request)

    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(
        transport=transport,
        timeout=httpx.Timeout(0.05, connect=0.05, read=0.05, write=0.05),
    )
    with pytest.raises(httpx.ReadTimeout):
        await client.get("https://example.test/anything")
    await client.aclose()


@pytest.mark.anyio
async def test_asyncclient_times_out_on_slow_body_via_tcp_server():
    async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        try:
            # lê até o fim dos headers HTTP
            await reader.readuntil(b"\r\n\r\n")
        except Exception:
            writer.close()
            return
        # envia apenas os headers, sem corpo ainda
        writer.write(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\n")
        await writer.drain()
        # atrasa o corpo além do read-timeout do cliente
        await asyncio.sleep(0.2)
        writer.write(b"ok")
        try:
            await writer.drain()
        finally:
            writer.close()

    server = await asyncio.start_server(handle, host="127.0.0.1", port=0)
    try:
        port = server.sockets[0].getsockname()[1]
        url = f"http://127.0.0.1:{port}/"

        client = httpx.AsyncClient(
            timeout=httpx.Timeout(0.05, connect=0.05, read=0.05, write=0.05)
        )
        with pytest.raises(httpx.ReadTimeout):
            # ao tentar ler o corpo, deve estourar read-timeout
            await client.get(url)
        await client.aclose()
    finally:
        server.close()
        await server.wait_closed()
