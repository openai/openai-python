# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Dict, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .beta_response_failed_event import BetaResponseFailedEvent
from .beta_response_queued_event import BetaResponseQueuedEvent
from .beta_response_created_event import BetaResponseCreatedEvent
from .beta_response_completed_event import BetaResponseCompletedEvent
from .beta_response_text_done_event import BetaResponseTextDoneEvent
from .beta_response_audio_done_event import BetaResponseAudioDoneEvent
from .beta_response_incomplete_event import BetaResponseIncompleteEvent
from .beta_response_text_delta_event import BetaResponseTextDeltaEvent
from .beta_response_audio_delta_event import BetaResponseAudioDeltaEvent
from .beta_response_in_progress_event import BetaResponseInProgressEvent
from .beta_response_refusal_done_event import BetaResponseRefusalDoneEvent
from .beta_response_inject_failed_event import BetaResponseInjectFailedEvent
from .beta_response_refusal_delta_event import BetaResponseRefusalDeltaEvent
from .beta_response_inject_created_event import BetaResponseInjectCreatedEvent
from .beta_response_mcp_call_failed_event import BetaResponseMcpCallFailedEvent
from .beta_response_output_item_done_event import BetaResponseOutputItemDoneEvent
from .beta_response_content_part_done_event import BetaResponseContentPartDoneEvent
from .beta_response_output_item_added_event import BetaResponseOutputItemAddedEvent
from .beta_response_content_part_added_event import BetaResponseContentPartAddedEvent
from .beta_response_mcp_call_completed_event import BetaResponseMcpCallCompletedEvent
from .beta_response_reasoning_text_done_event import BetaResponseReasoningTextDoneEvent
from .beta_response_mcp_call_in_progress_event import BetaResponseMcpCallInProgressEvent
from .beta_response_reasoning_text_delta_event import BetaResponseReasoningTextDeltaEvent
from .beta_response_audio_transcript_done_event import BetaResponseAudioTranscriptDoneEvent
from .beta_response_mcp_list_tools_failed_event import BetaResponseMcpListToolsFailedEvent
from .beta_response_audio_transcript_delta_event import BetaResponseAudioTranscriptDeltaEvent
from .beta_response_mcp_call_arguments_done_event import BetaResponseMcpCallArgumentsDoneEvent
from .beta_response_image_gen_call_completed_event import BetaResponseImageGenCallCompletedEvent
from .beta_response_mcp_call_arguments_delta_event import BetaResponseMcpCallArgumentsDeltaEvent
from .beta_response_mcp_list_tools_completed_event import BetaResponseMcpListToolsCompletedEvent
from .beta_response_image_gen_call_generating_event import BetaResponseImageGenCallGeneratingEvent
from .beta_response_web_search_call_completed_event import BetaResponseWebSearchCallCompletedEvent
from .beta_response_web_search_call_searching_event import BetaResponseWebSearchCallSearchingEvent
from .beta_response_file_search_call_completed_event import BetaResponseFileSearchCallCompletedEvent
from .beta_response_file_search_call_searching_event import BetaResponseFileSearchCallSearchingEvent
from .beta_response_image_gen_call_in_progress_event import BetaResponseImageGenCallInProgressEvent
from .beta_response_mcp_list_tools_in_progress_event import BetaResponseMcpListToolsInProgressEvent
from .beta_response_custom_tool_call_input_done_event import BetaResponseCustomToolCallInputDoneEvent
from .beta_response_reasoning_summary_part_done_event import BetaResponseReasoningSummaryPartDoneEvent
from .beta_response_reasoning_summary_text_done_event import BetaResponseReasoningSummaryTextDoneEvent
from .beta_response_web_search_call_in_progress_event import BetaResponseWebSearchCallInProgressEvent
from .beta_response_custom_tool_call_input_delta_event import BetaResponseCustomToolCallInputDeltaEvent
from .beta_response_file_search_call_in_progress_event import BetaResponseFileSearchCallInProgressEvent
from .beta_response_function_call_arguments_done_event import BetaResponseFunctionCallArgumentsDoneEvent
from .beta_response_image_gen_call_partial_image_event import BetaResponseImageGenCallPartialImageEvent
from .beta_response_output_text_annotation_added_event import BetaResponseOutputTextAnnotationAddedEvent
from .beta_response_reasoning_summary_part_added_event import BetaResponseReasoningSummaryPartAddedEvent
from .beta_response_reasoning_summary_text_delta_event import BetaResponseReasoningSummaryTextDeltaEvent
from .beta_response_function_call_arguments_delta_event import BetaResponseFunctionCallArgumentsDeltaEvent
from .beta_response_code_interpreter_call_code_done_event import BetaResponseCodeInterpreterCallCodeDoneEvent
from .beta_response_code_interpreter_call_completed_event import BetaResponseCodeInterpreterCallCompletedEvent
from .beta_response_code_interpreter_call_code_delta_event import BetaResponseCodeInterpreterCallCodeDeltaEvent
from .beta_response_code_interpreter_call_in_progress_event import BetaResponseCodeInterpreterCallInProgressEvent
from .beta_response_code_interpreter_call_interpreting_event import BetaResponseCodeInterpreterCallInterpretingEvent

