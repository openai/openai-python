"""
Example: routing OpenAI requests through an HTTP forward proxy.

Useful when outbound traffic from your machine must egress through a proxy
(e.g. a corporate gateway or a bastion host) before reaching the OpenAI API.
The proxy is configured on the underlying httpx client, and streaming
responses are preserved end-to-end.
"""

import os

import httpx

from openai import OpenAI, AsyncOpenAI

# Address of your forward proxy -- the proxy's own host:port, NOT the OpenAI
# base URL. The OpenAI client keeps its default base URL and reads the API key
# from the OPENAI_API_KEY environment variable.
proxy_url = os.getenv("OPENAI_PROXY_URL", "http://my.proxy.host:8080")


def run_sync_example() -> None:
    """Synchronously send a chat completion through the proxy and stream the response."""
    # `proxy=` replaces httpx's `proxies=` argument, which was removed in httpx 0.28.
    client = OpenAI(http_client=httpx.Client(proxy=proxy_url))
    with client.chat.completions.stream(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Hello!"}],
    ) as stream:
        for event in stream:
            print(event.content or "", end="", flush=True)


async def run_async_example() -> None:
    """Asynchronously send a chat completion through the proxy and stream the response."""
    async_client = AsyncOpenAI(http_client=httpx.AsyncClient(proxy=proxy_url))
    async with async_client.chat.completions.stream(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Hi!"}],
    ) as stream:
        async for event in stream:
            print(event.content or "", end="", flush=True)


if __name__ == "__main__":
    # For demonstration purposes, run the synchronous example when executed directly.
    run_sync_example()
    # To run the asynchronous example, use: asyncio.run(run_async_example())
