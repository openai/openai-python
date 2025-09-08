# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .realtime_transcription_session_client_secret import RealtimeTranscriptionSessionClientSecret
from .realtime_transcription_session_turn_detection import RealtimeTranscriptionSessionTurnDetection
from .realtime_transcription_session_input_audio_transcription import (
    RealtimeTranscriptionSessionInputAudioTranscription,
)

__all__ = ["RealtimeTranscriptionSessionCreateResponse"]


class RealtimeTranscriptionSessionCreateResponse(BaseModel):
    client_secret: RealtimeTranscriptionSessionClientSecret
    """Ephemeral key returned by the API.

    Only present when the session is created on the server via REST API.
    """

    input_audio_format: Optional[str] = None
    """The format of input audio. Options are `pcm16`, `g711_ulaw`, or `g711_alaw`."""

    input_audio_transcription: Optional[RealtimeTranscriptionSessionInputAudioTranscription] = None
    """Configuration of the transcription model."""

    modalities: Optional[List[Literal["text", "audio"]]] = None
    """The set of modalities the model can respond with.

    To disable audio, set this to ["text"].
    """

    turn_detection: Optional[RealtimeTranscriptionSessionTurnDetection] = None
    """Configuration for turn detection.

    Can be set to `null` to turn off. Server VAD means that the model will detect
    the start and end of speech based on audio volume and respond at the end of user
    speech.
    """
