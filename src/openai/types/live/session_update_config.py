# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .client_delegation import ClientDelegation
from .responses_delegation_update_config import ResponsesDelegationUpdateConfig

__all__ = ["SessionUpdateConfig", "Delegation", "DelegationResponses"]


class DelegationResponses(BaseModel):
    """
    Update the Responses backend for an existing Live session without changing delegation ownership.
    """

    type: Literal["responses"]
    """The delegation owner.

    Always `responses` for tasks handled by the Responses API.
    """

    responses: Optional[ResponsesDelegationUpdateConfig] = None
    """Responses backend settings to update.

    Omitted settings keep their existing values.
    """


Delegation: TypeAlias = Annotated[
    Union[ClientDelegation, DelegationResponses, None], PropertyInfo(discriminator="type")
]


class SessionUpdateConfig(BaseModel):
    """Changes to an active Live session.

    Only delegation backend settings can be updated after startup.
    """

    delegation: Optional[Delegation] = None
    """Delegation settings to update.

    The delegation type must match the current session; omitted settings retain
    their values.
    """
