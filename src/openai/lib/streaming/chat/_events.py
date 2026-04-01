from typing import List, Union, Generic, Optional
from typing_extensions import Literal

from ._types import ParsedChatCompletionSnapshot
from ...._models import BaseModel, GenericModel
from ..._parsing import ResponseFormatT
from ....types.chat import ChatCompletionChunk, ChatCompletionTokenLogprob


class ChunkEvent(BaseModel):
    """Emitted for every raw chunk received from the Chat Completions streaming API."""

    type: Literal["chunk"]

    chunk: ChatCompletionChunk

    snapshot: ParsedChatCompletionSnapshot


class ContentDeltaEvent(BaseModel):
    """This event is yielded for every chunk with `choice.delta.content` data."""

    type: Literal["content.delta"]

    delta: str

    snapshot: str

    parsed: Optional[object] = None


class ContentDoneEvent(GenericModel, Generic[ResponseFormatT]):
    """Emitted when the full content string for a choice is complete."""

    type: Literal["content.done"]

    content: str

    parsed: Optional[ResponseFormatT] = None


class RefusalDeltaEvent(BaseModel):
    """Emitted when a new refusal text delta is received."""

    type: Literal["refusal.delta"]

    delta: str

    snapshot: str


class RefusalDoneEvent(BaseModel):
    """Emitted when the full refusal string for a choice is complete."""

    type: Literal["refusal.done"]

    refusal: str


class FunctionToolCallArgumentsDeltaEvent(BaseModel):
    """Emitted when a new function tool call arguments delta is received."""

    type: Literal["tool_calls.function.arguments.delta"]

    name: str

    index: int

    arguments: str
    """Accumulated raw JSON string"""

    parsed_arguments: object
    """The parsed arguments so far"""

    arguments_delta: str
    """The JSON string delta"""


class FunctionToolCallArgumentsDoneEvent(BaseModel):
    """Emitted when the function tool call arguments string is complete."""

    type: Literal["tool_calls.function.arguments.done"]

    name: str

    index: int

    arguments: str
    """Accumulated raw JSON string"""

    parsed_arguments: object
    """The parsed arguments"""


class LogprobsContentDeltaEvent(BaseModel):
    """Emitted when new content logprob tokens are received."""

    type: Literal["logprobs.content.delta"]

    content: List[ChatCompletionTokenLogprob]

    snapshot: List[ChatCompletionTokenLogprob]


class LogprobsContentDoneEvent(BaseModel):
    """Emitted when the full content logprobs list is complete."""

    type: Literal["logprobs.content.done"]

    content: List[ChatCompletionTokenLogprob]


class LogprobsRefusalDeltaEvent(BaseModel):
    """Emitted when new refusal logprob tokens are received."""

    type: Literal["logprobs.refusal.delta"]

    refusal: List[ChatCompletionTokenLogprob]

    snapshot: List[ChatCompletionTokenLogprob]


class LogprobsRefusalDoneEvent(BaseModel):
    """Emitted when the full refusal logprobs list is complete."""

    type: Literal["logprobs.refusal.done"]

    refusal: List[ChatCompletionTokenLogprob]


ChatCompletionStreamEvent = Union[
    ChunkEvent,
    ContentDeltaEvent,
    ContentDoneEvent[ResponseFormatT],
    RefusalDeltaEvent,
    RefusalDoneEvent,
    FunctionToolCallArgumentsDeltaEvent,
    FunctionToolCallArgumentsDoneEvent,
    LogprobsContentDeltaEvent,
    LogprobsContentDoneEvent,
    LogprobsRefusalDeltaEvent,
    LogprobsRefusalDoneEvent,
]
