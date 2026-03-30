#!/usr/bin/env -S poetry run python

import asyncio

from openai import AsyncOpenAI

client = AsyncOpenAI()


async def main() -> None:
    video = await client.videos.create_and_poll(
        model="sora-2",
        prompt="A video of the words 'Thank you' in sparkling letters",
    )

    if video.status == "completed":
        print("Video successfully completed: ", video)
    else:
        print("Video creation failed. Status: ", video.status)


asyncio.run(main())
