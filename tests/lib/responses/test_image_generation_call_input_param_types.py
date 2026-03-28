from __future__ import annotations

from typing_extensions import assert_type

from openai.types.responses.response_input_param import ImageGenerationCall as ImageGenerationCallParam
from openai.types.responses.response_input_item_param import ImageGenerationCall as ImageGenerationCallItemParam


def test_image_generation_call_input_params_can_omit_result_and_status() -> None:
    input_item: ImageGenerationCallItemParam = {"id": "ig_123", "type": "image_generation_call"}
    input_param: ImageGenerationCallParam = {"id": "ig_456", "type": "image_generation_call"}

    assert input_item == {"id": "ig_123", "type": "image_generation_call"}
    assert input_param == {"id": "ig_456", "type": "image_generation_call"}
    assert "result" not in ImageGenerationCallItemParam.__required_keys__
    assert "status" not in ImageGenerationCallItemParam.__required_keys__
    assert "result" in ImageGenerationCallItemParam.__optional_keys__
    assert "status" in ImageGenerationCallItemParam.__optional_keys__
    assert "result" not in ImageGenerationCallParam.__required_keys__
    assert "status" not in ImageGenerationCallParam.__required_keys__
    assert "result" in ImageGenerationCallParam.__optional_keys__
    assert "status" in ImageGenerationCallParam.__optional_keys__
    assert_type(input_item["id"], str)
    assert_type(input_param["id"], str)
