# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["DemoWidgetHistory"]


class DemoWidgetHistory(BaseModel):
    """A demo-only status transition for a widget."""

    changed_at: int
    """The Unix timestamp when the widget entered the status."""

    status: Literal["pending", "active", "archived"]
    """The status entered by the widget."""
