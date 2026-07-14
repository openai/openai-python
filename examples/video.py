#!/usr/bin/env -S poetry run python
"""
Example script demonstrating video generation using Sora.

This async script generates a video from a text prompt using OpenAI's Sora model
and polls until the video generation is complete.
"""

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
