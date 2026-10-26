# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel
from .decision_trigger import DecisionTrigger
from .client_delegation import ClientDelegation
from .decisions_delegation_update_config import DecisionsDelegationUpdateConfig
from .responses_delegation_update_config import ResponsesDelegationUpdateConfig

__all__ = ["SessionUpdateConfig", "Delegation", "DelegationResponses", "DelegationDecisions"]


class DelegationResponses(BaseModel):
    """
    Update the Responses backend for an existing Live session without changing delegation ownership.
    """

    type: Literal["responses"]
    """The delegation owner.

    Always `responses` for tasks handled by the Responses API.
    """

    acknowledgement_delay_ms: Optional[int] = None
    """
    Milliseconds to wait before requesting an automatic spoken acknowledgement for a
    delegation. The model may still speak before this delay. Any commentary or
    thinking appended to the session cancels all pending acknowledgements, including
    those for other delegations. Defaults to 400 for Decisions sessions and 0
    (request immediately) for other sessions. Omission in a session update preserves
    the current value. Updates apply to subsequent delegations.
    """

    responses: Optional[ResponsesDelegationUpdateConfig] = None
    """Responses backend settings to update.

    Omitted settings keep their existing values.
    """


class DelegationDecisions(BaseModel):
    type: Literal["decisions"]

    acknowledgement_delay_ms: Optional[int] = None
    """
    Milliseconds to wait before requesting an automatic spoken acknowledgement for a
    delegation. The model may still speak before this delay. Any commentary or
    thinking appended to the session cancels all pending acknowledgements, including
    those for other delegations. Defaults to 400 for Decisions sessions and 0
    (request immediately) for other sessions. Omission in a session update preserves
    the current value. Updates apply to subsequent delegations.
    """

    decisions: Optional[DecisionsDelegationUpdateConfig] = None


Delegation: TypeAlias = Annotated[
    Union[ClientDelegation, DelegationResponses, DelegationDecisions, None], PropertyInfo(discriminator="type")
]


class SessionUpdateConfig(BaseModel):
    """
    Changes to an active Live session's delegation settings and transcript triggers.
    """

    delegation: Optional[Delegation] = None
    """Delegation settings to update.

    The delegation type must match the current session; omitted settings retain
    their values.
    """

    triggers: Optional[List[DecisionTrigger]] = None
    """At most one Decisions trigger per transcript event type.

    Triggers run independently of delegation. On update, omit triggers to keep the
    current configuration, send a list to replace it, or send an empty list to
    disable triggers.
    """
