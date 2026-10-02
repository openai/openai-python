# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["SessionTurnError"]


class SessionTurnError(BaseModel):
    """A customer-safe error describing why a session request failed."""

    code: Literal[
        "context_length_exceeded",
        "session_budget_exceeded",
        "usage_limit_exceeded",
        "credit_balance_exhausted",
        "rate_limit_exceeded",
        "flex_unavailable",
        "server_overloaded",
        "cyber_policy",
        "misalignment_policy_violation",
        "connection_failed",
        "server_error",
        "authentication_error",
        "invalid_request",
        "resource_not_found",
        "sandbox_error",
        "executor_version_incompatible",
        "active_turn_not_steerable",
        "request_timeout",
        "internal_error",
    ]
    """A stable, machine-readable failure category."""

    message: str
    """A customer-safe explanation of the failure."""