__all__ = [
    "BetaResponsesServerEvent",
    "BetaResponseAudioWsDelta",
    "BetaResponseAudioWsDone",
    "BetaResponseAudioTranscriptWsDelta",
    "BetaResponseAudioTranscriptWsDone",
    "BetaResponseCodeInterpreterCallCodeWsDelta",
    "BetaResponseCodeInterpreterCallCodeWsDone",
    "BetaResponseCodeInterpreterCallWsCompleted",
    "BetaResponseCodeInterpreterCallInWsProgress",
    "BetaResponseCodeInterpreterCallWsInterpreting",
    "BetaResponseWsCompleted",
    "BetaResponseContentPartWsAdded",
    "BetaResponseContentPartWsDone",
    "BetaResponseWsCreated",
    "BetaResponseFileSearchCallWsCompleted",
    "BetaResponseFileSearchCallInWsProgress",
    "BetaResponseFileSearchCallWsSearching",
    "BetaResponseFunctionCallArgumentsWsDelta",
    "BetaResponseFunctionCallArgumentsWsDone",
    "BetaResponseInWsProgress",
    "BetaResponseWsFailed",
    "BetaResponseWsIncomplete",
    "BetaResponseOutputItemWsAdded",
    "BetaResponseOutputItemWsDone",
    "BetaResponseReasoningSummaryPartWsAdded",
    "BetaResponseReasoningSummaryPartWsDone",
    "BetaResponseReasoningSummaryTextWsDelta",
    "BetaResponseReasoningSummaryTextWsDone",
    "BetaResponseReasoningTextWsDelta",
    "BetaResponseReasoningTextWsDone",
    "BetaResponseRefusalWsDelta",
    "BetaResponseRefusalWsDone",
    "BetaResponseTextWsDelta",
    "BetaResponseTextWsDone",
    "BetaResponseWebSearchCallWsCompleted",
    "BetaResponseWebSearchCallInWsProgress",
    "BetaResponseWebSearchCallWsSearching",
    "BetaResponseImageGenCallWsCompleted",
    "BetaResponseImageGenCallWsGenerating",
    "BetaResponseImageGenCallInWsProgress",
    "BetaResponseImageGenCallPartialWsImage",
    "BetaResponseMcpCallArgumentsWsDelta",
    "BetaResponseMcpCallArgumentsWsDone",
    "BetaResponseMcpCallWsCompleted",
    "BetaResponseMcpCallWsFailed",
    "BetaResponseMcpCallInWsProgress",
    "BetaResponseMcpListToolsWsCompleted",
    "BetaResponseMcpListToolsWsFailed",
    "BetaResponseMcpListToolsInWsProgress",
    "BetaResponseOutputTextAnnotationWsAdded",
    "BetaResponseWsQueued",
    "BetaResponseCustomToolCallInputWsDelta",
    "BetaResponseCustomToolCallInputWsDone",
    "BetaResponseWsError",
    "BetaResponseWsErrorError",
    "BetaResponseWsErrorAgent",
]


