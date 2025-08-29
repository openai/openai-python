"""Test response output items."""

import pytest
from openai.types.responses.response_output_item import ImageGenerationCall


class TestImageGenerationCall:
    """Test ImageGenerationCall class functionality."""

    def test_image_generation_call_basic_fields(self) -> None:
        """Test ImageGenerationCall with basic required fields."""
        img_call = ImageGenerationCall(
            id='ig_test',
            result='base64_image_data',
            status='completed',
            type='image_generation_call'
        )

        assert img_call.id == 'ig_test'
        assert img_call.result == 'base64_image_data'
        assert img_call.status == 'completed'
        assert img_call.type == 'image_generation_call'

    def test_image_generation_call_with_none_result(self) -> None:
        """Test ImageGenerationCall with None result."""
        img_call = ImageGenerationCall(
            id='ig_test',
            result=None,
            status='in_progress',
            type='image_generation_call'
        )

        assert img_call.id == 'ig_test'
        assert img_call.result is None
        assert img_call.status == 'in_progress'
        assert img_call.type == 'image_generation_call'

    def test_image_generation_call_dynamic_fields(self) -> None:
        """Test ImageGenerationCall allows dynamic field access without mypy errors."""
        # Create instance with additional fields that are not defined in the class
        img_call = ImageGenerationCall(
            id='ig_test',
            result='base64_image_data',
            status='completed',
            type='image_generation_call',
            background='transparent',
            output_format='png',
            quality='high',
            revised_prompt='A dog on transparent background',
            size='1024x1024',
            style='natural'
        )

        # Verify standard fields work
        assert img_call.id == 'ig_test'
        assert img_call.result == 'base64_image_data'
        assert img_call.status == 'completed'
        assert img_call.type == 'image_generation_call'

        # Verify dynamic field access works without mypy errors
        assert img_call.background == 'transparent'
        assert img_call.output_format == 'png'
        assert img_call.quality == 'high'
        assert img_call.revised_prompt == 'A dog on transparent background'
        assert img_call.size == '1024x1024'
        assert img_call.style == 'natural'

    def test_image_generation_call_status_values(self) -> None:
        """Test ImageGenerationCall with different status values."""
        statuses = ["in_progress", "completed", "generating", "failed"]
        
        for status in statuses:
            img_call = ImageGenerationCall(
                id=f'ig_test_{status}',
                result='base64_image_data' if status == 'completed' else None,
                status=status,
                type='image_generation_call'
            )
            assert img_call.status == status

    def test_image_generation_call_attribute_error(self) -> None:
        """Test ImageGenerationCall raises AttributeError for non-existent attributes."""
        img_call = ImageGenerationCall(
            id='ig_test',
            result='base64_image_data',
            status='completed',
            type='image_generation_call'
        )

        # Test that accessing non-existent attribute raises AttributeError
        with pytest.raises(AttributeError, match="'ImageGenerationCall' object has no attribute 'non_existent_field'"):
            _ = img_call.non_existent_field

        with pytest.raises(AttributeError, match="'ImageGenerationCall' object has no attribute 'invalid_attribute'"):
            _ = img_call.invalid_attribute

    def test_image_generation_call_dynamic_field_not_in_extra(self) -> None:
        """Test behavior when dynamic field is not found in __pydantic_extra__ or __dict__."""
        # Create instance without additional dynamic fields
        img_call = ImageGenerationCall(
            id='ig_test',
            result='base64_image_data',
            status='completed',
            type='image_generation_call'
        )

        # Test that accessing undefined dynamic field raises AttributeError
        with pytest.raises(AttributeError, match="'ImageGenerationCall' object has no attribute 'undefined_field'"):
            _ = img_call.undefined_field

    def test_image_generation_call_dynamic_fields_edge_cases(self) -> None:
        """Test edge cases for dynamic field access."""
        # Create instance with dynamic fields including edge case names
        img_call = ImageGenerationCall(
            id='ig_test',
            result='base64_image_data',
            status='completed',
            type='image_generation_call',
            empty_string='',
            zero_value=0,
            false_value=False,
            none_value=None
        )

        # Verify edge case values are handled correctly
        assert img_call.empty_string == ''
        assert img_call.zero_value == 0
        assert img_call.false_value is False
        assert img_call.none_value is None

        # Test that accessing truly non-existent field still raises error
        with pytest.raises(AttributeError, match="'ImageGenerationCall' object has no attribute 'truly_missing'"):
            _ = img_call.truly_missing