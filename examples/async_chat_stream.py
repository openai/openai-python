
#!/usr/bin/env -S rye run python
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def main() -> None:
    # Chat Completions is still supported indefinitely, but it's no longer the primary API.
    # This example remains useful for users who still rely on chat.completions.
    stream = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Say this is a test (streaming)."}],
        stream=True,
    )
    async for chunk in stream:
        # Some users prefer accessing delta objects; for demo purposes, printing the chunk is enough.
        print(chunk)

if __name__ == "__main__":
    asyncio.run(main())

