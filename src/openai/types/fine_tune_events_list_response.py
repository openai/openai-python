# File generated from our OpenAPI spec by Stainless.

from typing import List

from .._models import BaseModel
from .fine_tune_event import FineTuneEvent

__all__ = ["FineTuneEventsListResponse"]


class FineTuneEventsListResponse(BaseModel):
    data: List[FineTuneEvent]

    object: str
