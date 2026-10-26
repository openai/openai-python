## Realtime

Types:

```python
from openai.types.beta.realtime import (
    ConversationCreatedEvent,
    ConversationItem,
    ConversationItemContent,
    ConversationItemCreateEvent,
    ConversationItemCreatedEvent,
    ConversationItemDeleteEvent,
    ConversationItemDeletedEvent,
    ConversationItemInputAudioTranscriptionCompletedEvent,
    ConversationItemInputAudioTranscriptionDeltaEvent,
    ConversationItemInputAudioTranscriptionFailedEvent,
    ConversationItemRetrieveEvent,
    ConversationItemTruncateEvent,
    ConversationItemTruncatedEvent,
    ConversationItemWithReference,
    ErrorEvent,
    InputAudioBufferAppendEvent,
    InputAudioBufferClearEvent,
    InputAudioBufferClearedEvent,
    InputAudioBufferCommitEvent,
    InputAudioBufferCommittedEvent,
    InputAudioBufferSpeechStartedEvent,
    InputAudioBufferSpeechStoppedEvent,
    RateLimitsUpdatedEvent,
    RealtimeClientEvent,
    RealtimeResponse,
    RealtimeResponseStatus,
    RealtimeResponseUsage,
    RealtimeServerEvent,
    ResponseAudioDeltaEvent,
    ResponseAudioDoneEvent,
    ResponseAudioTranscriptDeltaEvent,
    ResponseAudioTranscriptDoneEvent,
    ResponseCancelEvent,
    ResponseContentPartAddedEvent,
    ResponseContentPartDoneEvent,
    ResponseCreateEvent,
    ResponseCreatedEvent,
    ResponseDoneEvent,
    ResponseFunctionCallArgumentsDeltaEvent,
    ResponseFunctionCallArgumentsDoneEvent,
    ResponseOutputItemAddedEvent,
    ResponseOutputItemDoneEvent,
    ResponseTextDeltaEvent,
    ResponseTextDoneEvent,
    SessionCreatedEvent,
    SessionUpdateEvent,
    SessionUpdatedEvent,
    TranscriptionSessionUpdate,
    TranscriptionSessionUpdatedEvent,
)
```

### Sessions

Types:

```python
from openai.types.beta.realtime import Session, SessionCreateResponse
```

Methods:

- <code title="post /realtime/sessions">client.beta.realtime.sessions.<a href="../src/openai/resources/beta/realtime/sessions.py">create</a>(\*\*<a href="../src/openai/types/beta/realtime/session_create_params.py">params</a>) -> <a href="../src/openai/types/beta/realtime/session_create_response.py">SessionCreateResponse</a></code>

### TranscriptionSessions

Types:

```python
from openai.types.beta.realtime import TranscriptionSession
```

Methods:

- <code title="post /realtime/transcription_sessions">client.beta.realtime.transcription_sessions.<a href="../src/openai/resources/beta/realtime/transcription_sessions.py">create</a>(\*\*<a href="../src/openai/types/beta/realtime/transcription_session_create_params.py">params</a>) -> <a href="../src/openai/types/beta/realtime/transcription_session.py">TranscriptionSession</a></code>
