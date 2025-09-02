# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, TypeAlias

from ..._models import BaseModel

__all__ = [
    "RealtimeSessionCreateResponse",
    "Audio",
    "AudioInput",
    "AudioInputNoiseReduction",
    "AudioInputTranscription",
    "AudioInputTurnDetection",
    "AudioOutput",
    "Tool",
    "Tracing",
    "TracingTracingConfiguration",
    "TurnDetection",
]


class AudioInputNoiseReduction(BaseModel):
    type: Optional[Literal["near_field", "far_field"]] = None


class AudioInputTranscription(BaseModel):
    language: Optional[str] = None
    """The language of the input audio."""

    model: Optional[str] = None
    """The model to use for transcription."""

    prompt: Optional[str] = None
    """Optional text to guide the model's style or continue a previous audio segment."""


class AudioInputTurnDetection(BaseModel):
    prefix_padding_ms: Optional[int] = None

    silence_duration_ms: Optional[int] = None

    threshold: Optional[float] = None

    type: Optional[str] = None
    """Type of turn detection, only `server_vad` is currently supported."""


class AudioInput(BaseModel):
    format: Optional[str] = None
    """The format of input audio. Options are `pcm16`, `g711_ulaw`, or `g711_alaw`."""

    noise_reduction: Optional[AudioInputNoiseReduction] = None
    """Configuration for input audio noise reduction."""

    transcription: Optional[AudioInputTranscription] = None
    """Configuration for input audio transcription."""

    turn_detection: Optional[AudioInputTurnDetection] = None
    """Configuration for turn detection."""


class AudioOutput(BaseModel):
    format: Optional[str] = None
    """The format of output audio. Options are `pcm16`, `g711_ulaw`, or `g711_alaw`."""

    speed: Optional[float] = None

    voice: Union[
        str, Literal["alloy", "ash", "ballad", "coral", "echo", "sage", "shimmer", "verse", "marin", "cedar"], None
    ] = None


class Audio(BaseModel):
    input: Optional[AudioInput] = None

    output: Optional[AudioOutput] = None


class Tool(BaseModel):
    description: Optional[str] = None
    """
    The description of the function, including guidance on when and how to call it,
    and guidance about what to tell the user when calling (if anything).
    """

    name: Optional[str] = None
    """The name of the function."""

    parameters: Optional[object] = None
    """Parameters of the function in JSON Schema."""

    type: Optional[Literal["function"]] = None
    """The type of the tool, i.e. `function`."""


class TracingTracingConfiguration(BaseModel):
    group_id: Optional[str] = None
    """
    The group id to attach to this trace to enable filtering and grouping in the
    traces dashboard.
    """

    metadata: Optional[object] = None
    """
    The arbitrary metadata to attach to this trace to enable filtering in the traces
    dashboard.
    """

    workflow_name: Optional[str] = None
    """The name of the workflow to attach to this trace.

    This is used to name the trace in the traces dashboard.
    """


Tracing: TypeAlias = Union[Literal["auto"], TracingTracingConfiguration]


class TurnDetection(BaseModel):
    prefix_padding_ms: Optional[int] = None
    """Amount of audio to include before the VAD detected speech (in milliseconds).

    Defaults to 300ms.
    """

    silence_duration_ms: Optional[int] = None
    """Duration of silence to detect speech stop (in milliseconds).

    Defaults to 500ms. With shorter values the model will respond more quickly, but
    may jump in on short pauses from the user.
    """

    threshold: Optional[float] = None
    """Activation threshold for VAD (0.0 to 1.0), this defaults to 0.5.

    A higher threshold will require louder audio to activate the model, and thus
    might perform better in noisy environments.
    """

    type: Optional[str] = None
    """Type of turn detection, only `server_vad` is currently supported."""


class RealtimeSessionCreateResponse(BaseModel):
    id: Optional[str] = None
    """Unique identifier for the session that looks like `sess_1234567890abcdef`."""

    audio: Optional[Audio] = None
    """Configuration for input and output audio for the session."""

    expires_at: Optional[int] = None
    """Expiration timestamp for the session, in seconds since epoch."""

    include: Optional[List[Literal["item.input_audio_transcription.logprobs"]]] = None
    """Additional fields to include in server outputs.

    - `item.input_audio_transcription.logprobs`: Include logprobs for input audio
      transcription.
    """

    instructions: Optional[str] = None
    """The default system instructions (i.e.

    system message) prepended to model calls. This field allows the client to guide
    the model on desired responses. The model can be instructed on response content
    and format, (e.g. "be extremely succinct", "act friendly", "here are examples of
    good responses") and on audio behavior (e.g. "talk quickly", "inject emotion
    into your voice", "laugh frequently"). The instructions are not guaranteed to be
    followed by the model, but they provide guidance to the model on the desired
    behavior.

    Note that the server sets default instructions which will be used if this field
    is not set and are visible in the `session.created` event at the start of the
    session.
    """

    max_output_tokens: Union[int, Literal["inf"], None] = None
    """
    Maximum number of output tokens for a single assistant response, inclusive of
    tool calls. Provide an integer between 1 and 4096 to limit output tokens, or
    `inf` for the maximum available tokens for a given model. Defaults to `inf`.
    """

    model: Optional[str] = None
    """The Realtime model used for this session."""

    object: Optional[str] = None
    """The object type. Always `realtime.session`."""

    output_modalities: Optional[List[Literal["text", "audio"]]] = None
    """The set of modalities the model can respond with.

    To disable audio, set this to ["text"].
    """

    tool_choice: Optional[str] = None
    """How the model chooses tools.

    Options are `auto`, `none`, `required`, or specify a function.
    """

    tools: Optional[List[Tool]] = None
    """Tools (functions) available to the model."""

    tracing: Optional[Tracing] = None
    """Configuration options for tracing.

    Set to null to disable tracing. Once tracing is enabled for a session, the
    configuration cannot be modified.

    `auto` will create a trace for the session with default values for the workflow
    name, group id, and metadata.
    """

    turn_detection: Optional[TurnDetection] = None
    """Configuration for turn detection.

    Can be set to `null` to turn off. Server VAD means that the model will detect
    the start and end of speech based on audio volume and respond at the end of user
    speech.
    """
