# Tests for https://github.com/openai/openai-python/issues/3419
# ResponseOutputTextAnnotationAddedEvent.annotation should be typed as Annotation, not object

from openai._models import construct_type
from openai.types.responses.response_output_text_annotation_added_event import ResponseOutputTextAnnotationAddedEvent
from openai.types.responses.response_output_text import (
    Annotation,
    AnnotationFileCitation,
    AnnotationURLCitation,
    AnnotationContainerFileCitation,
    AnnotationFilePath,
)


def test_annotation_url_citation() -> None:
    """Test that url_citation annotation is properly typed and parsed."""
    event = ResponseOutputTextAnnotationAddedEvent(
        annotation={
            "type": "url_citation",
            "title": "Example",
            "url": "https://example.com",
            "start_index": 0,
            "end_index": 10,
        },
        annotation_index=0,
        content_index=0,
        item_id="item_123",
        output_index=0,
        sequence_number=1,
        type="response.output_text.annotation.added",
    )

    # After the fix, annotation should be an AnnotationURLCitation, not plain object
    assert isinstance(event.annotation, AnnotationURLCitation)
    assert event.annotation.type == "url_citation"
    assert event.annotation.title == "Example"
    assert event.annotation.url == "https://example.com"
    assert event.annotation.start_index == 0
    assert event.annotation.end_index == 10


def test_annotation_file_citation() -> None:
    """Test that file_citation annotation is properly typed and parsed."""
    event = ResponseOutputTextAnnotationAddedEvent(
        annotation={
            "type": "file_citation",
            "file_id": "file_abc123",
            "filename": "document.pdf",
            "index": 0,
        },
        annotation_index=0,
        content_index=0,
        item_id="item_123",
        output_index=0,
        sequence_number=1,
        type="response.output_text.annotation.added",
    )

    assert isinstance(event.annotation, AnnotationFileCitation)
    assert event.annotation.type == "file_citation"
    assert event.annotation.file_id == "file_abc123"
    assert event.annotation.filename == "document.pdf"
    assert event.annotation.index == 0


def test_annotation_container_file_citation() -> None:
    """Test that container_file_citation annotation is properly typed and parsed."""
    event = ResponseOutputTextAnnotationAddedEvent(
        annotation={
            "type": "container_file_citation",
            "container_id": "container_abc",
            "file_id": "file_abc123",
            "filename": "document.pdf",
            "start_index": 0,
            "end_index": 10,
        },
        annotation_index=0,
        content_index=0,
        item_id="item_123",
        output_index=0,
        sequence_number=1,
        type="response.output_text.annotation.added",
    )

    assert isinstance(event.annotation, AnnotationContainerFileCitation)
    assert event.annotation.type == "container_file_citation"
    assert event.annotation.container_id == "container_abc"
    assert event.annotation.file_id == "file_abc123"
    assert event.annotation.filename == "document.pdf"
    assert event.annotation.start_index == 0
    assert event.annotation.end_index == 10


def test_annotation_file_path() -> None:
    """Test that file_path annotation is properly typed and parsed."""
    event = ResponseOutputTextAnnotationAddedEvent(
        annotation={
            "type": "file_path",
            "file_id": "file_abc123",
            "index": 0,
        },
        annotation_index=0,
        content_index=0,
        item_id="item_123",
        output_index=0,
        sequence_number=1,
        type="response.output_text.annotation.added",
    )

    assert isinstance(event.annotation, AnnotationFilePath)
    assert event.annotation.type == "file_path"
    assert event.annotation.file_id == "file_abc123"
    assert event.annotation.index == 0


def test_annotation_type_is_union() -> None:
    """Test that the annotation field accepts all annotation types."""
    # Verify the field is typed as Annotation (Union of all annotation types), not object
    # We check by inspecting the model's field info directly
    field_info = ResponseOutputTextAnnotationAddedEvent.model_fields["annotation"]
    annotation_type = field_info.annotation

    # The Annotation type is an Annotated[Union[...], ...]
    # We can verify it's not just 'object'
    assert annotation_type is not object


def test_construct_type_with_annotation() -> None:
    """Test that construct_type works with the Annotation type for streaming events."""
    # This simulates how streaming events are parsed
    annotation_data = {
        "type": "url_citation",
        "title": "Test",
        "url": "https://test.com",
        "start_index": 5,
        "end_index": 15,
    }

    # construct_type should be able to parse this as an Annotation
    annotation = construct_type(value=annotation_data, type_=Annotation)
    assert isinstance(annotation, AnnotationURLCitation)
    assert annotation.title == "Test"
    assert annotation.url == "https://test.com"
