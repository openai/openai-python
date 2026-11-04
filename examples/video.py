#!/usr/bin/env -S uv run python

import asyncio

from openai import AsyncOpenAI

client = AsyncOpenAI()


async def main() -> None:
    # This example intentionally demonstrates the deprecated video helper.
    video = await client.videos.create_and_poll(  # ty: ignore[deprecated]
        model="sora-2",
        prompt="A video of the words 'Thank you' in sparkling letters",
    )

    if video.status == "completed":
        print("Video successfully completed: ", video)
    else:
        print("Video creation failed. Status: ", video.status)


asyncio.run(main())
