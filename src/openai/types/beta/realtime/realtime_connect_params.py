from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["RealtimeConnectParams"]


class RealtimeConnectParams(TypedDict, total=False):
    model: Required[str]
