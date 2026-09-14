# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

from .inline_capability_source_param import InlineCapabilitySourceParam

__all__ = ["HostedPluginParam"]


class HostedPluginParam(TypedDict, total=False):
    """Supplies a plugin ZIP directly in the session request."""

    description: Required[str]
    """The plugin description declared in `.codex-plugin/plugin.json`."""

    name: Required[str]
    """The plugin name declared in `.codex-plugin/plugin.json`."""

    source: Required[InlineCapabilitySourceParam]
    """Provides ZIP bytes encoded with standard base64."""

    type: Required[Literal["inline"]]
    """The type of the object. Always `inline`."""
