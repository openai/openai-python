"""Stream a mono PCM WAV to Live and print grouped user/assistant transcripts.

Run with OPENAI_API_KEY in the environment:
    python examples/live/audio_transcript.py speech.wav

Use a 16-bit mono WAV recorded at 24 kHz. Audio is paced in real time. This
example sends silence after the recording so the assistant can finish replying.
"""

from __future__ import annotations

import os
import wave
import base64
import asyncio
import argparse
from pathlib import Path

from openai import AsyncOpenAI, OpenAIError
from openai.lib.live import TranscriptSegment, AsyncTranscriptGrouper


def read_audio(path: Path) -> bytes:
    with wave.open(str(path), "rb") as source:
        if (source.getnchannels(), source.getsampwidth(), source.getframerate()) != (1, 2, 24000):
            raise ValueError("Expected a mono, 16-bit, 24000 Hz PCM WAV")
        return source.readframes(source.getnframes())


async def run(path: Path, *, model: str, listen_seconds: float = 15) -> list[TranscriptSegment]:
    audio = read_audio(path)
    segments: dict[str, TranscriptSegment] = {}

    def render(segment: TranscriptSegment) -> None:
        segments[segment.id] = segment
        print(f"{segment.speaker}: {segment.text}")

    async with AsyncOpenAI() as client, AsyncTranscriptGrouper(backchannel_max_duration_ms=0) as transcript:
        transcript.on("segment.updated", render)
        async with client.live.connect(max_retries=0) as connection:
            await connection.session.start(
                session={
                    "model": model,
                    "audio": {"format": {"type": "audio/pcm", "rate": 24000}},
                    "instructions": "Respond briefly and naturally to the user.",
                }
            )
            while True:
                event = await asyncio.wait_for(connection.recv(), timeout=30)
                if event.type == "error":
                    raise OpenAIError("Live rejected session startup; inspect your model access and configuration")
                if event.type == "session.started":
                    break

            async def receive() -> None:
                async for event in connection:
                    if event.type == "error":
                        raise OpenAIError("Live returned an error while processing the audio")
                    await transcript.push(event)
                    if event.type == "session.closed":
                        return

            receiver = asyncio.create_task(receive())
            try:
                # Twenty milliseconds of signed little-endian PCM16 per message.
                chunk_bytes = 24000 * 2 // 50
                samples = audio + bytes(int(listen_seconds * 24000 * 2))
                for offset in range(0, len(samples), chunk_bytes):
                    if receiver.done():
                        await receiver
                        break
                    chunk = samples[offset : offset + chunk_bytes]
                    await connection.session.input_audio.append(audio=base64.b64encode(chunk).decode("ascii"))
                    await asyncio.sleep(len(chunk) / (24000 * 2))
                if receiver.done():
                    await receiver
                await transcript.close()
            finally:
                receiver.cancel()
                await asyncio.gather(receiver, return_exceptions=True)
    return list(segments.values())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audio", type=Path)
    parser.add_argument("--model", default=os.environ.get("OPENAI_LIVE_MODEL", "gpt-live-1"))
    args = parser.parse_args()
    asyncio.run(run(args.audio, model=args.model))