class BetaResponseAudioWsDelta(BetaResponseAudioDeltaEvent):
    """Emitted when there is a partial audio response."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseAudioWsDone(BetaResponseAudioDoneEvent):
    """Emitted when the audio response is complete."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseAudioTranscriptWsDelta(BetaResponseAudioTranscriptDeltaEvent):
    """Emitted when there is a partial transcript of audio."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseAudioTranscriptWsDone(BetaResponseAudioTranscriptDoneEvent):
    """Emitted when the full audio transcript is completed."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseCodeInterpreterCallCodeWsDelta(BetaResponseCodeInterpreterCallCodeDeltaEvent):
    """Emitted when a partial code snippet is streamed by the code interpreter."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseCodeInterpreterCallCodeWsDone(BetaResponseCodeInterpreterCallCodeDoneEvent):
    """Emitted when the code snippet is finalized by the code interpreter."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseCodeInterpreterCallWsCompleted(BetaResponseCodeInterpreterCallCompletedEvent):
    """Emitted when the code interpreter call is completed."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseCodeInterpreterCallInWsProgress(BetaResponseCodeInterpreterCallInProgressEvent):
    """Emitted when a code interpreter call is in progress."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseCodeInterpreterCallWsInterpreting(BetaResponseCodeInterpreterCallInterpretingEvent):
    """Emitted when the code interpreter is actively interpreting the code snippet."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseWsCompleted(BetaResponseCompletedEvent):
    """Emitted when the model response is complete."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseContentPartWsAdded(BetaResponseContentPartAddedEvent):
    """Emitted when a new content part is added."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseContentPartWsDone(BetaResponseContentPartDoneEvent):
    """Emitted when a content part is done."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseWsCreated(BetaResponseCreatedEvent):
    """An event that is emitted when a response is created."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseFileSearchCallWsCompleted(BetaResponseFileSearchCallCompletedEvent):
    """Emitted when a file search call is completed (results found)."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseFileSearchCallInWsProgress(BetaResponseFileSearchCallInProgressEvent):
    """Emitted when a file search call is initiated."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseFileSearchCallWsSearching(BetaResponseFileSearchCallSearchingEvent):
    """Emitted when a file search is currently searching."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseFunctionCallArgumentsWsDelta(BetaResponseFunctionCallArgumentsDeltaEvent):
    """Emitted when there is a partial function-call arguments delta."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseFunctionCallArgumentsWsDone(BetaResponseFunctionCallArgumentsDoneEvent):
    """Emitted when function-call arguments are finalized."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseInWsProgress(BetaResponseInProgressEvent):
    """Emitted when the response is in progress."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseWsFailed(BetaResponseFailedEvent):
    """An event that is emitted when a response fails."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseWsIncomplete(BetaResponseIncompleteEvent):
    """An event that is emitted when a response finishes as incomplete."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseOutputItemWsAdded(BetaResponseOutputItemAddedEvent):
    """Emitted when a new output item is added."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseOutputItemWsDone(BetaResponseOutputItemDoneEvent):
    """Emitted when an output item is marked done."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseReasoningSummaryPartWsAdded(BetaResponseReasoningSummaryPartAddedEvent):
    """Emitted when a new reasoning summary part is added."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseReasoningSummaryPartWsDone(BetaResponseReasoningSummaryPartDoneEvent):
    """Emitted when a reasoning summary part is completed."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseReasoningSummaryTextWsDelta(BetaResponseReasoningSummaryTextDeltaEvent):
    """Emitted when a delta is added to a reasoning summary text."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseReasoningSummaryTextWsDone(BetaResponseReasoningSummaryTextDoneEvent):
    """Emitted when a reasoning summary text is completed."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseReasoningTextWsDelta(BetaResponseReasoningTextDeltaEvent):
    """Emitted when a delta is added to a reasoning text."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseReasoningTextWsDone(BetaResponseReasoningTextDoneEvent):
    """Emitted when a reasoning text is completed."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseRefusalWsDelta(BetaResponseRefusalDeltaEvent):
    """Emitted when there is a partial refusal text."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseRefusalWsDone(BetaResponseRefusalDoneEvent):
    """Emitted when refusal text is finalized."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseTextWsDelta(BetaResponseTextDeltaEvent):
    """Emitted when there is an additional text delta."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseTextWsDone(BetaResponseTextDoneEvent):
    """Emitted when text content is finalized."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseWebSearchCallWsCompleted(BetaResponseWebSearchCallCompletedEvent):
    """Emitted when a web search call is completed."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseWebSearchCallInWsProgress(BetaResponseWebSearchCallInProgressEvent):
    """Emitted when a web search call is initiated."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseWebSearchCallWsSearching(BetaResponseWebSearchCallSearchingEvent):
    """Emitted when a web search call is executing."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseImageGenCallWsCompleted(BetaResponseImageGenCallCompletedEvent):
    """
    Emitted when an image generation tool call has completed and the final image is available.
    """

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseImageGenCallWsGenerating(BetaResponseImageGenCallGeneratingEvent):
    """
    Emitted when an image generation tool call is actively generating an image (intermediate state).
    """

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseImageGenCallInWsProgress(BetaResponseImageGenCallInProgressEvent):
    """Emitted when an image generation tool call is in progress."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseImageGenCallPartialWsImage(BetaResponseImageGenCallPartialImageEvent):
    """Emitted when a partial image is available during image generation streaming."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseMcpCallArgumentsWsDelta(BetaResponseMcpCallArgumentsDeltaEvent):
    """
    Emitted when there is a delta (partial update) to the arguments of an MCP tool call.
    """

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseMcpCallArgumentsWsDone(BetaResponseMcpCallArgumentsDoneEvent):
    """Emitted when the arguments for an MCP tool call are finalized."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseMcpCallWsCompleted(BetaResponseMcpCallCompletedEvent):
    """Emitted when an MCP  tool call has completed successfully."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseMcpCallWsFailed(BetaResponseMcpCallFailedEvent):
    """Emitted when an MCP  tool call has failed."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseMcpCallInWsProgress(BetaResponseMcpCallInProgressEvent):
    """Emitted when an MCP  tool call is in progress."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseMcpListToolsWsCompleted(BetaResponseMcpListToolsCompletedEvent):
    """Emitted when the list of available MCP tools has been successfully retrieved."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseMcpListToolsWsFailed(BetaResponseMcpListToolsFailedEvent):
    """Emitted when the attempt to list available MCP tools has failed."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseMcpListToolsInWsProgress(BetaResponseMcpListToolsInProgressEvent):
    """
    Emitted when the system is in the process of retrieving the list of available MCP tools.
    """

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseOutputTextAnnotationWsAdded(BetaResponseOutputTextAnnotationAddedEvent):
    """Emitted when an annotation is added to output text content."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseWsQueued(BetaResponseQueuedEvent):
    """Emitted when a response is queued and waiting to be processed."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseCustomToolCallInputWsDelta(BetaResponseCustomToolCallInputDeltaEvent):
    """Event representing a delta (partial update) to the input of a custom tool call."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseCustomToolCallInputWsDone(BetaResponseCustomToolCallInputDoneEvent):
    """Event indicating that input for a custom tool call is complete."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class BetaResponseWsErrorError(BaseModel):
    """Details about the error."""

    code: Optional[str] = None
    """The error code that was emitted, if any."""

    message: str
    """The human-readable error message that was emitted."""

    param: Optional[str] = None
    """The parameter name that was associated with the error, if any."""

    type: str
    """The error type that was emitted."""

    headers: Optional[Dict[str, str]] = None
    """The response headers that were emitted with the error, if any."""


