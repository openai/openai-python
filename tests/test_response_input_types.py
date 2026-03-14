from __future__ import annotations

from openai.types.responses import ResponseInputParam
from openai.types.responses.response_input_item_param import ImageGenerationCall


def test_image_generation_call_input_allows_id_only() -> None:
    image_generation_call: ImageGenerationCall = {
        "id": "ig_123",
        "type": "image_generation_call",
    }

    response_input: ResponseInputParam = [image_generation_call]

    assert response_input == [image_generation_call]
