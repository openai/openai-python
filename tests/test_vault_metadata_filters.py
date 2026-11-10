import httpx2 as httpx
import pytest

from openai import OpenAI, AsyncOpenAI


@pytest.mark.parametrize("credentials", [False, True])
def test_empty_metadata_filter_sync(credentials: bool) -> None:
    requests: list[httpx.Request] = []

    def handle(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"data": [], "has_more": False, "object": "list"})

    with OpenAI(
        api_key="test-key",
        base_url="https://example.com/v1",
        http_client=httpx.Client(transport=httpx.MockTransport(handle)),
    ) as client:
        if credentials:
            client.beta.agents.vaults.credentials.list("vault_test", metadata={"state": ""})
        else:
            client.beta.agents.vaults.list(metadata={"state": ""})

    assert len(requests) == 1
    assert requests[0].url.params.get("metadata[state]") == ""
    assert requests[0].url.path == ("/v1/vaults/vault_test/credentials" if credentials else "/v1/vaults")


@pytest.mark.parametrize("credentials", [False, True])
async def test_empty_metadata_filter_async(credentials: bool) -> None:
    requests: list[httpx.Request] = []

    def handle(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"data": [], "has_more": False, "object": "list"})

    async with AsyncOpenAI(
        api_key="test-key",
        base_url="https://example.com/v1",
        http_client=httpx.AsyncClient(transport=httpx.MockTransport(handle)),
    ) as client:
        if credentials:
            await client.beta.agents.vaults.credentials.list("vault_test", metadata={"state": ""})
        else:
            await client.beta.agents.vaults.list(metadata={"state": ""})

    assert len(requests) == 1
    assert requests[0].url.params.get("metadata[state]") == ""
    assert requests[0].url.path == ("/v1/vaults/vault_test/credentials" if credentials else "/v1/vaults")
