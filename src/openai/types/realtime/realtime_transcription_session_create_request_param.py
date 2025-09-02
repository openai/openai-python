# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from typing_extensions import Literal, Required, TypedDict

__all__ = [
    "RealtimeTranscriptionSessionCreateRequestParam",
    "InputAudioNoiseReduction",
    "InputAudioTranscription",
    "TurnDetection",
]


class InputAudioNoiseReduction(TypedDict, total=False):
    type: Literal["near_field", "far_field"]
    """Type of noise reduction.

    `near_field` is for close-talking microphones such as headphones, `far_field` is
    for far-field microphones such as laptop or conference room microphones.
    """


class InputAudioTranscription(TypedDict, total=False):
    language: str
    """The language of the input audio.

    Supplying the input language in
    [ISO-639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) (e.g. `en`)
    format will improve accuracy and latency.
    """

    model: Literal["gpt-4o-transcribe", "gpt-4o-mini-transcribe", "whisper-1"]
    """
    The model to use for transcription, current options are `gpt-4o-transcribe`,
    `gpt-4o-mini-transcribe`, and `whisper-1`.
    """

    prompt: str
    """
    An optional text to guide the model's style or continue a previous audio
    segment. For `whisper-1`, the
    [prompt is a list of keywords](https://platform.openai.com/docs/guides/speech-to-text#prompting).
    For `gpt-4o-transcribe` models, the prompt is a free text string, for example
    "expect words related to technology".
    """


class TurnDetection(TypedDict, total=False):
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


class RealtimeTranscriptionSessionCreateRequestParam(TypedDict, total=False):
    model: Required[Union[str, Literal["whisper-1", "gpt-4o-transcribe", "gpt-4o-mini-transcribe"]]]
    """ID of the model to use.

    The options are `gpt-4o-transcribe`, `gpt-4o-mini-transcribe`, and `whisper-1`
    (which is powered by our open source Whisper V2 model).
    """

    type: Required[Literal["transcription"]]
    """The type of session to create.

    Always `transcription` for transcription sessions.
    """

    include: List[Literal["item.input_audio_transcription.logprobs"]]
    """The set of items to include in the transcription. Current available items are:

    - `item.input_audio_transcription.logprobs`
    """

    input_audio_format: Literal["pcm16", "g711_ulaw", "g711_alaw"]
    """The format of input audio.

    Options are `pcm16`, `g711_ulaw`, or `g711_alaw`. For `pcm16`, input audio must
    be 16-bit PCM at a 24kHz sample rate, single channel (mono), and little-endian
    byte order.
    """

    input_audio_noise_reduction: InputAudioNoiseReduction
    """Configuration for input audio noise reduction.

    This can be set to `null` to turn off. Noise reduction filters audio added to
    the input audio buffer before it is sent to VAD and the model. Filtering the
    audio can improve VAD and turn detection accuracy (reducing false positives) and
    model performance by improving perception of the input audio.
    """

    input_audio_transcription: InputAudioTranscription
    """Configuration for input audio transcription.

    The client can optionally set the language and prompt for transcription, these
    offer additional guidance to the transcription service.
    """

    turn_detection: TurnDetection
    """Configuration for turn detection.

    Can be set to `null` to turn off. Server VAD means that the model will detect
    the start and end of speech based on audio volume and respond at the end of user
    speech.
    """
