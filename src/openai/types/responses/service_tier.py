# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal, TypeAlias

__all__ = ["ServiceTier"]

ServiceTier: TypeAlias = Optional[Literal["auto", "default", "flex", "scale", "priority", "fast", "ultrafast"]]
