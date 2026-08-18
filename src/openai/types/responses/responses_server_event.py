# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Dict, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .response_failed_event import ResponseFailedEvent
from .response_queued_event import ResponseQueuedEvent
from .response_created_event import ResponseCreatedEvent
from .response_completed_event import ResponseCompletedEvent
from .response_text_done_event import ResponseTextDoneEvent
from .response_audio_done_event import ResponseAudioDoneEvent
from .response_incomplete_event import ResponseIncompleteEvent
from .response_text_delta_event import ResponseTextDeltaEvent
from .response_audio_delta_event import ResponseAudioDeltaEvent
from .response_in_progress_event import ResponseInProgressEvent
from .response_refusal_done_event import ResponseRefusalDoneEvent
from .response_refusal_delta_event import ResponseRefusalDeltaEvent
from .response_mcp_call_failed_event import ResponseMcpCallFailedEvent
from .response_output_item_done_event import ResponseOutputItemDoneEvent
from .response_content_part_done_event import ResponseContentPartDoneEvent
from .response_output_item_added_event import ResponseOutputItemAddedEvent
from .response_content_part_added_event import ResponseContentPartAddedEvent
from .response_mcp_call_completed_event import ResponseMcpCallCompletedEvent
from .response_reasoning_text_done_event import ResponseReasoningTextDoneEvent
from .response_mcp_call_in_progress_event import ResponseMcpCallInProgressEvent
from .response_reasoning_text_delta_event import ResponseReasoningTextDeltaEvent
from .response_audio_transcript_done_event import ResponseAudioTranscriptDoneEvent
from .response_mcp_list_tools_failed_event import ResponseMcpListToolsFailedEvent
from .response_audio_transcript_delta_event import ResponseAudioTranscriptDeltaEvent
from .response_mcp_call_arguments_done_event import ResponseMcpCallArgumentsDoneEvent
from .response_shell_call_command_done_event import ResponseShellCallCommandDoneEvent
from .response_image_gen_call_completed_event import ResponseImageGenCallCompletedEvent
from .response_mcp_call_arguments_delta_event import ResponseMcpCallArgumentsDeltaEvent
from .response_mcp_list_tools_completed_event import ResponseMcpListToolsCompletedEvent
from .response_shell_call_command_added_event import ResponseShellCallCommandAddedEvent
from .response_shell_call_command_delta_event import ResponseShellCallCommandDeltaEvent
from .response_image_gen_call_generating_event import ResponseImageGenCallGeneratingEvent
from .response_web_search_call_completed_event import ResponseWebSearchCallCompletedEvent
from .response_web_search_call_searching_event import ResponseWebSearchCallSearchingEvent
from .response_file_search_call_completed_event import ResponseFileSearchCallCompletedEvent
from .response_file_search_call_searching_event import ResponseFileSearchCallSearchingEvent
from .response_image_gen_call_in_progress_event import ResponseImageGenCallInProgressEvent
from .response_mcp_list_tools_in_progress_event import ResponseMcpListToolsInProgressEvent
from .response_custom_tool_call_input_done_event import ResponseCustomToolCallInputDoneEvent
from .response_reasoning_summary_part_done_event import ResponseReasoningSummaryPartDoneEvent
from .response_reasoning_summary_text_done_event import ResponseReasoningSummaryTextDoneEvent
from .response_web_search_call_in_progress_event import ResponseWebSearchCallInProgressEvent
from .response_custom_tool_call_input_delta_event import ResponseCustomToolCallInputDeltaEvent
from .response_file_search_call_in_progress_event import ResponseFileSearchCallInProgressEvent
from .response_function_call_arguments_done_event import ResponseFunctionCallArgumentsDoneEvent
from .response_image_gen_call_partial_image_event import ResponseImageGenCallPartialImageEvent
from .response_output_text_annotation_added_event import ResponseOutputTextAnnotationAddedEvent
from .response_reasoning_summary_part_added_event import ResponseReasoningSummaryPartAddedEvent
from .response_reasoning_summary_text_delta_event import ResponseReasoningSummaryTextDeltaEvent
from .response_function_call_arguments_delta_event import ResponseFunctionCallArgumentsDeltaEvent
from .response_shell_call_output_content_done_event import ResponseShellCallOutputContentDoneEvent
from .response_code_interpreter_call_code_done_event import ResponseCodeInterpreterCallCodeDoneEvent
from .response_code_interpreter_call_completed_event import ResponseCodeInterpreterCallCompletedEvent
from .response_shell_call_output_content_delta_event import ResponseShellCallOutputContentDeltaEvent
from .response_code_interpreter_call_code_delta_event import ResponseCodeInterpreterCallCodeDeltaEvent
from .response_code_interpreter_call_in_progress_event import ResponseCodeInterpreterCallInProgressEvent
from .response_code_interpreter_call_interpreting_event import ResponseCodeInterpreterCallInterpretingEvent

