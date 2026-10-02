# Live transcript grouping

`TranscriptGrouper` groups public Live transcript fragments into user and assistant
display segments. Its grouping policy matches the TypeScript SDK helper. It does
not infer server turns, detect speech, or track audio playback.

```python
from openai.lib.live import TranscriptGrouper

with TranscriptGrouper() as transcript:
    transcript.on("segment.updated", render_segment)
    transcript.on("segment.closed", finalize_segment)
    for event in connection:
        transcript.push(event)
```

For an asyncio Live connection, use the asynchronous wrapper. Its callbacks may
be synchronous functions or async functions; async callbacks are awaited in order.

```python
from openai.lib.live import AsyncTranscriptGrouper

async with AsyncTranscriptGrouper() as transcript:
    transcript.on("segment.updated", render_segment)
    transcript.on("segment.closed", finalize_segment)
    async for event in connection:
        await transcript.push(event)
```

Both wrappers also support `@transcript.on("segment.updated")`, `once`, and `off`.
Each update is a frozen `TranscriptSegment` containing `id`, `previous_id`,
`speaker`, `text`, `start_ms`, and `end_ms`. Replace the bubble's displayed text
with `segment.text`; each update contains the complete, append-only text, not a
delta. A closed event contains the final snapshot as `event.segment` and its local
decision as `event.reason`: `speaker_change`, `inactivity`, `timestamp_reset`,
`session_closed`, or `manual`. Closed segments never reopen.

IDs are local to the helper, not server turn/item IDs. `previous_id` links the
previous emitted segment. Transcript times remain session milliseconds from the
public events. A segment closing does not mean its audio has finished playing.

## Timing and lifecycle

Create one grouper per session and close it on disconnect. Context managers close
the grouper on exit, including on exceptions. `close()` is idempotent, flushes
buffered text according to the grouping policy, finalizes emitted segments, and
cancels timers. It never closes or reconnects the underlying transport.
`push()` after closure raises `OpenAIError`.

Only `session.input_transcript.delta`, `session.output_transcript.delta`, and `session.closed`
drive grouping. Other events are ignored. Duplicate transcript event IDs and empty
text do not restart inactivity. Malformed transcript fields raise `OpenAIError`.
Keep the raw event stream separately when a lossless transcript is required:
the default policy can suppress brief overlapping acknowledgments such as “mhm”.

Constructor options are milliseconds and preserve the TypeScript defaults:

| Option | Default |
| --- | --- |
| `min_turn_separation_ms` | 500 |
| `assistant_silence_ms` | 2000 |
| `backchannel_max_duration_ms` | 1000 |
| `backchannel_isolation_ms` | 2000 |

Set `backchannel_max_duration_ms=0` to disable acknowledgment suppression. `None`
uses the default; explicit zero is retained. Values must be finite and between
zero and 2,147,483,647. Ambiguous speaker changes settle for at most 50 ms.
Source timestamps take precedence; a monotonic local clock supplies inactivity
fallback when no more transcript events arrive. Delivery delays can affect the
projection. User segments do not close from inactivity alone.

The synchronous helper serializes callbacks but may deliver timer-triggered
callbacks on a daemon timer thread. Applications should marshal UI work to their
UI thread. Callbacks run outside its state lock and may close the grouper; callbacks
already running finish in order. Callback exceptions propagate to the calling
`push()`/`close()`, or to `threading.excepthook` for timer-triggered callbacks.

The asynchronous helper belongs to the asyncio loop where it is first used;
all callbacks run on that loop. Timer-triggered callback errors go to the loop's
exception handler. Use `await transcript.close()` or `async with` for cleanup.
Cancelling a task waiting on `push()` or `close()` does not cancel notification
delivery already in progress. Call `close()` again to await cleanup if necessary.

## Offline example

Run `python examples/live/transcript_grouper.py` in the SDK development environment.
It replays synthetic transcript events and prints segment updates without making
API calls, using an API key, or playing audio.

## Live audio examples

With `OPENAI_API_KEY` set, run `python examples/live/audio_transcript.py speech.wav`
to send a 24 kHz, 16-bit mono PCM recording through the primary WebSocket. It
waits for `session.started`, paces audio in real time, and prints grouped user and
assistant transcripts. `--model` or `OPENAI_LIVE_MODEL` selects a different model.

For browser audio, your backend can exchange the SDP with `client.live.create`
and attach `client.live.sideband.connect(session_id=result.session.id)` before
returning the SDP answer. Feed sideband events into the same transcript grouper.
