# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from .._models import BaseModel
from .demo_widget import DemoWidget

__all__ = ["DemoAPIListResponse"]


class DemoAPIListResponse(BaseModel):
    """A list of demo API widgets."""

    data: List[DemoWidget]
    """The demo widgets in the current page."""

    object: Literal["list"]
    """The object type, which is always `list`."""