__all__ = [
    "ResponsesServerEvent",
    "ResponseAudioWsDelta",
    "ResponseAudioWsDone",
    "ResponseAudioTranscriptWsDelta",
    "ResponseAudioTranscriptWsDone",
    "ResponseCodeInterpreterCallCodeWsDelta",
    "ResponseCodeInterpreterCallCodeWsDone",
    "ResponseCodeInterpreterCallWsCompleted",
    "ResponseCodeInterpreterCallInWsProgress",
    "ResponseCodeInterpreterCallWsInterpreting",
    "ResponseWsCompleted",
    "ResponseContentPartWsAdded",
    "ResponseContentPartWsDone",
    "ResponseWsCreated",
    "ResponseFileSearchCallWsCompleted",
    "ResponseFileSearchCallInWsProgress",
    "ResponseFileSearchCallWsSearching",
    "ResponseFunctionCallArgumentsWsDelta",
    "ResponseFunctionCallArgumentsWsDone",
    "ResponseShellCallCommandWsAdded",
    "ResponseShellCallCommandWsDelta",
    "ResponseShellCallCommandWsDone",
    "ResponseShellCallOutputContentWsDelta",
    "ResponseShellCallOutputContentWsDone",
    "ResponseInWsProgress",
    "ResponseWsFailed",
    "ResponseWsIncomplete",
    "ResponseOutputItemWsAdded",
    "ResponseOutputItemWsDone",
    "ResponseReasoningSummaryPartWsAdded",
    "ResponseReasoningSummaryPartWsDone",
    "ResponseReasoningSummaryTextWsDelta",
    "ResponseReasoningSummaryTextWsDone",
    "ResponseReasoningTextWsDelta",
    "ResponseReasoningTextWsDone",
    "ResponseRefusalWsDelta",
    "ResponseRefusalWsDone",
    "ResponseTextWsDelta",
    "ResponseTextWsDone",
    "ResponseWebSearchCallWsCompleted",
    "ResponseWebSearchCallInWsProgress",
    "ResponseWebSearchCallWsSearching",
    "ResponseImageGenCallWsCompleted",
    "ResponseImageGenCallWsGenerating",
    "ResponseImageGenCallInWsProgress",
    "ResponseImageGenCallPartialWsImage",
    "ResponseMcpCallArgumentsWsDelta",
    "ResponseMcpCallArgumentsWsDone",
    "ResponseMcpCallWsCompleted",
    "ResponseMcpCallWsFailed",
    "ResponseMcpCallInWsProgress",
    "ResponseMcpListToolsWsCompleted",
    "ResponseMcpListToolsWsFailed",
    "ResponseMcpListToolsInWsProgress",
    "ResponseOutputTextAnnotationWsAdded",
    "ResponseWsQueued",
    "ResponseCustomToolCallInputWsDelta",
    "ResponseCustomToolCallInputWsDone",
    "ResponseWsError",
    "ResponseWsErrorError",
]


