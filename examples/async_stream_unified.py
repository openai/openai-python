#!/usr/bin/env -S rye run python
import asyncio
from openai import AsyncOpenAI
from openai._streaming.unified import extract_text, StreamEvent
from openai._streaming.adapters import ResponsesEventAdapter  # or ChatCompletionsEventAdapter


async def main():
    client = AsyncOpenAI()
    # Example with Responses stream (manual adapter for now)
    async with client.responses.stream(
        model="gpt-4.1-mini",
        input="Write a single haiku about async streams.",
    ) as stream:
        async for raw_evt in stream:
            # Convert raw event into a unified StreamEvent
            ev: StreamEvent = ResponsesEventAdapter.adapt(raw_evt)
            txt = extract_text(ev)
            if txt:
                print(txt, end="")
    print()  # newline at the end


if __name__ == "__main__":
    asyncio.run(main())
