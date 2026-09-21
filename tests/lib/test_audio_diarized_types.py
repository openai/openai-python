from __future__ import annotations

from typing_extensions import assert_type

import httpx2
import pytest

from openai import AsyncOpenAI, omit
from tests.respx2 import MockRouter
from openai.types.audio import TranscriptionDiarized, TranscriptionDiarizedSegment


@pytest.mark.respx2()
async def test_async_diarized_nonstreaming_types(async_client: AsyncOpenAI, respx2_mock: MockRouter) -> None:
    route = respx2_mock.post(f"{str(async_client.base_url).rstrip('/')}/audio/transcriptions").mock(
        return_value=httpx2.Response(
            200,
            json={
                "text": "hello",
                "duration": 1.0,
                "task": "transcribe",
                "segments": [
                    {
                        "id": "segment-1",
                        "type": "transcript.text.segment",
                        "start": 0.0,
                        "end": 1.0,
                        "text": "hello",
                        "speaker": "A",
                    }
                ],
            },
        )
    )
    default = assert_type(
        await async_client.audio.transcriptions.create(
            file=b"audio", model="gpt-4o-transcribe-diarize", response_format="diarized_json"
        ),
        TranscriptionDiarized,
    )
    false = assert_type(
        await async_client.audio.transcriptions.create(
            file=b"audio", model="gpt-4o-transcribe-diarize", response_format="diarized_json", stream=False
        ),
        TranscriptionDiarized,
    )
    null = assert_type(
        await async_client.audio.transcriptions.create(
            file=b"audio", model="gpt-4o-transcribe-diarize", response_format="diarized_json", stream=None
        ),
        TranscriptionDiarized,
    )
    omitted = assert_type(
        await async_client.audio.transcriptions.create(
            file=b"audio", model="gpt-4o-transcribe-diarize", response_format="diarized_json", stream=omit
        ),
        TranscriptionDiarized,
    )
    for response in (default, false, null, omitted):
        assert isinstance(response, TranscriptionDiarized)
        assert_type(response.segments[0], TranscriptionDiarizedSegment)
        assert response.segments[0].id == "segment-1"
        assert response.segments[0].speaker == "A"
    assert route.call_count == 4
