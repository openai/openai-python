# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["DemoWidgetConfiguration"]


class DemoWidgetConfiguration(BaseModel):
    """Demo-only configuration applied to a widget."""

    priority: int
    """The scheduling priority of the widget."""

    region: Literal["us-east", "us-west", "eu-west"]
    """The region used by the widget."""

    labels: Optional[Dict[str, str]] = None
    """User-defined labels attached to the widget."""
