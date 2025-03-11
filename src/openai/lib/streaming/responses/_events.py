from __future__ import annotations

from typing import Optional
from typing_extensions import Union, Generic, TypeVar, Annotated, TypeAlias

from ...._utils import PropertyInfo
from ...._compat import GenericModel
from ....types.responses import (
    ParsedResponse,
    ResponseErrorEvent,
    ResponseFailedEvent,
    ResponseCreatedEvent,
    ResponseTextDoneEvent as RawResponseTextDoneEvent,
    ResponseAudioDoneEvent,
    ResponseCompletedEvent as RawResponseCompletedEvent,
    ResponseTextDeltaEvent as RawResponseTextDeltaEvent,
    ResponseAudioDeltaEvent,
    ResponseIncompleteEvent,
    ResponseInProgressEvent,
    ResponseRefusalDoneEvent,
    ResponseRefusalDeltaEvent,
    ResponseOutputItemDoneEvent,
    ResponseContentPartDoneEvent,
    ResponseOutputItemAddedEvent,
    ResponseContentPartAddedEvent,
    ResponseAudioTranscriptDoneEvent,
    ResponseTextAnnotationDeltaEvent,
    ResponseAudioTranscriptDeltaEvent,
    ResponseWebSearchCallCompletedEvent,
    ResponseWebSearchCallSearchingEvent,
    ResponseFileSearchCallCompletedEvent,
    ResponseFileSearchCallSearchingEvent,
    ResponseWebSearchCallInProgressEvent,
    ResponseFileSearchCallInProgressEvent,
    ResponseFunctionCallArgumentsDoneEvent,
    ResponseFunctionCallArgumentsDeltaEvent as RawResponseFunctionCallArgumentsDeltaEvent,
    ResponseCodeInterpreterCallCodeDoneEvent,
    ResponseCodeInterpreterCallCodeDeltaEvent,
    ResponseCodeInterpreterCallCompletedEvent,
    ResponseCodeInterpreterCallInProgressEvent,
    ResponseCodeInterpreterCallInterpretingEvent,
)

TextFormatT = TypeVar(
    "TextFormatT",
    # if it isn't given then we don't do any parsing
    default=None,
)


class ResponseTextDeltaEvent(RawResponseTextDeltaEvent):
    snapshot: str


class ResponseTextDoneEvent(RawResponseTextDoneEvent, GenericModel, Generic[TextFormatT]):
    parsed: Optional[TextFormatT] = None


class ResponseFunctionCallArgumentsDeltaEvent(RawResponseFunctionCallArgumentsDeltaEvent):
    snapshot: str


class ResponseCompletedEvent(RawResponseCompletedEvent, GenericModel, Generic[TextFormatT]):
    response: ParsedResponse[TextFormatT]  # type: ignore[assignment]


ResponseStreamEvent: TypeAlias = Annotated[
    Union[
        # wrappers with snapshots added on
        ResponseTextDeltaEvent,
        ResponseTextDoneEvent[TextFormatT],
        ResponseFunctionCallArgumentsDeltaEvent,
        ResponseCompletedEvent[TextFormatT],
        # the same as the non-accumulated API
        ResponseAudioDeltaEvent,
        ResponseAudioDoneEvent,
        ResponseAudioTranscriptDeltaEvent,
        ResponseAudioTranscriptDoneEvent,
        ResponseCodeInterpreterCallCodeDeltaEvent,
        ResponseCodeInterpreterCallCodeDoneEvent,
        ResponseCodeInterpreterCallCompletedEvent,
        ResponseCodeInterpreterCallInProgressEvent,
        ResponseCodeInterpreterCallInterpretingEvent,
        ResponseContentPartAddedEvent,
        ResponseContentPartDoneEvent,
        ResponseCreatedEvent,
        ResponseErrorEvent,
        ResponseFileSearchCallCompletedEvent,
        ResponseFileSearchCallInProgressEvent,
        ResponseFileSearchCallSearchingEvent,
        ResponseFunctionCallArgumentsDoneEvent,
        ResponseInProgressEvent,
        ResponseFailedEvent,
        ResponseIncompleteEvent,
        ResponseOutputItemAddedEvent,
        ResponseOutputItemDoneEvent,
        ResponseRefusalDeltaEvent,
        ResponseRefusalDoneEvent,
        ResponseTextAnnotationDeltaEvent,
        ResponseTextDoneEvent,
        ResponseWebSearchCallCompletedEvent,
        ResponseWebSearchCallInProgressEvent,
        ResponseWebSearchCallSearchingEvent,
    ],
    PropertyInfo(discriminator="type"),
]
