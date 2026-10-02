# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal, TypeAlias

__all__ = ["BetaServiceTier"]

BetaServiceTier: TypeAlias = Optional[Literal["auto", "default", "flex", "scale", "priority", "fast", "ultrafast"]]
