#!/usr/bin/env -S poetry run python

import asyncio

from openai import AsyncOpenAI

# gets API Key from environment variable OPENAI_API_KEY
client = AsyncOpenAI()


async def main() -> None:
    stream = await client.chat.completions.create(
        model="gpt-5.5",
        messages=[
            {
                "role": "user",
                "content": "Say this is a test",
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
