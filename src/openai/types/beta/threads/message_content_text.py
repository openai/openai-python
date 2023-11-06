# File generated from our OpenAPI spec by Stainless.

from typing import List, Union
from typing_extensions import Literal

from ...._models import BaseModel

__all__ = [
    "MessageContentText",
    "Text",
    "TextAnnotation",
    "TextAnnotationFileCitation",
    "TextAnnotationFileCitationFileCitation",
    "TextAnnotationFilePath",
    "TextAnnotationFilePathFilePath",
]


class TextAnnotationFileCitationFileCitation(BaseModel):
    file_id: str
    """The ID of the specific File the citation is from."""

    quote: str
    """The specific quote in the File."""


class TextAnnotationFileCitation(BaseModel):
    end_index: int

    file_citation: TextAnnotationFileCitationFileCitation

    start_index: int

    text: str
    """The text in the Message content that needs to be replaced."""

    type: Literal["file_citation"]
    """Will always be `file_citation`."""


class TextAnnotationFilePathFilePath(BaseModel):
    file_id: str
    """The ID of the File that was generated."""


class TextAnnotationFilePath(BaseModel):
    end_index: int

    file_path: TextAnnotationFilePathFilePath

    start_index: int

    text: str
    """The text in the Message content that needs to be replaced."""

    type: Literal["file_path"]
    """Will always be `file_path`."""


TextAnnotation = Union[TextAnnotationFileCitation, TextAnnotationFilePath]


class Text(BaseModel):
    annotations: List[TextAnnotation]

    value: str
    """The data that makes up the text."""


class MessageContentText(BaseModel):
    text: Text

    type: Literal["text"]
    """Will always be `text`."""