class ResponseAudioWsDelta(ResponseAudioDeltaEvent):
    """Emitted when there is a partial audio response."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseAudioWsDone(ResponseAudioDoneEvent):
    """Emitted when the audio response is complete."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseAudioTranscriptWsDelta(ResponseAudioTranscriptDeltaEvent):
    """Emitted when there is a partial transcript of audio."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseAudioTranscriptWsDone(ResponseAudioTranscriptDoneEvent):
    """Emitted when the full audio transcript is completed."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseCodeInterpreterCallCodeWsDelta(ResponseCodeInterpreterCallCodeDeltaEvent):
    """Emitted when a partial code snippet is streamed by the code interpreter."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseCodeInterpreterCallCodeWsDone(ResponseCodeInterpreterCallCodeDoneEvent):
    """Emitted when the code snippet is finalized by the code interpreter."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseCodeInterpreterCallWsCompleted(ResponseCodeInterpreterCallCompletedEvent):
    """Emitted when the code interpreter call is completed."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseCodeInterpreterCallInWsProgress(ResponseCodeInterpreterCallInProgressEvent):
    """Emitted when a code interpreter call is in progress."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseCodeInterpreterCallWsInterpreting(ResponseCodeInterpreterCallInterpretingEvent):
    """Emitted when the code interpreter is actively interpreting the code snippet."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseWsCompleted(ResponseCompletedEvent):
    """Emitted when the model response is complete."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseContentPartWsAdded(ResponseContentPartAddedEvent):
    """Emitted when a new content part is added."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseContentPartWsDone(ResponseContentPartDoneEvent):
    """Emitted when a content part is done."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseWsCreated(ResponseCreatedEvent):
    """An event that is emitted when a response is created."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseFileSearchCallWsCompleted(ResponseFileSearchCallCompletedEvent):
    """Emitted when a file search call is completed (results found)."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseFileSearchCallInWsProgress(ResponseFileSearchCallInProgressEvent):
    """Emitted when a file search call is initiated."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseFileSearchCallWsSearching(ResponseFileSearchCallSearchingEvent):
    """Emitted when a file search is currently searching."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseFunctionCallArgumentsWsDelta(ResponseFunctionCallArgumentsDeltaEvent):
    """Emitted when there is a partial function-call arguments delta."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseFunctionCallArgumentsWsDone(ResponseFunctionCallArgumentsDoneEvent):
    """Emitted when function-call arguments are finalized."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseShellCallCommandWsAdded(ResponseShellCallCommandAddedEvent):
    """A streaming event that indicated a shell command was added to a tool call."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseShellCallCommandWsDelta(ResponseShellCallCommandDeltaEvent):
    """A streaming event that indicated a shell command was incrementally updated."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseShellCallCommandWsDone(ResponseShellCallCommandDoneEvent):
    """A streaming event that indicated a shell command was completed."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseShellCallOutputContentWsDelta(ResponseShellCallOutputContentDeltaEvent):
    """A streaming event that indicated shell call output was incrementally added."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseShellCallOutputContentWsDone(ResponseShellCallOutputContentDoneEvent):
    """A streaming event that indicated shell call output was completed."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseInWsProgress(ResponseInProgressEvent):
    """Emitted when the response is in progress."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseWsFailed(ResponseFailedEvent):
    """An event that is emitted when a response fails."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseWsIncomplete(ResponseIncompleteEvent):
    """An event that is emitted when a response finishes as incomplete."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseOutputItemWsAdded(ResponseOutputItemAddedEvent):
    """Emitted when a new output item is added."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseOutputItemWsDone(ResponseOutputItemDoneEvent):
    """Emitted when an output item is marked done."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseReasoningSummaryPartWsAdded(ResponseReasoningSummaryPartAddedEvent):
    """Emitted when a new reasoning summary part is added."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseReasoningSummaryPartWsDone(ResponseReasoningSummaryPartDoneEvent):
    """Emitted when a reasoning summary part is completed."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseReasoningSummaryTextWsDelta(ResponseReasoningSummaryTextDeltaEvent):
    """Emitted when a delta is added to a reasoning summary text."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseReasoningSummaryTextWsDone(ResponseReasoningSummaryTextDoneEvent):
    """Emitted when a reasoning summary text is completed."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseReasoningTextWsDelta(ResponseReasoningTextDeltaEvent):
    """Emitted when a delta is added to a reasoning text."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseReasoningTextWsDone(ResponseReasoningTextDoneEvent):
    """Emitted when a reasoning text is completed."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseRefusalWsDelta(ResponseRefusalDeltaEvent):
    """Emitted when there is a partial refusal text."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseRefusalWsDone(ResponseRefusalDoneEvent):
    """Emitted when refusal text is finalized."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseTextWsDelta(ResponseTextDeltaEvent):
    """Emitted when there is an additional text delta."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseTextWsDone(ResponseTextDoneEvent):
    """Emitted when text content is finalized."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseWebSearchCallWsCompleted(ResponseWebSearchCallCompletedEvent):
    """Emitted when a web search call is completed."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseWebSearchCallInWsProgress(ResponseWebSearchCallInProgressEvent):
    """Emitted when a web search call is initiated."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseWebSearchCallWsSearching(ResponseWebSearchCallSearchingEvent):
    """Emitted when a web search call is executing."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseImageGenCallWsCompleted(ResponseImageGenCallCompletedEvent):
    """
    Emitted when an image generation tool call has completed and the final image is available.
    """

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseImageGenCallWsGenerating(ResponseImageGenCallGeneratingEvent):
    """
    Emitted when an image generation tool call is actively generating an image (intermediate state).
    """

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseImageGenCallInWsProgress(ResponseImageGenCallInProgressEvent):
    """Emitted when an image generation tool call is in progress."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseImageGenCallPartialWsImage(ResponseImageGenCallPartialImageEvent):
    """Emitted when a partial image is available during image generation streaming."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseMcpCallArgumentsWsDelta(ResponseMcpCallArgumentsDeltaEvent):
    """
    Emitted when there is a delta (partial update) to the arguments of an MCP tool call.
    """

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseMcpCallArgumentsWsDone(ResponseMcpCallArgumentsDoneEvent):
    """Emitted when the arguments for an MCP tool call are finalized."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseMcpCallWsCompleted(ResponseMcpCallCompletedEvent):
    """Emitted when an MCP  tool call has completed successfully."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseMcpCallWsFailed(ResponseMcpCallFailedEvent):
    """Emitted when an MCP  tool call has failed."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseMcpCallInWsProgress(ResponseMcpCallInProgressEvent):
    """Emitted when an MCP  tool call is in progress."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseMcpListToolsWsCompleted(ResponseMcpListToolsCompletedEvent):
    """Emitted when the list of available MCP tools has been successfully retrieved."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseMcpListToolsWsFailed(ResponseMcpListToolsFailedEvent):
    """Emitted when the attempt to list available MCP tools has failed."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseMcpListToolsInWsProgress(ResponseMcpListToolsInProgressEvent):
    """
    Emitted when the system is in the process of retrieving the list of available MCP tools.
    """

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseOutputTextAnnotationWsAdded(ResponseOutputTextAnnotationAddedEvent):
    """Emitted when an annotation is added to output text content."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseWsQueued(ResponseQueuedEvent):
    """Emitted when a response is queued and waiting to be processed."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseCustomToolCallInputWsDelta(ResponseCustomToolCallInputDeltaEvent):
    """Event representing a delta (partial update) to the input of a custom tool call."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseCustomToolCallInputWsDone(ResponseCustomToolCallInputDoneEvent):
    """Event indicating that input for a custom tool call is complete."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


class ResponseWsErrorError(BaseModel):
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


class ResponseWsError(BaseModel):
    """Emitted when an error occurs while processing a Responses WebSocket request."""

    error: ResponseWsErrorError
    """Details about the error."""

    type: Literal["error"]
    """The type of the event. Always `error`."""

    sequence_number: Optional[int] = None
    """The sequence number of an error emitted by the response stream."""

    status: Optional[int] = None
    """The HTTP status code associated with a WebSocket protocol error."""

    stream_id: Optional[str] = None
    """The WebSocket lane that emitted this event.

    This field is present when the originating `response.create` event supplied a
    `stream_id`.
    """


ResponsesServerEvent: TypeAlias = Annotated[
    Union[
        ResponseAudioWsDelta,
        ResponseAudioWsDone,
        ResponseAudioTranscriptWsDelta,
        ResponseAudioTranscriptWsDone,
        ResponseCodeInterpreterCallCodeWsDelta,
        ResponseCodeInterpreterCallCodeWsDone,
        ResponseCodeInterpreterCallWsCompleted,
        ResponseCodeInterpreterCallInWsProgress,
        ResponseCodeInterpreterCallWsInterpreting,
        ResponseWsCompleted,
        ResponseContentPartWsAdded,
        ResponseContentPartWsDone,
        ResponseWsCreated,
        ResponseFileSearchCallWsCompleted,
        ResponseFileSearchCallInWsProgress,
        ResponseFileSearchCallWsSearching,
        ResponseFunctionCallArgumentsWsDelta,
        ResponseFunctionCallArgumentsWsDone,
        ResponseShellCallCommandWsAdded,
        ResponseShellCallCommandWsDelta,
        ResponseShellCallCommandWsDone,
        ResponseShellCallOutputContentWsDelta,
        ResponseShellCallOutputContentWsDone,
        ResponseInWsProgress,
        ResponseWsFailed,
        ResponseWsIncomplete,
        ResponseOutputItemWsAdded,
        ResponseOutputItemWsDone,
        ResponseReasoningSummaryPartWsAdded,
        ResponseReasoningSummaryPartWsDone,
        ResponseReasoningSummaryTextWsDelta,
        ResponseReasoningSummaryTextWsDone,
        ResponseReasoningTextWsDelta,
        ResponseReasoningTextWsDone,
        ResponseRefusalWsDelta,
        ResponseRefusalWsDone,
        ResponseTextWsDelta,
        ResponseTextWsDone,
        ResponseWebSearchCallWsCompleted,
        ResponseWebSearchCallInWsProgress,
        ResponseWebSearchCallWsSearching,
        ResponseImageGenCallWsCompleted,
        ResponseImageGenCallWsGenerating,
        ResponseImageGenCallInWsProgress,
        ResponseImageGenCallPartialWsImage,
        ResponseMcpCallArgumentsWsDelta,
        ResponseMcpCallArgumentsWsDone,
        ResponseMcpCallWsCompleted,
        ResponseMcpCallWsFailed,
        ResponseMcpCallInWsProgress,
        ResponseMcpListToolsWsCompleted,
        ResponseMcpListToolsWsFailed,
        ResponseMcpListToolsInWsProgress,
        ResponseOutputTextAnnotationWsAdded,
        ResponseWsQueued,
        ResponseCustomToolCallInputWsDelta,
        ResponseCustomToolCallInputWsDone,
        ResponseWsError,
    ],
    PropertyInfo(discriminator="type"),
]
