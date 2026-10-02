"""Replay synthetic transcript events; no API key, network or audio is required."""

from openai.lib.live import TranscriptGrouper, TranscriptSegment, TranscriptSegmentClosedEvent
from openai.types.live import ServerEvent, InputTranscriptDeltaEvent, OutputTranscriptDeltaEvent


def render(segment: TranscriptSegment) -> None:
    # Replace the bubble's complete text rather than appending this snapshot.
    print(f"{segment.id} [{segment.speaker}]: {segment.text}")


def finalize(event: TranscriptSegmentClosedEvent) -> None:
    print(f"{event.segment.id} closed: {event.reason}")


def main() -> None:
    events: list[ServerEvent] = [
        InputTranscriptDeltaEvent(
            type="session.input_transcript.delta",
            start_ms=0,
            end_ms=200,
            event_id="user-1",
            delta="Tell me",
        ),
        OutputTranscriptDeltaEvent(
            type="session.output_transcript.delta",
            start_ms=200,
            end_ms=400,
            event_id="assistant-1",
            delta="mhm",
        ),
        InputTranscriptDeltaEvent(
            type="session.input_transcript.delta",
            start_ms=800,
            end_ms=1000,
            event_id="user-2",
            delta="more",
        ),
        OutputTranscriptDeltaEvent(
            type="session.output_transcript.delta",
            start_ms=2000,
            end_ms=2400,
            event_id="assistant-2",
            delta="Here is the answer.",
        ),
    ]
    with TranscriptGrouper() as grouper:
        grouper.on("segment.updated", render)
        grouper.on("segment.closed", finalize)
        for event in events:
            grouper.push(event)


if __name__ == "__main__":
    main()
