# Realtime Translation

Install `openai[realtime]` to use Translation over WebSocket. The
`client.realtime.translations.connect()` method provides the typed connection.
`TranslationSession` adds finish and cleanup rules.

```python
import base64

from openai import OpenAI
from openai.lib.realtime_translation import TranslationSession

with OpenAI() as client:
    with TranslationSession(
        client.realtime.translations, model="gpt-realtime-translate"
    ) as connection:
        connection.send({
            "type": "session.input_audio_buffer.append",
            "audio": base64.b64encode(pcm_audio).decode("ascii"),
        })
        connection.send({"type": "session.close"})
        while True:
            event = connection.recv()
            if event.type == "session.output_transcript.delta":
                print(event.delta, end="", flush=True)
            if event.type == "session.closed":
                break
```

Here, `pcm_audio` contains audio bytes in the format accepted by the session.
For async applications, use `AsyncOpenAI`, `AsyncTranslationSession`,
`async with`, and await `send()` and `recv()`.

Sending `session.close` once stops further input. Continue receiving until
`session.closed` to retain trailing audio and text. Repeated finish commands
do nothing; new input after finish raises `OpenAIError`. A socket closing before
`session.closed` is an error, not successful completion. The helper does not
reconnect or replay commands. It closes its connection when the context exits,
including when receiving is cancelled or application code raises an exception.

Use one receiver per connection. Server error events and unknown future events
remain visible to the caller. `extra_query`, `extra_headers`, and
`websocket_connection_options` configure the request and connection.
The helper rejects unsupported providers and `intent` query parameters before
opening a connection.
