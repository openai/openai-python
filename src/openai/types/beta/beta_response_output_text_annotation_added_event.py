# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel

__all__ = [
    "BetaResponseOutputTextAnnotationAddedEvent",
    "Annotation",
    "AnnotationFileCitation",
    "AnnotationURLCitation",
    "AnnotationContainerFileCitation",
    "AnnotationFilePath",
    "Agent",
]


class AnnotationFileCitation(BaseModel):
    """A citation to a file."""

    file_id: str
    """The ID of the file."""

    filename: str
    """The filename of the file cited."""

    index: int
    """The index of the file in the list of files."""

    type: Literal["file_citation"]
    """The type of the file citation. Always `file_citation`."""


class AnnotationURLCitation(BaseModel):
    """A citation for a web resource used to generate a model response."""

    end_index: int
    """The index of the last character of the URL citation in the message."""

    start_index: int
    """The index of the first character of the URL citation in the message."""

    title: str
    """The title of the web resource."""

    type: Literal["url_citation"]
    """The type of the URL citation. Always `url_citation`."""

    url: str
    """The URL of the web resource."""


class AnnotationContainerFileCitation(BaseModel):
    """A citation for a container file used to generate a model response."""

    container_id: str
    """The ID of the container file."""

    end_index: int
    """The index of the last character of the container file citation in the message."""

    file_id: str
    """The ID of the file."""

    filename: str
    """The filename of the container file cited."""

    start_index: int
    """The index of the first character of the container file citation in the message."""

    type: Literal["container_file_citation"]
    """The type of the container file citation. Always `container_file_citation`."""


class AnnotationFilePath(BaseModel):
    """A path to a file."""

    file_id: str
    """The ID of the file."""

    index: int
    """The index of the file in the list of files."""

    type: Literal["file_path"]
    """The type of the file path. Always `file_path`."""


Annotation: TypeAlias = Annotated[
    Union[AnnotationFileCitation, AnnotationURLCitation, AnnotationContainerFileCitation, AnnotationFilePath, None],
    PropertyInfo(discriminator="type"),
]


class Agent(BaseModel):
    """The agent that owns this multi-agent streaming event."""

    agent_name: str
    """The canonical name of the agent that produced this item."""


class BetaResponseOutputTextAnnotationAddedEvent(BaseModel):
    """Emitted when an annotation is added to output text content."""

    annotation: Optional[Annotation] = None
    """An annotation that applies to a span of output text."""

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

    agent: Optional[Agent] = None
    """The agent that owns this multi-agent streaming event."""
