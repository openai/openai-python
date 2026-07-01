import pytest

from openai._compat import parse_obj
from openai.types.realtime.response_audio_done_event import ResponseAudioDoneEvent
from openai.types.realtime.response_audio_delta_event import ResponseAudioDeltaEvent
from openai.types.realtime.response_audio_transcript_done_event import ResponseAudioTranscriptDoneEvent
from openai.types.realtime.response_audio_transcript_delta_event import ResponseAudioTranscriptDeltaEvent


@pytest.mark.parametrize(
    ("model", "event_type", "extra"),
    [
        (ResponseAudioDeltaEvent, "response.audio.delta", {"delta": "abc"}),
        (ResponseAudioDoneEvent, "response.audio.done", {}),
        (ResponseAudioTranscriptDeltaEvent, "response.audio_transcript.delta", {"delta": "hello"}),
        (ResponseAudioTranscriptDoneEvent, "response.audio_transcript.done", {"transcript": "hello"}),
    ],
)
def test_realtime_audio_event_type_literals_match_api_events(model: type, event_type: str, extra: dict) -> None:
    event = parse_obj(
        model,
        {
            "event_id": "event_1",
            "response_id": "resp_1",
            "item_id": "item_1",
            "output_index": 0,
            "content_index": 0,
            "type": event_type,
            **extra,
        },
    )
    assert event.type == event_type
