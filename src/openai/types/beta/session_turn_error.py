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
        "rate_limit_exceeded",
        "server_overloaded",
        "cyber_policy",
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
    """A stable, machine-readable failure category.

    - `context_length_exceeded` - The request exceeds the model's context window.
    - `session_budget_exceeded` - The session has reached its usage budget.
    - `usage_limit_exceeded` - The organization has reached a usage, plan, or
      billing limit.
    - `rate_limit_exceeded` - The request exceeds the available rate limit.
    - `server_overloaded` - The model service is temporarily overloaded.
    - `cyber_policy` - The request was rejected by a safety policy.
    - `connection_failed` - The request could not connect to the model service.
    - `server_error` - The model service encountered an unexpected error.
    - `authentication_error` - The API credentials are invalid or lack the required
      access.
    - `invalid_request` - The request contains invalid input or configuration.
    - `resource_not_found` - The requested model or resource is unavailable.
    - `sandbox_error` - The request could not complete in its execution environment.
    - `executor_version_incompatible` - The executor must be upgraded before it can
      run this turn.
    - `active_turn_not_steerable` - The session cannot accept additional input while
      a request is running.
    - `request_timeout` - The request timed out before the model service responded.
    - `internal_error` - An unexpected internal error prevented the session request
      from completing.
    """

    message: str
    """A customer-safe explanation of the failure."""
