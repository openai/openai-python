# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, TypedDict

from ..shared.reasoning_effort import ReasoningEffort

__all__ = ["Reasoning"]


class Reasoning(TypedDict, total=False):
    effort: Optional[ReasoningEffort]
    """**o-series models only**

    Constrains effort on reasoning for
    [reasoning models](https://platform.openai.com/docs/guides/reasoning). Currently
    supported values are `low`, `medium`, and `high`. Reducing reasoning effort can
    result in faster responses and fewer tokens used on reasoning in a response.
    """

    generate_summary: Optional[Literal["concise", "detailed"]]
    """**computer_use_preview only**

    A summary of the reasoning performed by the model. This can be useful for
    debugging and understanding the model's reasoning process. One of `concise` or
    `detailed`.
    """
