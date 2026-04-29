# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, TypedDict

from ...._types import SequenceNotStr

__all__ = ["AuditLogListParams", "EffectiveAt"]


class AuditLogListParams(TypedDict, total=False):
    actor_emails: SequenceNotStr[str]
    """Return only events performed by users with these emails."""

    actor_ids: SequenceNotStr[str]
    """Return only events performed by these actors.

    Can be a user ID, a service account ID, or an api key tracking ID.
    """

    after: str
    """A cursor for use in pagination.

    `after` is an object ID that defines your place in the list. For instance, if
    you make a list request and receive 100 objects, ending with obj_foo, your
    subsequent call can include after=obj_foo in order to fetch the next page of the
    list.
    """

    before: str
    """A cursor for use in pagination.

    `before` is an object ID that defines your place in the list. For instance, if
    you make a list request and receive 100 objects, starting with obj_foo, your
    subsequent call can include before=obj_foo in order to fetch the previous page
    of the list.
    """

    effective_at: EffectiveAt
    """Return only events whose `effective_at` (Unix seconds) is in this range."""

    event_types: List[
        Literal[
            "api_key.created",
            "api_key.updated",
            "api_key.deleted",
            "certificate.created",
            "certificate.updated",
            "certificate.deleted",
            "certificates.activated",
            "certificates.deactivated",
            "checkpoint.permission.created",
            "checkpoint.permission.deleted",
            "external_key.registered",
            "external_key.removed",
            "group.created",
            "group.updated",
            "group.deleted",
            "invite.sent",
            "invite.accepted",
            "invite.deleted",
            "ip_allowlist.created",
            "ip_allowlist.updated",
            "ip_allowlist.deleted",
            "ip_allowlist.config.activated",
            "ip_allowlist.config.deactivated",
            "login.succeeded",
            "login.failed",
            "logout.succeeded",
            "logout.failed",
            "organization.updated",
            "project.created",
            "project.updated",
            "project.archived",
            "project.deleted",
            "rate_limit.updated",
            "rate_limit.deleted",
            "resource.deleted",
            "tunnel.created",
            "tunnel.updated",
            "tunnel.deleted",
            "role.created",
            "role.updated",
            "role.deleted",
            "role.assignment.created",
            "role.assignment.deleted",
            "scim.enabled",
            "scim.disabled",
            "service_account.created",
            "service_account.updated",
            "service_account.deleted",
            "user.added",
            "user.updated",
            "user.deleted",
        ]
    ]
    """Return only events with a `type` in one of these values.

    For example, `project.created`. For all options, see the documentation for the
    [audit log object](https://platform.openai.com/docs/api-reference/audit-logs/object).
    """

    limit: int
    """A limit on the number of objects to be returned.

    Limit can range between 1 and 100, and the default is 20.
    """

    project_ids: SequenceNotStr[str]
    """Return only events for these projects."""

    resource_ids: SequenceNotStr[str]
    """Return only events performed on these targets.

    For example, a project ID updated.
    """


class EffectiveAt(TypedDict, total=False):
    """Return only events whose `effective_at` (Unix seconds) is in this range."""

    gt: int
    """
    Return only events whose `effective_at` (Unix seconds) is greater than this
    value.
    """

    gte: int
    """
    Return only events whose `effective_at` (Unix seconds) is greater than or equal
    to this value.
    """

    lt: int
    """Return only events whose `effective_at` (Unix seconds) is less than this value."""

    lte: int
    """
    Return only events whose `effective_at` (Unix seconds) is less than or equal to
    this value.
    """
