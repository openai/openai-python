# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel
from .realtime_transcription_session_audio_input import RealtimeTranscriptionSessionAudioInput

__all__ = ["RealtimeTranscriptionSessionAudio"]


class RealtimeTranscriptionSessionAudio(BaseModel):
    input: Optional[RealtimeTranscriptionSessionAudioInput] = None