class BetaResponseWsErrorAgent(BaseModel):
    """The agent that owns this multi-agent streaming event."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class BetaResponseWsError(BaseModel):
    """Emitted when an error occurs while processing a Responses WebSocket request."""

    error: BetaResponseWsErrorError
    """Details about the error."""

    type: Literal["error"]
    """The type of the event. Always `error`."""

    agent: Optional[BetaResponseWsErrorAgent] = None
    """The agent that owns this multi-agent streaming event."""

    sequence_number: Optional[int] = None
    """The sequence number of an error emitted by the response stream."""

    status: Optional[int] = None
    """The HTTP status code associated with a WebSocket protocol error."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


BetaResponsesServerEvent: TypeAlias = Annotated[
    Union[
        BetaResponseAudioWsDelta,
        BetaResponseAudioWsDone,
        BetaResponseAudioTranscriptWsDelta,
        BetaResponseAudioTranscriptWsDone,
        BetaResponseCodeInterpreterCallCodeWsDelta,
        BetaResponseCodeInterpreterCallCodeWsDone,
        BetaResponseCodeInterpreterCallWsCompleted,
        BetaResponseCodeInterpreterCallInWsProgress,
        BetaResponseCodeInterpreterCallWsInterpreting,
        BetaResponseWsCompleted,
        BetaResponseContentPartWsAdded,
        BetaResponseContentPartWsDone,
        BetaResponseWsCreated,
        BetaResponseFileSearchCallWsCompleted,
        BetaResponseFileSearchCallInWsProgress,
        BetaResponseFileSearchCallWsSearching,
        BetaResponseFunctionCallArgumentsWsDelta,
        BetaResponseFunctionCallArgumentsWsDone,
        BetaResponseInWsProgress,
        BetaResponseWsFailed,
        BetaResponseWsIncomplete,
        BetaResponseOutputItemWsAdded,
        BetaResponseOutputItemWsDone,
        BetaResponseReasoningSummaryPartWsAdded,
        BetaResponseReasoningSummaryPartWsDone,
        BetaResponseReasoningSummaryTextWsDelta,
        BetaResponseReasoningSummaryTextWsDone,
        BetaResponseReasoningTextWsDelta,
        BetaResponseReasoningTextWsDone,
        BetaResponseRefusalWsDelta,
        BetaResponseRefusalWsDone,
        BetaResponseTextWsDelta,
        BetaResponseTextWsDone,
        BetaResponseWebSearchCallWsCompleted,
        BetaResponseWebSearchCallInWsProgress,
        BetaResponseWebSearchCallWsSearching,
        BetaResponseImageGenCallWsCompleted,
        BetaResponseImageGenCallWsGenerating,
        BetaResponseImageGenCallInWsProgress,
        BetaResponseImageGenCallPartialWsImage,
        BetaResponseMcpCallArgumentsWsDelta,
        BetaResponseMcpCallArgumentsWsDone,
        BetaResponseMcpCallWsCompleted,
        BetaResponseMcpCallWsFailed,
        BetaResponseMcpCallInWsProgress,
        BetaResponseMcpListToolsWsCompleted,
        BetaResponseMcpListToolsWsFailed,
        BetaResponseMcpListToolsInWsProgress,
        BetaResponseOutputTextAnnotationWsAdded,
        BetaResponseWsQueued,
        BetaResponseCustomToolCallInputWsDelta,
        BetaResponseCustomToolCallInputWsDone,
        BetaResponseWsError,
        BetaResponseInjectCreatedEvent,
        BetaResponseInjectFailedEvent,
    ],
    PropertyInfo(discriminator="type"),
]
