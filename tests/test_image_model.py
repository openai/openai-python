from typing import get_args

from openai.types import ImageModel


def test_image_model_includes_gpt_image_2() -> None:
    assert "gpt-image-2" in get_args(ImageModel)
