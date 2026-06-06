#!/usr/bin/env -S rye run python

import asyncio

from openai import AsyncOpenAI

# gets API Key from environment variable OPENAI_API_KEY
client = AsyncOpenAI()


async def main() -> None:
    stream = await client.chat.completions.create(
        model="gpt-4o",
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

        print(chunk.choices[0].delta.content or "", end="")
    print()


asyncio.run(main())
