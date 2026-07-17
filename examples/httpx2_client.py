#!/usr/bin/env -S poetry run python

import asyncio

from openai import OpenAI, AsyncOpenAI, DefaultHttpx2Client, DefaultAsyncHttpx2Client

# gets API Key from environment variable OPENAI_API_KEY
client = OpenAI(http_client=DefaultHttpx2Client())

# Non-streaming, synchronous client backed by httpx2:
print("----- standard request -----")
completion = client.chat.completions.create(
    model="gpt-5.5",
    messages=[
        {
            "role": "user",
            "content": "Say this is a test",
        },
    ],
)
print(completion.choices[0].message.content)


async def main() -> None:
    async with AsyncOpenAI(http_client=DefaultAsyncHttpx2Client()) as async_client:
        print("----- async streaming request -----")
        stream = await async_client.chat.completions.create(
            model="gpt-5.5",
            messages=[
                {
                    "role": "user",
                    "content": "How do I output all files in a directory using Python?",
                },
            ],
            stream=True,
        )
        async for chunk in stream:
            if not chunk.choices:
                continue

            print(chunk.choices[0].delta.content, end="")
        print()


asyncio.run(main())
