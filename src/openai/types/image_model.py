# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal, TypeAlias

__all__ = ["ImageModel"]

ImageModel: TypeAlias = Literal[
    "gpt-image-1.5",
    "gpt-image-2",
    "gpt-image-2-2026-04-21",
    "gpt-image-2.5-sunburst",
    "gpt-image-2.5-sunburst-2026-09-08",
    "gpt-image-2.5-flare",
    "gpt-image-2.5-flare-2026-09-08",
    "gpt-image-1",
    "gpt-image-1-mini",
    "chatgpt-image-latest",
    "dall-e-2",
    "dall-e-3",
]
"""Deprecated values:

- "dall-e-2", "dall-e-3": This model was retired on May 12, 2026. Use a GPT
  image model instead.
"""
