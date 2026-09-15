# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal, TypeAlias

__all__ = ["BetaResponseStatus"]

BetaResponseStatus: TypeAlias = Literal["completed", "failed", "in_progress", "cancelled", "queued", "incomplete"]
