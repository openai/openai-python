#!/usr/bin/env rye run python

import time
from pathlib import Path

from openai import OpenAI

# gets OPENAI_API_KEY from your environment variables
openai = OpenAI()

speech_file_path = Path(__file__).parent / "speech.mp3"


def main() -> None:
    stream_to_speakers()

    # Create text-to-speech audio file
    with openai.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="alloy",
        input="the quick brown fox jumped over the lazy dogs",
    ) as response:
        response.stream_to_file(speech_file_path)

    # Create transcription from audio file
    transcription = openai.audio.transcriptions.create(
        model="whisper-1",
        file=speech_file_path,
    )
    print(transcription.text)

    # Create translation from audio file
    translation = openai.audio.translations.create(
        model="whisper-1",
        file=speech_file_path,
    )
    print(translation.text)


def stream_to_speakers() -> None:
    import pyaudio

    player_stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1, rate=24000, output=True)

    start_time = time.time()

    with openai.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="alloy",
        response_format="pcm",  # similar to WAV, but without a header chunk at the start.
        input="""I see skies of blue and clouds of white
                The bright blessed days, the dark sacred nights
                And I think to myself
                What a wonderful world""",
    ) as response:
        print(f"Time to first byte: {int((time.time() - start_time) * 1000)}ms")
        for chunk in response.iter_bytes(chunk_size=1024):
            player_stream.write(chunk)

    print(f"Done in {int((time.time() - start_time) * 1000)}ms.")


if __name__ == "__main__":
    main()
