"""Example: Using AwsOpenAI (sync) and AsyncAwsOpenAI (async) with SigV4 signing.

Requires:
  - botocore installed (pip install botocore)
  - AWS credentials configured (env vars, ~/.aws/credentials, IAM role, etc.)
  - AWS_REGION or AWS_DEFAULT_REGION set (or pass region= explicitly)

Run:
  export AWS_REGION=us-west-2
  PYTHONPATH=src python3 examples/bedrock_mantle.py
"""

import asyncio

from openai.lib.aws import AwsOpenAI, AsyncAwsOpenAI

# --- Synchronous usage ---

client = AwsOpenAI(region="us-west-2")

response = client.chat.completions.create(
    model="openai.gpt-oss-120b",
    messages=[{"role": "user", "content": "Hello, how are you?"}],
)

print("Sync:", response.choices[0].message.content)


# --- Asynchronous usage ---


async def main() -> None:
    async_client = AsyncAwsOpenAI(region="us-west-2")

    response = await async_client.chat.completions.create(
        model="openai.gpt-oss-120b",
        messages=[{"role": "user", "content": "Hello from async!"}],
    )

    print("Async:", response.choices[0].message.content)


asyncio.run(main())


# --- Streaming usage (sync) ---

print("\nStreaming: ", end="")
stream = client.chat.completions.create(
    model="openai.gpt-oss-120b",
    messages=[{"role": "user", "content": "Count from 1 to 5."}],
    stream=True,
)
for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        print(delta, end="", flush=True)
print()


# --- Streaming usage (async) ---


async def stream_async() -> None:
    async_client = AsyncAwsOpenAI(region="us-west-2")

    print("Async streaming: ", end="")
    stream = await async_client.chat.completions.create(
        model="openai.gpt-oss-120b",
        messages=[{"role": "user", "content": "Count from 1 to 5."}],
        stream=True,
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            print(delta, end="", flush=True)
    print()


asyncio.run(stream_async())
