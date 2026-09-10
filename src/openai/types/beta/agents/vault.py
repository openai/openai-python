# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from typing_extensions import Literal

from ...._models import BaseModel

__all__ = ["Vault"]


class Vault(BaseModel):
    """
    A collection of credentials that agent tools can use to authenticate to MCP servers.
    """

    id: str
    """The ID of the vault."""

    created_at: int
    """The Unix timestamp, in seconds, when the vault was created."""

    metadata: Dict[str, str]
    """
    Key-value pairs associated with the vault, such as an application or team
    identifier.
    """

    name: Optional[str] = None
    """The human-readable name of the vault, if set."""

    object: Literal["vault"]
    """The object type. Always `vault`."""
