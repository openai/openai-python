# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["HostedPlugin"]


class HostedPlugin(BaseModel):
    """A plugin installed from an inline ZIP archive."""

    description: str
    """The installed plugin description."""

    name: str
    """The installed plugin name."""

    type: Literal["inline"]
    """The type of the object. Always `inline`."""
