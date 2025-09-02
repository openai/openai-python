# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, TypeAlias

from ..._models import BaseModel
from .realtime_session_create_response import RealtimeSessionCreateResponse

__all__ = [
    "ClientSecretCreateResponse",
    "Session",
    "SessionRealtimeTranscriptionSessionCreateResponse",
    "SessionRealtimeTranscriptionSessionCreateResponseAudio",
    "SessionRealtimeTranscriptionSessionCreateResponseAudioInput",
    "SessionRealtimeTranscriptionSessionCreateResponseAudioInputNoiseReduction",
    "SessionRealtimeTranscriptionSessionCreateResponseAudioInputTranscription",
    "SessionRealtimeTranscriptionSessionCreateResponseAudioInputTurnDetection",
]


class SessionRealtimeTranscriptionSessionCreateResponseAudioInputNoiseReduction(BaseModel):
    type: Optional[Literal["near_field", "far_field"]] = None


class SessionRealtimeTranscriptionSessionCreateResponseAudioInputTranscription(BaseModel):
    language: Optional[str] = None
    """The language of the input audio.

    Supplying the input language in
    [ISO-639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) (e.g. `en`)
    format will improve accuracy and latency.
    """

    model: Optional[Literal["gpt-4o-transcribe", "gpt-4o-mini-transcribe", "whisper-1"]] = None
    """The model to use for transcription.

    Can be `gpt-4o-transcribe`, `gpt-4o-mini-transcribe`, or `whisper-1`.
    """

    prompt: Optional[str] = None
    """An optional text to guide the model's style or continue a previous audio
    segment.

    The [prompt](https://platform.openai.com/docs/guides/speech-to-text#prompting)
    should match the audio language.
    """


class SessionRealtimeTranscriptionSessionCreateResponseAudioInputTurnDetection(BaseModel):
    prefix_padding_ms: Optional[int] = None

    silence_duration_ms: Optional[int] = None

    threshold: Optional[float] = None

    type: Optional[str] = None
    """Type of turn detection, only `server_vad` is currently supported."""


class SessionRealtimeTranscriptionSessionCreateResponseAudioInput(BaseModel):
    format: Optional[str] = None
    """The format of input audio. Options are `pcm16`, `g711_ulaw`, or `g711_alaw`."""

    noise_reduction: Optional[SessionRealtimeTranscriptionSessionCreateResponseAudioInputNoiseReduction] = None
    """Configuration for input audio noise reduction."""

    transcription: Optional[SessionRealtimeTranscriptionSessionCreateResponseAudioInputTranscription] = None
    """Configuration of the transcription model."""

    turn_detection: Optional[SessionRealtimeTranscriptionSessionCreateResponseAudioInputTurnDetection] = None
    """Configuration for turn detection."""


class SessionRealtimeTranscriptionSessionCreateResponseAudio(BaseModel):
    input: Optional[SessionRealtimeTranscriptionSessionCreateResponseAudioInput] = None


class SessionRealtimeTranscriptionSessionCreateResponse(BaseModel):
    id: Optional[str] = None
    """Unique identifier for the session that looks like `sess_1234567890abcdef`."""

    audio: Optional[SessionRealtimeTranscriptionSessionCreateResponseAudio] = None
    """Configuration for input audio for the session."""

    expires_at: Optional[int] = None
    """Expiration timestamp for the session, in seconds since epoch."""

    include: Optional[List[Literal["item.input_audio_transcription.logprobs"]]] = None
    """Additional fields to include in server outputs.

    - `item.input_audio_transcription.logprobs`: Include logprobs for input audio
      transcription.
    """

    object: Optional[str] = None
    """The object type. Always `realtime.transcription_session`."""


Session: TypeAlias = Union[RealtimeSessionCreateResponse, SessionRealtimeTranscriptionSessionCreateResponse]


class ClientSecretCreateResponse(BaseModel):
    expires_at: int
    """Expiration timestamp for the client secret, in seconds since epoch."""

    session: Session
    """The session configuration for either a realtime or transcription session."""

    value: str
    """The generated client secret value."""
