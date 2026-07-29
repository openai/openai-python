# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from .._models import BaseModel
from .demo_widget_history import DemoWidgetHistory
from .demo_widget_configuration import DemoWidgetConfiguration

__all__ = ["DemoWidget"]


class DemoWidget(BaseModel):
    """A demo-only widget used to test SDK generation."""

    id: str
    """The unique identifier of the widget."""

    configuration: DemoWidgetConfiguration
    """Demo-only configuration applied to a widget."""

    history: List[DemoWidgetHistory]
    """Status transitions recorded for the widget."""

    name: str
    """The human-readable name of the widget."""

    object: Literal["demo_api.widget"]
    """The object type, which is always `demo_api.widget`."""

    status: Literal["pending", "active", "archived"]
    """The current status of the widget."""
