# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Annotated, TypeAlias

from ..._utils import PropertyInfo
from .beta_response_error_event import BetaResponseErrorEvent
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
from .beta_response_refusal_delta_event import BetaResponseRefusalDeltaEvent
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

__all__ = ["BetaResponseStreamEvent"]

BetaResponseStreamEvent: TypeAlias = Annotated[
    Union[
        BetaResponseAudioDeltaEvent,
        BetaResponseAudioDoneEvent,
        BetaResponseAudioTranscriptDeltaEvent,
        BetaResponseAudioTranscriptDoneEvent,
        BetaResponseCodeInterpreterCallCodeDeltaEvent,
        BetaResponseCodeInterpreterCallCodeDoneEvent,
        BetaResponseCodeInterpreterCallCompletedEvent,
        BetaResponseCodeInterpreterCallInProgressEvent,
        BetaResponseCodeInterpreterCallInterpretingEvent,
        BetaResponseCompletedEvent,
        BetaResponseContentPartAddedEvent,
        BetaResponseContentPartDoneEvent,
        BetaResponseCreatedEvent,
        BetaResponseErrorEvent,
        BetaResponseFileSearchCallCompletedEvent,
        BetaResponseFileSearchCallInProgressEvent,
        BetaResponseFileSearchCallSearchingEvent,
        BetaResponseFunctionCallArgumentsDeltaEvent,
        BetaResponseFunctionCallArgumentsDoneEvent,
        BetaResponseInProgressEvent,
        BetaResponseFailedEvent,
        BetaResponseIncompleteEvent,
        BetaResponseOutputItemAddedEvent,
        BetaResponseOutputItemDoneEvent,
        BetaResponseReasoningSummaryPartAddedEvent,
        BetaResponseReasoningSummaryPartDoneEvent,
        BetaResponseReasoningSummaryTextDeltaEvent,
        BetaResponseReasoningSummaryTextDoneEvent,
        BetaResponseReasoningTextDeltaEvent,
        BetaResponseReasoningTextDoneEvent,
        BetaResponseRefusalDeltaEvent,
        BetaResponseRefusalDoneEvent,
        BetaResponseTextDeltaEvent,
        BetaResponseTextDoneEvent,
        BetaResponseWebSearchCallCompletedEvent,
        BetaResponseWebSearchCallInProgressEvent,
        BetaResponseWebSearchCallSearchingEvent,
        BetaResponseImageGenCallCompletedEvent,
        BetaResponseImageGenCallGeneratingEvent,
        BetaResponseImageGenCallInProgressEvent,
        BetaResponseImageGenCallPartialImageEvent,
        BetaResponseMcpCallArgumentsDeltaEvent,
        BetaResponseMcpCallArgumentsDoneEvent,
        BetaResponseMcpCallCompletedEvent,
        BetaResponseMcpCallFailedEvent,
        BetaResponseMcpCallInProgressEvent,
        BetaResponseMcpListToolsCompletedEvent,
        BetaResponseMcpListToolsFailedEvent,
        BetaResponseMcpListToolsInProgressEvent,
        BetaResponseOutputTextAnnotationAddedEvent,
        BetaResponseQueuedEvent,
        BetaResponseCustomToolCallInputDeltaEvent,
        BetaResponseCustomToolCallInputDoneEvent,
    ],
    PropertyInfo(discriminator="type"),
]
