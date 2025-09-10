# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Required, TypedDict

from .noise_reduction_type import NoiseReductionType
from .audio_transcription_param import AudioTranscriptionParam

__all__ = ["TranscriptionSessionUpdateParam", "Session", "SessionInputAudioNoiseReduction", "SessionTurnDetection"]


class SessionInputAudioNoiseReduction(TypedDict, total=False):
    type: NoiseReductionType
    """Type of noise reduction.

    `near_field` is for close-talking microphones such as headphones, `far_field` is
    for far-field microphones such as laptop or conference room microphones.
    """


class SessionTurnDetection(TypedDict, total=False):
    prefix_padding_ms: int
    """Amount of audio to include before the VAD detected speech (in milliseconds).

    Defaults to 300ms.
    """

    silence_duration_ms: int
    """Duration of silence to detect speech stop (in milliseconds).

    Defaults to 500ms. With shorter values the model will respond more quickly, but
    may jump in on short pauses from the user.
    """

    threshold: float
    """Activation threshold for VAD (0.0 to 1.0), this defaults to 0.5.

    A higher threshold will require louder audio to activate the model, and thus
    might perform better in noisy environments.
    """

    type: Literal["server_vad"]
    """Type of turn detection.

    Only `server_vad` is currently supported for transcription sessions.
    """


class Session(TypedDict, total=False):
    include: List[Literal["item.input_audio_transcription.logprobs"]]
    """The set of items to include in the transcription.

    Current available items are: `item.input_audio_transcription.logprobs`
    """

    input_audio_format: Literal["pcm16", "g711_ulaw", "g711_alaw"]
    """The format of input audio.

    Options are `pcm16`, `g711_ulaw`, or `g711_alaw`. For `pcm16`, input audio must
    be 16-bit PCM at a 24kHz sample rate, single channel (mono), and little-endian
    byte order.
    """

    input_audio_noise_reduction: SessionInputAudioNoiseReduction
    """Configuration for input audio noise reduction.

    This can be set to `null` to turn off. Noise reduction filters audio added to
    the input audio buffer before it is sent to VAD and the model. Filtering the
    audio can improve VAD and turn detection accuracy (reducing false positives) and
    model performance by improving perception of the input audio.
    """

    input_audio_transcription: AudioTranscriptionParam
    """Configuration for input audio transcription.

    The client can optionally set the language and prompt for transcription, these
    offer additional guidance to the transcription service.
    """

    turn_detection: SessionTurnDetection
    """Configuration for turn detection.

    Can be set to `null` to turn off. Server VAD means that the model will detect
    the start and end of speech based on audio volume and respond at the end of user
    speech.
    """


class TranscriptionSessionUpdateParam(TypedDict, total=False):
    session: Required[Session]
    """Realtime transcription session object configuration."""

    type: Required[Literal["transcription_session.update"]]
    """The event type, must be `transcription_session.update`."""

    event_id: str
    """Optional client-generated ID used to identify this event."""
