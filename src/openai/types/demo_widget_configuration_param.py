# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Literal, Required, TypedDict

__all__ = ["DemoWidgetConfigurationParam"]


class DemoWidgetConfigurationParam(TypedDict, total=False):
    """Demo-only configuration applied to a widget."""

    priority: Required[int]
    """The scheduling priority of the widget."""

    region: Required[Literal["us-east", "us-west", "eu-west"]]
    """The region used by the widget."""

    labels: Dict[str, str]
    """User-defined labels attached to the widget."""
