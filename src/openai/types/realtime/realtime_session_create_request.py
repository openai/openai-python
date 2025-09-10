# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .realtime_truncation import RealtimeTruncation
from .realtime_audio_config import RealtimeAudioConfig
from .realtime_tools_config import RealtimeToolsConfig
from .realtime_tracing_config import RealtimeTracingConfig
from ..responses.response_prompt import ResponsePrompt
from .realtime_tool_choice_config import RealtimeToolChoiceConfig

__all__ = ["RealtimeSessionCreateRequest"]


class RealtimeSessionCreateRequest(BaseModel):
    type: Literal["realtime"]
    """The type of session to create. Always `realtime` for the Realtime API."""

    audio: Optional[RealtimeAudioConfig] = None
    """Configuration for input and output audio."""

    include: Optional[List[Literal["item.input_audio_transcription.logprobs"]]] = None
    """Additional fields to include in server outputs.

    `item.input_audio_transcription.logprobs`: Include logprobs for input audio
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

    model: Union[
        str,
        Literal[
            "gpt-realtime",
            "gpt-realtime-2025-08-28",
            "gpt-4o-realtime-preview",
            "gpt-4o-realtime-preview-2024-10-01",
            "gpt-4o-realtime-preview-2024-12-17",
            "gpt-4o-realtime-preview-2025-06-03",
            "gpt-4o-mini-realtime-preview",
            "gpt-4o-mini-realtime-preview-2024-12-17",
        ],
        None,
    ] = None
    """The Realtime model used for this session."""

    output_modalities: Optional[List[Literal["text", "audio"]]] = None
    """The set of modalities the model can respond with.

    It defaults to `["audio"]`, indicating that the model will respond with audio
    plus a transcript. `["text"]` can be used to make the model respond with text
    only. It is not possible to request both `text` and `audio` at the same time.
    """

    prompt: Optional[ResponsePrompt] = None
    """Reference to a prompt template and its variables.

    [Learn more](https://platform.openai.com/docs/guides/text?api-mode=responses#reusable-prompts).
    """

    tool_choice: Optional[RealtimeToolChoiceConfig] = None
    """How the model chooses tools.

    Provide one of the string modes or force a specific function/MCP tool.
    """

    tools: Optional[RealtimeToolsConfig] = None
    """Tools available to the model."""

    tracing: Optional[RealtimeTracingConfig] = None
    """
    Realtime API can write session traces to the
    [Traces Dashboard](/logs?api=traces). Set to null to disable tracing. Once
    tracing is enabled for a session, the configuration cannot be modified.

    `auto` will create a trace for the session with default values for the workflow
    name, group id, and metadata.
    """

    truncation: Optional[RealtimeTruncation] = None
    """
    Controls how the realtime conversation is truncated prior to model inference.
    The default is `auto`.
    """
