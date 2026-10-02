# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ClientDelegation"]


class ClientDelegation(BaseModel):
    """Delegate tasks to your application.

    The Live session emits delegation events that your backend handles.
    """

    type: Literal["client"]
    """The delegation owner. Always `client` for tasks handled by your application."""
