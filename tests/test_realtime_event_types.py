from __future__ import annotations

from typing import Any

import pytest

from openai._compat import parse_obj
from openai._models import validate_type
from openai.types.realtime import RealtimeServerEvent
from openai.types.realtime.response_audio_transcript_done_event import ResponseAudioTranscriptDoneEvent
from openai.types.realtime.response_audio_transcript_delta_event import ResponseAudioTranscriptDeltaEvent


@pytest.mark.parametrize(
    ("event_type", "event_cls", "extra"),
    [
        ("response.audio_transcript.delta", ResponseAudioTranscriptDeltaEvent, {"delta": "hel"}),
        ("response.audio_transcript.done", ResponseAudioTranscriptDoneEvent, {"transcript": "hello"}),
    ],
)
def test_response_audio_transcript_events_accept_webrtc_event_types(
    event_type: str,
    event_cls: type[ResponseAudioTranscriptDeltaEvent] | type[ResponseAudioTranscriptDoneEvent],
    extra: dict[str, str],
) -> None:
    payload = _audio_transcript_event_payload(event_type, extra)

    event = parse_obj(event_cls, payload)

    assert event.type == event_type


@pytest.mark.parametrize(
    ("event_type", "event_cls", "extra"),
    [
        ("response.audio_transcript.delta", ResponseAudioTranscriptDeltaEvent, {"delta": "hel"}),
        ("response.audio_transcript.done", ResponseAudioTranscriptDoneEvent, {"transcript": "hello"}),
    ],
)
def test_realtime_server_event_discriminates_webrtc_audio_transcript_event_types(
    event_type: str,
    event_cls: type[ResponseAudioTranscriptDeltaEvent] | type[ResponseAudioTranscriptDoneEvent],
    extra: dict[str, str],
) -> None:
    payload = _audio_transcript_event_payload(event_type, extra)

    event = validate_type(type_=RealtimeServerEvent, value=payload)

    assert isinstance(event, event_cls)
    assert event.type == event_type


def _audio_transcript_event_payload(event_type: str, extra: dict[str, str]) -> dict[str, Any]:
    return {
        "content_index": 0,
        "event_id": "event_123",
        "item_id": "item_123",
        "output_index": 0,
        "response_id": "resp_123",
        "type": event_type,
        **extra,
    }
