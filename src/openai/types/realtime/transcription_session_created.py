# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel

__all__ = [
    "TranscriptionSessionCreated",
    "Session",
    "SessionAudio",
    "SessionAudioInput",
    "SessionAudioInputNoiseReduction",
    "SessionAudioInputTranscription",
    "SessionAudioInputTurnDetection",
]


class SessionAudioInputNoiseReduction(BaseModel):
    type: Optional[Literal["near_field", "far_field"]] = None


class SessionAudioInputTranscription(BaseModel):
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


class SessionAudioInputTurnDetection(BaseModel):
    prefix_padding_ms: Optional[int] = None

    silence_duration_ms: Optional[int] = None

    threshold: Optional[float] = None

    type: Optional[str] = None
    """Type of turn detection, only `server_vad` is currently supported."""


class SessionAudioInput(BaseModel):
    format: Optional[str] = None
    """The format of input audio. Options are `pcm16`, `g711_ulaw`, or `g711_alaw`."""

    noise_reduction: Optional[SessionAudioInputNoiseReduction] = None
    """Configuration for input audio noise reduction."""

    transcription: Optional[SessionAudioInputTranscription] = None
    """Configuration of the transcription model."""

    turn_detection: Optional[SessionAudioInputTurnDetection] = None
    """Configuration for turn detection."""


class SessionAudio(BaseModel):
    input: Optional[SessionAudioInput] = None


class Session(BaseModel):
    id: Optional[str] = None
    """Unique identifier for the session that looks like `sess_1234567890abcdef`."""

    audio: Optional[SessionAudio] = None
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


class TranscriptionSessionCreated(BaseModel):
    event_id: str
    """The unique ID of the server event."""

    session: Session
    """A Realtime transcription session configuration object."""

    type: Literal["transcription_session.created"]
    """The event type, must be `transcription_session.created`."""
