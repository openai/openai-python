# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel
from .response_output_text import Annotation

__all__ = ["ResponseOutputTextAnnotationAddedEvent"]


class ResponseOutputTextAnnotationAddedEvent(BaseModel):
    """Emitted when an annotation is added to output text content."""

    annotation: Annotation
    """The annotation object being added."""

    annotation_index: int
    """The index of the annotation within the content part."""

    content_index: int
    """The index of the content part within the output item."""

    item_id: str
    """The unique identifier of the item to which the annotation is being added."""

    output_index: int
    """The index of the output item in the response's output array."""

    sequence_number: int
    """The sequence number of this event."""

    type: Literal["response.output_text.annotation.added"]
    """The type of the event. Always 'response.output_text.annotation.added'."""
