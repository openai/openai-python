import pytest
import httpx
from openai import AsyncOpenAI

@pytest.mark.anyio
async def test_openai_client_bubbles_readtimeout_from_transport():
    async def handler(request: httpx.Request) -> httpx.Response:
        # Força um ReadTimeout vindo do transporte
        raise httpx.ReadTimeout("forced timeout", request=request)

    transport = httpx.MockTransport(handler)
    http_client = httpx.AsyncClient(
        transport=transport,
        timeout=httpx.Timeout(0.05, connect=0.05, read=0.05, write=0.05),
        base_url="https://api.openai.test",
    )
    client = AsyncOpenAI(
        api_key="dummy",
        http_client=http_client,
        base_url="https://api.openai.test"
    )

    with pytest.raises(httpx.ReadTimeout):
        # Qualquer chamada simples; o MockTransport intercepta
        await client.models.list()

    await http_client.aclose()
