# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Optional
from typing_extensions import Literal, Required, TypedDict

from ..._types import FileTypes
from ..audio_model import AudioModel
from .transcription_include import TranscriptionInclude
from ..audio_response_format import AudioResponseFormat

__all__ = [
    "TranscriptionCreateParamsBase",
    "TranscriptionCreateParamsNonStreaming",
    "TranscriptionCreateParamsStreaming",
]


class TranscriptionCreateParamsBase(TypedDict, total=False):
    file: Required[FileTypes]
    """
    The audio file object (not file name) to transcribe, in one of these formats:
    flac, mp3, mp4, mpeg, mpga, m4a, ogg, wav, or webm.
    """

    model: Required[Union[str, AudioModel]]
    """ID of the model to use.

    The options are `gpt-4o-transcribe`, `gpt-4o-mini-transcribe`, and `whisper-1`
    (which is powered by our open source Whisper V2 model).
    """

    include: List[TranscriptionInclude]
    """Additional information to include in the transcription response.

    `logprobs` will return the log probabilities of the tokens in the response to
    understand the model's confidence in the transcription. `logprobs` only works
    with response_format set to `json` and only with the models `gpt-4o-transcribe`
    and `gpt-4o-mini-transcribe`.
    """

    language: str
    """The language of the input audio.

    Supplying the input language in
    [ISO-639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) (e.g. `en`)
    format will improve accuracy and latency.
    """

    prompt: str
    """An optional text to guide the model's style or continue a previous audio
    segment.

    The [prompt](https://platform.openai.com/docs/guides/speech-to-text#prompting)
    should match the audio language.
    """

    response_format: AudioResponseFormat
    """
    The format of the output, in one of these options: `json`, `text`, `srt`,
    `verbose_json`, or `vtt`. For `gpt-4o-transcribe` and `gpt-4o-mini-transcribe`,
    the only supported format is `json`.
    """

    temperature: float
    """The sampling temperature, between 0 and 1.

    Higher values like 0.8 will make the output more random, while lower values like
    0.2 will make it more focused and deterministic. If set to 0, the model will use
    [log probability](https://en.wikipedia.org/wiki/Log_probability) to
    automatically increase the temperature until certain thresholds are hit.
    """

    timestamp_granularities: List[Literal["word", "segment"]]
    """The timestamp granularities to populate for this transcription.

    `response_format` must be set `verbose_json` to use timestamp granularities.
    Either or both of these options are supported: `word`, or `segment`. Note: There
    is no additional latency for segment timestamps, but generating word timestamps
    incurs additional latency.
    """


class TranscriptionCreateParamsNonStreaming(TranscriptionCreateParamsBase, total=False):
    stream: Optional[Literal[False]]
    """
    If set to true, the model response data will be streamed to the client as it is
    generated using
    [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format).
    See the
    [Streaming section of the Speech-to-Text guide](https://platform.openai.com/docs/guides/speech-to-text?lang=curl#streaming-transcriptions)
    for more information.

    Note: Streaming is not supported for the `whisper-1` model and will be ignored.
    """


class TranscriptionCreateParamsStreaming(TranscriptionCreateParamsBase):
    stream: Required[Literal[True]]
    """
    If set to true, the model response data will be streamed to the client as it is
    generated using
    [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format).
    See the
    [Streaming section of the Speech-to-Text guide](https://platform.openai.com/docs/guides/speech-to-text?lang=curl#streaming-transcriptions)
    for more information.

    Note: Streaming is not supported for the `whisper-1` model and will be ignored.
    """


TranscriptionCreateParams = Union[TranscriptionCreateParamsNonStreaming, TranscriptionCreateParamsStreaming]
