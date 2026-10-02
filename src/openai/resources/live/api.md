# Live

Types:

```python
from openai.types.live import (
    AudioFormat,
    BuiltInVoice,
    ClientConfig,
    ClientDelegation,
    ClientEvent,
    CommentaryAppendEvent,
    CommentaryAppendedEvent,
    CustomVoice,
    DataChannelConfig,
    DelegationCreatedEvent,
    Error,
    ErrorEvent,
    ForkSessionConfig,
    ForkSessionStartEvent,
    FunctionTool,
    InfoEvent,
    InitialItem,
    InputAudioAppendEvent,
    InputAudioMuteEvent,
    InputAudioMutedEvent,
    InputAudioUnmuteEvent,
    InputAudioUnmutedEvent,
    InputTranscriptDeltaEvent,
    InstructionsAppendEvent,
    InstructionsAppendedEvent,
    MediaSessionConfig,
    MediaSessionForkConfig,
    OutputAudioDeltaEvent,
    OutputTranscriptDeltaEvent,
    ResponseCreateEvent,
    ResponseEvent,
    ResponseItemCreateEvent,
    ResponsesDelegationConfig,
    ResponsesDelegationUpdateConfig,
    ServerEvent,
    ServerEventSelector,
    SessionCloseEvent,
    SessionClosedEvent,
    SessionConfig,
    SessionResource,
    SessionStartEvent,
    SessionStartedEvent,
    SessionUpdateConfig,
    SessionUpdateEvent,
    SessionUpdatedEvent,
    SessionUsage,
    SessionUsageUpdatedEvent,
    ThinkingAppendEvent,
    ThinkingAppendedEvent,
    LiveCreateResponse,
)
```

Methods:

- <code title="post /live/sessions">client.live.<a href="./src/openai/resources/live/live.py">create</a>(\*\*<a href="src/openai/types/live/live_create_params.py">params</a>) -> <a href="./src/openai/types/live/live_create_response.py">LiveCreateResponse</a></code>

## Sideband

Types:

```python
from openai.types.live import ConnectClientEvent, ConnectServerEvent
```

## Forks

Types:

```python
from openai.types.live import ForkClientEvent, ForkServerEvent
```

## Sessions

Types:

```python
from openai.types.live import SessionForkResponse
```

Methods:

- <code title="post /live/sessions/{session_id}/accept">client.live.sessions.<a href="./src/openai/resources/live/sessions.py">accept</a>(session_id, \*\*<a href="src/openai/types/live/session_accept_params.py">params</a>) -> None</code>
- <code title="get /live/sessions/{session_id}/content">client.live.sessions.<a href="./src/openai/resources/live/sessions.py">download_recording</a>(session_id) -> HttpxBinaryResponseContent</code>
- <code title="post /live/sessions/{session_id}/fork">client.live.sessions.<a href="./src/openai/resources/live/sessions.py">fork</a>(session_id, \*\*<a href="src/openai/types/live/session_fork_params.py">params</a>) -> <a href="./src/openai/types/live/session_fork_response.py">SessionForkResponse</a></code>
- <code title="post /live/sessions/{session_id}/hangup">client.live.sessions.<a href="./src/openai/resources/live/sessions.py">hangup</a>(session_id) -> None</code>
- <code title="post /live/sessions/{session_id}/refer">client.live.sessions.<a href="./src/openai/resources/live/sessions.py">refer</a>(session_id, \*\*<a href="src/openai/types/live/session_refer_params.py">params</a>) -> None</code>
- <code title="post /live/sessions/{session_id}/reject">client.live.sessions.<a href="./src/openai/resources/live/sessions.py">reject</a>(session_id, \*\*<a href="src/openai/types/live/session_reject_params.py">params</a>) -> None</code>
