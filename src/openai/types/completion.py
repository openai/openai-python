# File generated from our OpenAPI spec by Stainless.

from typing import List, Optional

from .._models import BaseModel
from .completion_usage import CompletionUsage
from .completion_choice import CompletionChoice

__all__ = ["Completion"]


class Completion(BaseModel):
    id: str
    """A unique identifier for the completion."""

    choices: List[CompletionChoice]
    """The list of completion choices the model generated for the input prompt."""

    created: int
    """The Unix timestamp (in seconds) of when the completion was created."""

    model: str
    """The model used for completion."""

    object: str
    """The object type, which is always "text_completion" """

    usage: Optional[CompletionUsage] = None
    """Usage statistics for the completion request."""
