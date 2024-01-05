#!/usr/bin/env -S poetry run python

import asyncio

from openai import AsyncOpenAI

# gets API Key from environment variable OPENAI_API_KEY
client = AsyncOpenAI()


async def main() -> None:
    stream = await client.completions.create(
        model="gpt-3.5-turbo-instruct",
        prompt="Say this is a test",
        stream=True,
    )
    async for completion in stream:
        print(completion.choices[0].text, end="")
    print()


asyncio.run(main())
