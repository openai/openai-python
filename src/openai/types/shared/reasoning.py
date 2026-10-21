# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import Literal

from ..._models import BaseModel
from .reasoning_effort import ReasoningEffort

__all__ = ["Reasoning"]


class Reasoning(BaseModel):
    """**gpt-5 and o-series models only**

    Configuration options for
    [reasoning models](https://platform.openai.com/docs/guides/reasoning).
    """

    context: Optional[Literal["auto", "current_turn", "all_turns"]] = None
    """
    Controls which reasoning items are rendered back to the model on later turns. If
    omitted or set to `auto`, the model determines the context mode. The `gpt-5.6`
    model family defaults to `all_turns`; earlier models default to `current_turn`.

    When returned on a response, this is the effective reasoning context mode used
    for the response.
    """

    effort: Optional[ReasoningEffort] = None
    """Constrains effort on reasoning for reasoning models.

    Currently supported values are `none`, `minimal`, `low`, `medium`, `high`,
    `xhigh`, and `max`. Reducing reasoning effort can result in faster responses and
    fewer tokens used on reasoning in a response. Not all reasoning models support
    every value. See the
    [reasoning guide](https://platform.openai.com/docs/guides/reasoning) for
    model-specific support.
    """

    generate_summary: Optional[Literal["auto", "concise", "detailed"]] = None
    """**Deprecated:** use `summary` instead.

    A summary of the reasoning performed by the model. This can be useful for
    debugging and understanding the model's reasoning process. One of `auto`,
    `concise`, or `detailed`.
    """

    mode: Union[str, Literal["standard", "pro"], None] = None
    """Controls the reasoning execution mode for the request.

    When returned on a response, this is the effective execution mode.
    """

    summary: Optional[Literal["auto", "concise", "detailed"]] = None
    """A summary of the reasoning performed by the model.

    This can be useful for debugging and understanding the model's reasoning
    process. One of `auto`, `concise`, or `detailed`.

    `concise` is supported for `computer-use-preview` models and all reasoning
    models after `gpt-5`.
    """
