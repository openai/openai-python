
#!/usr/bin/env -S rye run python
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def main() -> None:
    # Async streaming with the Responses API (the recommended primary API).
    stream = await client.responses.create(
        model="gpt-4o-mini",
        input="Write a one-sentence bedtime story about a unicorn.",
        stream=True,
    )
    async for event in stream:
        # Each event may contain deltas and final results; printing directly is sufficient for demo purposes.
        print(event)

if __name__ == "__main__":
    asyncio.run(main())

