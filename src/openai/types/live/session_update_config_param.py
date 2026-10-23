# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, TypeAlias, TypedDict

from .decision_trigger_param import DecisionTriggerParam
from .client_delegation_param import ClientDelegationParam
from .decisions_delegation_update_config_param import DecisionsDelegationUpdateConfigParam
from .responses_delegation_update_config_param import ResponsesDelegationUpdateConfigParam

__all__ = ["SessionUpdateConfigParam", "Delegation", "DelegationResponses", "DelegationDecisions"]


class DelegationResponses(TypedDict, total=False):
    """
    Update the Responses backend for an existing Live session without changing delegation ownership.
    """

    type: Required[Literal["responses"]]
    """The delegation owner.

    Always `responses` for tasks handled by the Responses API.
    """

    acknowledgement_delay_ms: int
    """
    Milliseconds to wait before requesting an automatic spoken acknowledgement for a
    delegation. The model may still speak before this delay. Any commentary or
    thinking appended to the session cancels all pending acknowledgements, including
    those for other delegations. Defaults to 400 for Decisions sessions and 0
    (request immediately) for other sessions. Omission in a session update preserves
    the current value. Updates apply to subsequent delegations.
    """

    responses: ResponsesDelegationUpdateConfigParam
    """Responses backend settings to update.

    Omitted settings keep their existing values.
    """


class DelegationDecisions(TypedDict, total=False):
    type: Required[Literal["decisions"]]

    acknowledgement_delay_ms: int
    """
    Milliseconds to wait before requesting an automatic spoken acknowledgement for a
    delegation. The model may still speak before this delay. Any commentary or
    thinking appended to the session cancels all pending acknowledgements, including
    those for other delegations. Defaults to 400 for Decisions sessions and 0
    (request immediately) for other sessions. Omission in a session update preserves
    the current value. Updates apply to subsequent delegations.
    """

    decisions: DecisionsDelegationUpdateConfigParam


Delegation: TypeAlias = Union[ClientDelegationParam, DelegationResponses, DelegationDecisions]


class SessionUpdateConfigParam(TypedDict, total=False):
    """
    Changes to an active Live session's delegation settings and transcript triggers.
    """

    delegation: Optional[Delegation]
    """Delegation settings to update.

    The delegation type must match the current session; omitted settings retain
    their values.
    """

    triggers: Iterable[DecisionTriggerParam]
    """At most one Decisions trigger per transcript event type.

    Triggers run independently of delegation. On update, omit triggers to keep the
    current configuration, send a list to replace it, or send an empty list to
    disable triggers.
    """
