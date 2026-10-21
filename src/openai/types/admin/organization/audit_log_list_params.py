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
            "workload_identity_provider.created",
            "workload_identity_provider.updated",
            "workload_identity_provider.deleted",
            "workload_identity_provider_mapping.created",
            "workload_identity_provider_mapping.updated",
            "workload_identity_provider_mapping.deleted",
            "role.created",
            "role.updated",
            "role.deleted",
            "role.assignment.created",
            "role.assignment.deleted",
            "role.bound_to_resource",
            "role.unbound_from_resource",
            "scim.enabled",
            "scim.disabled",
            "service_account.created",
            "service_account.updated",
            "service_account.deleted",
            "user.added",
            "user.updated",
            "user.deleted",
            "tenant.metadata.updated",
            "tenant.microsoft_entra_mapping.upserted",
            "tenant.microsoft_entra_mapping.deleted",
            "tenant.workload_identity.provider.created",
            "tenant.workload_identity.provider.updated",
            "tenant.workload_identity.provider.archived",
            "tenant.workload_identity.mapping.created",
            "tenant.workload_identity.mapping.updated",
            "tenant.workload_identity.mapping.archived",
            "tenant.workload_identity.binding.created",
            "tenant.workload_identity.principal.provisioned",
            "tenant.admin_api_key.created",
            "tenant.admin_api_key.updated",
            "tenant.admin_api_key.deleted",
            "tenant.project_api_key.created",
            "tenant.chatgpt_access_token.revoked",
            "tenant.migration.completed",
            "tenant.sso.migrated",
            "tenant.domains.migrated",
            "tenant.sso_connection.created",
            "tenant.sso_connection.updated",
            "tenant.sso_connection.deleted",
            "tenant.sso_connection.setup.started",
            "tenant.policy.created",
            "tenant.policy.updated",
            "tenant.policy.deleted",
            "tenant.policy.attached",
            "tenant.policy.detached",
            "tenant.principal_authentication_policy.resolved",
            "tenant.scim.setup.started",
            "tenant.scim.deletion.requested",
            "tenant.scim.directory.created",
            "tenant.product_access_policy.updated",
            "tenant.resource_share_grant.created",
            "tenant.resource_share_grant.updated",
            "tenant.resource_share_grant.accepted",
            "tenant.resource_share_grant.declined",
            "tenant.resource_share_grant.revoked",
            "tenant.resource_share_grant.deleted",
            "tenant.service_account.updated",
            "tenant.service_account.deleted",
            "tenant.service_account.token.revoked",
            "tenant.billing.overage_limit.updated",
            "tenant.billing.alerts.updated",
            "tenant.billing.info.updated",
            "tenant.usage_limit.workspace.updated",
            "tenant.usage_limit.group.updated",
            "tenant.usage_limit.user.updated",
            "tenant.usage_limit.increase_request.updated",
            "tenant.usage_limit.increase_request.resolved",
            "tenant.group.created",
            "tenant.group.updated",
            "tenant.group.deleted",
            "tenant.group.member.added",
            "tenant.group.member.removed",
            "tenant.migration_rollout.status.updated",
            "tenant.migration_rollout.tier.updated",
            "tenant.role.metadata.updated",
            "tenant.custom_role.created",
            "tenant.custom_role.updated",
            "tenant.custom_role.deleted",
            "tenant.role_assignment.created",
            "tenant.role_assignment.deleted",
            "tenant.resource_role_assignment.created",
            "tenant.resource_role_assignment.deleted",
            "tenant.resource_access.updated",
            "tenant.resource_access.deleted",
            "tenant.session_policy.created",
            "tenant.session_policy.updated",
            "tenant.session_policy.deleted",
            "tenant.session_revocation.started",
            "tenant.third_party_app_policy.updated",
            "tenant.user.added",
            "tenant.user.updated",
            "tenant.user.removed",
            "tenant.user.looked_up",
            "tenant.user.invited",
            "tenant.membership.revoked",
            "tenant.api_organization_invite.upserted",
            "tenant.api_organization_invite.deleted",
            "tenant.chatgpt_workspace_invite.upserted",
            "tenant.membership.accepted",
            "tenant.membership.declined",
            "tenant.workspace_invite_email_settings.updated",
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

    For example, a project ID updated. For ChatGPT connector role events, use the
    workspace connector resource ID shown in `details.id`, such as
    `<workspace_id>__<connector_id>`.
    """

    tenant_only: bool
    """Return only tenant-scoped events associated with this organization.

    Required for tenant-scoped events such as `role.bound_to_resource` and
    `role.unbound_from_resource`. When `true`, all supplied event types must be
    tenant-scoped.
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
