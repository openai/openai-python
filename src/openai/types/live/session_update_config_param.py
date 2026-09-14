# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .client_delegation_param import ClientDelegationParam
from .responses_delegation_update_config_param import ResponsesDelegationUpdateConfigParam

__all__ = ["SessionUpdateConfigParam", "Delegation", "DelegationResponses"]


class DelegationResponses(TypedDict, total=False):
    """
    Update the Responses backend for an existing Live session without changing delegation ownership.
    """

    type: Required[Literal["responses"]]
    """The delegation owner.

    Always `responses` for tasks handled by the Responses API.
    """

    responses: ResponsesDelegationUpdateConfigParam
    """Responses backend settings to update.

    Omitted settings keep their existing values.
    """


Delegation: TypeAlias = Union[ClientDelegationParam, DelegationResponses]


class SessionUpdateConfigParam(TypedDict, total=False):
    """Changes to an active Live session.

    Only delegation backend settings can be updated after startup.
    """

    delegation: Optional[Delegation]
    """Delegation settings to update.

    The delegation type must match the current session; omitted settings retain
    their values.
    """
