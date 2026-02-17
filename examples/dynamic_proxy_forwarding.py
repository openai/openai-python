"""
Example: forwarding OpenAI requests through an intermediary proxy.

Machine A sends requests to Machine B, and Machine B forwards to the OpenAI service while preserving streaming responses.
"""

import os
import httpx
from openai import OpenAI, AsyncOpenAI

# Base URL for your proxy server (Machine B)
proxy_base_url = os.getenv("PROXY_BASE_URL", "http://my.proxy.host:8080/v1")


def run_sync_example() -> None:
    """Synchronously send a chat completion request via the proxy and stream the response."""
    client = OpenAI(
        base_url=proxy_base_url,
        http_client=httpx.Client(proxies=proxy_base_url),
    )
    with client.chat.completions.stream(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Hello!"}],
    ) as stream:
        for event in stream:
            print(event.content or "", end="", flush=True)


async def run_async_example() -> None:
    """Asynchronously send a chat completion request via the proxy and stream the response."""
    async_client = AsyncOpenAI(
        base_url=proxy_base_url,
        http_client=httpx.AsyncClient(proxies=proxy_base_url),
    )
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
