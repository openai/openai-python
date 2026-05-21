#!/usr/bin/env rye run python

import asyncio

from openai import AsyncOpenAI
from openai.helpers import Microphone

# gets OPENAI_API_KEY from your environment variables
openai = AsyncOpenAI()


async def main() -> None:
    print("Recording for the next 10 seconds...")
    recording = await Microphone(timeout=10).record()
    print("Recording complete")
    transcription = await openai.audio.transcriptions.create(
        model="whisper-1",
        file=recording,
    )

    print(transcription.text)


if __name__ == "__main__":
    asyncio.run(main())
