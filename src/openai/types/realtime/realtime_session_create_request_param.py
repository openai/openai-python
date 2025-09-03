# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Optional
from typing_extensions import Literal, Required, TypedDict

from .realtime_truncation_param import RealtimeTruncationParam
from .realtime_audio_config_param import RealtimeAudioConfigParam
from .realtime_tools_config_param import RealtimeToolsConfigParam
from .realtime_tracing_config_param import RealtimeTracingConfigParam
from ..responses.response_prompt_param import ResponsePromptParam
from .realtime_tool_choice_config_param import RealtimeToolChoiceConfigParam
from .realtime_client_secret_config_param import RealtimeClientSecretConfigParam

__all__ = ["RealtimeSessionCreateRequestParam"]


class RealtimeSessionCreateRequestParam(TypedDict, total=False):
    model: Required[
        Union[
            str,
            Literal[
                "gpt-realtime",
                "gpt-realtime-2025-08-28",
                "gpt-4o-realtime",
                "gpt-4o-mini-realtime",
                "gpt-4o-realtime-preview",
                "gpt-4o-realtime-preview-2024-10-01",
                "gpt-4o-realtime-preview-2024-12-17",
                "gpt-4o-realtime-preview-2025-06-03",
                "gpt-4o-mini-realtime-preview",
                "gpt-4o-mini-realtime-preview-2024-12-17",
            ],
        ]
    ]
    """The Realtime model used for this session."""

    type: Required[Literal["realtime"]]
    """The type of session to create. Always `realtime` for the Realtime API."""

    audio: RealtimeAudioConfigParam
    """Configuration for input and output audio."""

    client_secret: RealtimeClientSecretConfigParam
    """Configuration options for the generated client secret."""

    include: List[Literal["item.input_audio_transcription.logprobs"]]
    """Additional fields to include in server outputs.

    - `item.input_audio_transcription.logprobs`: Include logprobs for input audio
      transcription.
    """

    instructions: str
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

    max_output_tokens: Union[int, Literal["inf"]]
    """
    Maximum number of output tokens for a single assistant response, inclusive of
    tool calls. Provide an integer between 1 and 4096 to limit output tokens, or
    `inf` for the maximum available tokens for a given model. Defaults to `inf`.
    """

    output_modalities: List[Literal["text", "audio"]]
    """The set of modalities the model can respond with.

    To disable audio, set this to ["text"].
    """

    prompt: Optional[ResponsePromptParam]
    """Reference to a prompt template and its variables.

    [Learn more](https://platform.openai.com/docs/guides/text?api-mode=responses#reusable-prompts).
    """

    temperature: float
    """Sampling temperature for the model, limited to [0.6, 1.2].

    For audio models a temperature of 0.8 is highly recommended for best
    performance.
    """

    tool_choice: RealtimeToolChoiceConfigParam
    """How the model chooses tools.

    Provide one of the string modes or force a specific function/MCP tool.
    """

    tools: RealtimeToolsConfigParam
    """Tools available to the model."""

    tracing: Optional[RealtimeTracingConfigParam]
    """Configuration options for tracing.

    Set to null to disable tracing. Once tracing is enabled for a session, the
    configuration cannot be modified.

    `auto` will create a trace for the session with default values for the workflow
    name, group id, and metadata.
    """

    truncation: RealtimeTruncationParam
    """
    Controls how the realtime conversation is truncated prior to model inference.
    The default is `auto`. When set to `retention_ratio`, the server retains a
    fraction of the conversation tokens prior to the instructions.
    """
