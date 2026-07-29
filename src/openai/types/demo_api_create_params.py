# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Required, TypedDict

from .demo_widget_configuration_param import DemoWidgetConfigurationParam

__all__ = ["DemoAPICreateParams"]


class DemoAPICreateParams(TypedDict, total=False):
    configuration: Required[DemoWidgetConfigurationParam]
    """Demo-only configuration applied to a widget."""

    name: Required[str]
    """The human-readable name of the widget."""

    metadata: Dict[str, str]
    """Optional metadata attached to the widget."""
