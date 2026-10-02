# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["ClientDelegationParam"]


class ClientDelegationParam(TypedDict, total=False):
    """Delegate tasks to your application.

    The Live session emits delegation events that your backend handles.
    """

    type: Required[Literal["client"]]
    """The delegation owner. Always `client` for tasks handled by your application."""
