# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = [
    "AuditLogListResponse",
    "Actor",
    "ActorAPIKey",
    "ActorAPIKeyServiceAccount",
    "ActorAPIKeyUser",
    "ActorSession",
    "ActorSessionUser",
    "APIKeyCreated",
    "APIKeyCreatedData",
    "APIKeyDeleted",
    "APIKeyUpdated",
    "APIKeyUpdatedChangesRequested",
    "CertificateCreated",
    "CertificateDeleted",
    "CertificateUpdated",
    "CertificatesActivated",
    "CertificatesActivatedCertificate",
    "CertificatesDeactivated",
    "CertificatesDeactivatedCertificate",
    "CheckpointPermissionCreated",
    "CheckpointPermissionCreatedData",
    "CheckpointPermissionDeleted",
    "ExternalKeyRegistered",
    "ExternalKeyRemoved",
    "GroupCreated",
    "GroupCreatedData",
    "GroupDeleted",
    "GroupUpdated",
    "GroupUpdatedChangesRequested",
    "InviteAccepted",
    "InviteDeleted",
    "InviteSent",
    "InviteSentData",
    "IPAllowlistConfigActivated",
    "IPAllowlistConfigActivatedConfig",
    "IPAllowlistConfigDeactivated",
    "IPAllowlistConfigDeactivatedConfig",
    "IPAllowlistCreated",
    "IPAllowlistDeleted",
    "IPAllowlistUpdated",
    "LoginFailed",
    "LogoutFailed",
    "OrganizationUpdated",
    "OrganizationUpdatedChangesRequested",
    "Project",
    "ProjectArchived",
    "ProjectCreated",
    "ProjectCreatedData",
    "ProjectDeleted",
    "ProjectUpdated",
    "ProjectUpdatedChangesRequested",
    "RateLimitDeleted",
    "RateLimitUpdated",
    "RateLimitUpdatedChangesRequested",
    "RoleAssignmentCreated",
    "RoleAssignmentDeleted",
    "RoleCreated",
    "RoleDeleted",
    "RoleUpdated",
    "RoleUpdatedChangesRequested",
    "ScimDisabled",
    "ScimEnabled",
    "ServiceAccountCreated",
    "ServiceAccountCreatedData",
    "ServiceAccountDeleted",
    "ServiceAccountUpdated",
    "ServiceAccountUpdatedChangesRequested",
    "UserAdded",
    "UserAddedData",
    "UserDeleted",
    "UserUpdated",
    "UserUpdatedChangesRequested",
]


class ActorAPIKeyServiceAccount(BaseModel):
    """The service account that performed the audit logged action."""

    id: Optional[str] = None
    """The service account id."""


class ActorAPIKeyUser(BaseModel):
    """The user who performed the audit logged action."""

    id: Optional[str] = None
    """The user id."""

    email: Optional[str] = None
    """The user email."""


class ActorAPIKey(BaseModel):
    """The API Key used to perform the audit logged action."""

    id: Optional[str] = None
    """The tracking id of the API key."""

    service_account: Optional[ActorAPIKeyServiceAccount] = None
    """The service account that performed the audit logged action."""

    type: Optional[Literal["user", "service_account"]] = None
    """The type of API key. Can be either `user` or `service_account`."""

    user: Optional[ActorAPIKeyUser] = None
    """The user who performed the audit logged action."""


class ActorSessionUser(BaseModel):
    """The user who performed the audit logged action."""

    id: Optional[str] = None
    """The user id."""

    email: Optional[str] = None
    """The user email."""


class ActorSession(BaseModel):
    """The session in which the audit logged action was performed."""

    ip_address: Optional[str] = None
    """The IP address from which the action was performed."""

    user: Optional[ActorSessionUser] = None
    """The user who performed the audit logged action."""


class Actor(BaseModel):
    """The actor who performed the audit logged action."""

    api_key: Optional[ActorAPIKey] = None
    """The API Key used to perform the audit logged action."""

    session: Optional[ActorSession] = None
    """The session in which the audit logged action was performed."""

    type: Optional[Literal["session", "api_key"]] = None
    """The type of actor. Is either `session` or `api_key`."""


class APIKeyCreatedData(BaseModel):
    """The payload used to create the API key."""

    scopes: Optional[List[str]] = None
    """A list of scopes allowed for the API key, e.g. `["api.model.request"]`"""


class APIKeyCreated(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The tracking ID of the API key."""

    data: Optional[APIKeyCreatedData] = None
    """The payload used to create the API key."""


class APIKeyDeleted(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The tracking ID of the API key."""


class APIKeyUpdatedChangesRequested(BaseModel):
    """The payload used to update the API key."""

    scopes: Optional[List[str]] = None
    """A list of scopes allowed for the API key, e.g. `["api.model.request"]`"""


class APIKeyUpdated(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The tracking ID of the API key."""

    changes_requested: Optional[APIKeyUpdatedChangesRequested] = None
    """The payload used to update the API key."""


class CertificateCreated(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The certificate ID."""

    name: Optional[str] = None
    """The name of the certificate."""


class CertificateDeleted(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The certificate ID."""

    certificate: Optional[str] = None
    """The certificate content in PEM format."""

    name: Optional[str] = None
    """The name of the certificate."""


class CertificateUpdated(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The certificate ID."""

    name: Optional[str] = None
    """The name of the certificate."""


class CertificatesActivatedCertificate(BaseModel):
    id: Optional[str] = None
    """The certificate ID."""

    name: Optional[str] = None
    """The name of the certificate."""


class CertificatesActivated(BaseModel):
    """The details for events with this `type`."""

    certificates: Optional[List[CertificatesActivatedCertificate]] = None


class CertificatesDeactivatedCertificate(BaseModel):
    id: Optional[str] = None
    """The certificate ID."""

    name: Optional[str] = None
    """The name of the certificate."""


class CertificatesDeactivated(BaseModel):
    """The details for events with this `type`."""

    certificates: Optional[List[CertificatesDeactivatedCertificate]] = None


class CheckpointPermissionCreatedData(BaseModel):
    """The payload used to create the checkpoint permission."""

    fine_tuned_model_checkpoint: Optional[str] = None
    """The ID of the fine-tuned model checkpoint."""

    project_id: Optional[str] = None
    """The ID of the project that the checkpoint permission was created for."""


class CheckpointPermissionCreated(BaseModel):
    """
    The project and fine-tuned model checkpoint that the checkpoint permission was created for.
    """

    id: Optional[str] = None
    """The ID of the checkpoint permission."""

    data: Optional[CheckpointPermissionCreatedData] = None
    """The payload used to create the checkpoint permission."""


class CheckpointPermissionDeleted(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The ID of the checkpoint permission."""


class ExternalKeyRegistered(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The ID of the external key configuration."""

    data: Optional[object] = None
    """The configuration for the external key."""


class ExternalKeyRemoved(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The ID of the external key configuration."""


class GroupCreatedData(BaseModel):
    """Information about the created group."""

    group_name: Optional[str] = None
    """The group name."""


class GroupCreated(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The ID of the group."""

    data: Optional[GroupCreatedData] = None
    """Information about the created group."""


class GroupDeleted(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The ID of the group."""


class GroupUpdatedChangesRequested(BaseModel):
    """The payload used to update the group."""

    group_name: Optional[str] = None
    """The updated group name."""


class GroupUpdated(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The ID of the group."""

    changes_requested: Optional[GroupUpdatedChangesRequested] = None
    """The payload used to update the group."""


class InviteAccepted(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The ID of the invite."""


class InviteDeleted(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The ID of the invite."""


class InviteSentData(BaseModel):
    """The payload used to create the invite."""

    email: Optional[str] = None
    """The email invited to the organization."""

    role: Optional[str] = None
    """The role the email was invited to be. Is either `owner` or `member`."""


class InviteSent(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The ID of the invite."""

    data: Optional[InviteSentData] = None
    """The payload used to create the invite."""


class IPAllowlistConfigActivatedConfig(BaseModel):
    id: Optional[str] = None
    """The ID of the IP allowlist configuration."""

    name: Optional[str] = None
    """The name of the IP allowlist configuration."""


class IPAllowlistConfigActivated(BaseModel):
    """The details for events with this `type`."""

    configs: Optional[List[IPAllowlistConfigActivatedConfig]] = None
    """The configurations that were activated."""


class IPAllowlistConfigDeactivatedConfig(BaseModel):
    id: Optional[str] = None
    """The ID of the IP allowlist configuration."""

    name: Optional[str] = None
    """The name of the IP allowlist configuration."""


class IPAllowlistConfigDeactivated(BaseModel):
    """The details for events with this `type`."""

    configs: Optional[List[IPAllowlistConfigDeactivatedConfig]] = None
    """The configurations that were deactivated."""


class IPAllowlistCreated(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The ID of the IP allowlist configuration."""

    allowed_ips: Optional[List[str]] = None
    """The IP addresses or CIDR ranges included in the configuration."""

    name: Optional[str] = None
    """The name of the IP allowlist configuration."""


class IPAllowlistDeleted(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The ID of the IP allowlist configuration."""

    allowed_ips: Optional[List[str]] = None
    """The IP addresses or CIDR ranges that were in the configuration."""

    name: Optional[str] = None
    """The name of the IP allowlist configuration."""


class IPAllowlistUpdated(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The ID of the IP allowlist configuration."""

    allowed_ips: Optional[List[str]] = None
    """The updated set of IP addresses or CIDR ranges in the configuration."""


class LoginFailed(BaseModel):
    """The details for events with this `type`."""

    error_code: Optional[str] = None
    """The error code of the failure."""

    error_message: Optional[str] = None
    """The error message of the failure."""


class LogoutFailed(BaseModel):
    """The details for events with this `type`."""

    error_code: Optional[str] = None
    """The error code of the failure."""

    error_message: Optional[str] = None
    """The error message of the failure."""


class OrganizationUpdatedChangesRequested(BaseModel):
    """The payload used to update the organization settings."""

    api_call_logging: Optional[str] = None
    """How your organization logs data from supported API calls.

    One of `disabled`, `enabled_per_call`, `enabled_for_all_projects`, or
    `enabled_for_selected_projects`
    """

    api_call_logging_project_ids: Optional[str] = None
    """
    The list of project ids if api_call_logging is set to
    `enabled_for_selected_projects`
    """

    description: Optional[str] = None
    """The organization description."""

    name: Optional[str] = None
    """The organization name."""

    threads_ui_visibility: Optional[str] = None
    """
    Visibility of the threads page which shows messages created with the Assistants
    API and Playground. One of `ANY_ROLE`, `OWNERS`, or `NONE`.
    """

    title: Optional[str] = None
    """The organization title."""

    usage_dashboard_visibility: Optional[str] = None
    """
    Visibility of the usage dashboard which shows activity and costs for your
    organization. One of `ANY_ROLE` or `OWNERS`.
    """


class OrganizationUpdated(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The organization ID."""

    changes_requested: Optional[OrganizationUpdatedChangesRequested] = None
    """The payload used to update the organization settings."""


class Project(BaseModel):
    """The project that the action was scoped to.

    Absent for actions not scoped to projects. Note that any admin actions taken via Admin API keys are associated with the default project.
    """

    id: Optional[str] = None
    """The project ID."""

    name: Optional[str] = None
    """The project title."""


class ProjectArchived(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The project ID."""


class ProjectCreatedData(BaseModel):
    """The payload used to create the project."""

    name: Optional[str] = None
    """The project name."""

    title: Optional[str] = None
    """The title of the project as seen on the dashboard."""


class ProjectCreated(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The project ID."""

    data: Optional[ProjectCreatedData] = None
    """The payload used to create the project."""


class ProjectDeleted(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The project ID."""


class ProjectUpdatedChangesRequested(BaseModel):
    """The payload used to update the project."""

    title: Optional[str] = None
    """The title of the project as seen on the dashboard."""


class ProjectUpdated(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The project ID."""

    changes_requested: Optional[ProjectUpdatedChangesRequested] = None
    """The payload used to update the project."""


class RateLimitDeleted(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The rate limit ID"""


class RateLimitUpdatedChangesRequested(BaseModel):
    """The payload used to update the rate limits."""

    batch_1_day_max_input_tokens: Optional[int] = None
    """The maximum batch input tokens per day. Only relevant for certain models."""

    max_audio_megabytes_per_1_minute: Optional[int] = None
    """The maximum audio megabytes per minute. Only relevant for certain models."""

    max_images_per_1_minute: Optional[int] = None
    """The maximum images per minute. Only relevant for certain models."""

    max_requests_per_1_day: Optional[int] = None
    """The maximum requests per day. Only relevant for certain models."""

    max_requests_per_1_minute: Optional[int] = None
    """The maximum requests per minute."""

    max_tokens_per_1_minute: Optional[int] = None
    """The maximum tokens per minute."""


class RateLimitUpdated(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The rate limit ID"""

    changes_requested: Optional[RateLimitUpdatedChangesRequested] = None
    """The payload used to update the rate limits."""


class RoleAssignmentCreated(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The identifier of the role assignment."""

    principal_id: Optional[str] = None
    """The principal (user or group) that received the role."""

    principal_type: Optional[str] = None
    """The type of principal (user or group) that received the role."""

    resource_id: Optional[str] = None
    """The resource the role assignment is scoped to."""

    resource_type: Optional[str] = None
    """The type of resource the role assignment is scoped to."""


class RoleAssignmentDeleted(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The identifier of the role assignment."""

    principal_id: Optional[str] = None
    """The principal (user or group) that had the role removed."""

    principal_type: Optional[str] = None
    """The type of principal (user or group) that had the role removed."""

    resource_id: Optional[str] = None
    """The resource the role assignment was scoped to."""

    resource_type: Optional[str] = None
    """The type of resource the role assignment was scoped to."""


class RoleCreated(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The role ID."""

    permissions: Optional[List[str]] = None
    """The permissions granted by the role."""

    resource_id: Optional[str] = None
    """The resource the role is scoped to."""

    resource_type: Optional[str] = None
    """The type of resource the role belongs to."""

    role_name: Optional[str] = None
    """The name of the role."""


class RoleDeleted(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The role ID."""


class RoleUpdatedChangesRequested(BaseModel):
    """The payload used to update the role."""

    description: Optional[str] = None
    """The updated role description, when provided."""

    metadata: Optional[object] = None
    """Additional metadata stored on the role."""

    permissions_added: Optional[List[str]] = None
    """The permissions added to the role."""

    permissions_removed: Optional[List[str]] = None
    """The permissions removed from the role."""

    resource_id: Optional[str] = None
    """The resource the role is scoped to."""

    resource_type: Optional[str] = None
    """The type of resource the role belongs to."""

    role_name: Optional[str] = None
    """The updated role name, when provided."""


class RoleUpdated(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The role ID."""

    changes_requested: Optional[RoleUpdatedChangesRequested] = None
    """The payload used to update the role."""


class ScimDisabled(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The ID of the SCIM was disabled for."""


class ScimEnabled(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The ID of the SCIM was enabled for."""


class ServiceAccountCreatedData(BaseModel):
    """The payload used to create the service account."""

    role: Optional[str] = None
    """The role of the service account. Is either `owner` or `member`."""


class ServiceAccountCreated(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The service account ID."""

    data: Optional[ServiceAccountCreatedData] = None
    """The payload used to create the service account."""


class ServiceAccountDeleted(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The service account ID."""


class ServiceAccountUpdatedChangesRequested(BaseModel):
    """The payload used to updated the service account."""

    role: Optional[str] = None
    """The role of the service account. Is either `owner` or `member`."""


class ServiceAccountUpdated(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The service account ID."""

    changes_requested: Optional[ServiceAccountUpdatedChangesRequested] = None
    """The payload used to updated the service account."""


class UserAddedData(BaseModel):
    """The payload used to add the user to the project."""

    role: Optional[str] = None
    """The role of the user. Is either `owner` or `member`."""


class UserAdded(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The user ID."""

    data: Optional[UserAddedData] = None
    """The payload used to add the user to the project."""


class UserDeleted(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The user ID."""


class UserUpdatedChangesRequested(BaseModel):
    """The payload used to update the user."""

    role: Optional[str] = None
    """The role of the user. Is either `owner` or `member`."""


class UserUpdated(BaseModel):
    """The details for events with this `type`."""

    id: Optional[str] = None
    """The project ID."""

    changes_requested: Optional[UserUpdatedChangesRequested] = None
    """The payload used to update the user."""


class AuditLogListResponse(BaseModel):
    """A log of a user action or configuration change within this organization."""

    id: str
    """The ID of this log."""

    effective_at: int
    """The Unix timestamp (in seconds) of the event."""

    type: Literal[
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
    """The event type."""

    actor: Optional[Actor] = None
    """The actor who performed the audit logged action."""

    api_key_created: Optional[APIKeyCreated] = FieldInfo(alias="api_key.created", default=None)
    """The details for events with this `type`."""

    api_key_deleted: Optional[APIKeyDeleted] = FieldInfo(alias="api_key.deleted", default=None)
    """The details for events with this `type`."""

    api_key_updated: Optional[APIKeyUpdated] = FieldInfo(alias="api_key.updated", default=None)
    """The details for events with this `type`."""

    certificate_created: Optional[CertificateCreated] = FieldInfo(alias="certificate.created", default=None)
    """The details for events with this `type`."""

    certificate_deleted: Optional[CertificateDeleted] = FieldInfo(alias="certificate.deleted", default=None)
    """The details for events with this `type`."""

    certificate_updated: Optional[CertificateUpdated] = FieldInfo(alias="certificate.updated", default=None)
    """The details for events with this `type`."""

    certificates_activated: Optional[CertificatesActivated] = FieldInfo(alias="certificates.activated", default=None)
    """The details for events with this `type`."""

    certificates_deactivated: Optional[CertificatesDeactivated] = FieldInfo(
        alias="certificates.deactivated", default=None
    )
    """The details for events with this `type`."""

    checkpoint_permission_created: Optional[CheckpointPermissionCreated] = FieldInfo(
        alias="checkpoint.permission.created", default=None
    )
    """
    The project and fine-tuned model checkpoint that the checkpoint permission was
    created for.
    """

    checkpoint_permission_deleted: Optional[CheckpointPermissionDeleted] = FieldInfo(
        alias="checkpoint.permission.deleted", default=None
    )
    """The details for events with this `type`."""

    external_key_registered: Optional[ExternalKeyRegistered] = FieldInfo(alias="external_key.registered", default=None)
    """The details for events with this `type`."""

    external_key_removed: Optional[ExternalKeyRemoved] = FieldInfo(alias="external_key.removed", default=None)
    """The details for events with this `type`."""

    group_created: Optional[GroupCreated] = FieldInfo(alias="group.created", default=None)
    """The details for events with this `type`."""

    group_deleted: Optional[GroupDeleted] = FieldInfo(alias="group.deleted", default=None)
    """The details for events with this `type`."""

    group_updated: Optional[GroupUpdated] = FieldInfo(alias="group.updated", default=None)
    """The details for events with this `type`."""

    invite_accepted: Optional[InviteAccepted] = FieldInfo(alias="invite.accepted", default=None)
    """The details for events with this `type`."""

    invite_deleted: Optional[InviteDeleted] = FieldInfo(alias="invite.deleted", default=None)
    """The details for events with this `type`."""

    invite_sent: Optional[InviteSent] = FieldInfo(alias="invite.sent", default=None)
    """The details for events with this `type`."""

    ip_allowlist_config_activated: Optional[IPAllowlistConfigActivated] = FieldInfo(
        alias="ip_allowlist.config.activated", default=None
    )
    """The details for events with this `type`."""

    ip_allowlist_config_deactivated: Optional[IPAllowlistConfigDeactivated] = FieldInfo(
        alias="ip_allowlist.config.deactivated", default=None
    )
    """The details for events with this `type`."""

    ip_allowlist_created: Optional[IPAllowlistCreated] = FieldInfo(alias="ip_allowlist.created", default=None)
    """The details for events with this `type`."""

    ip_allowlist_deleted: Optional[IPAllowlistDeleted] = FieldInfo(alias="ip_allowlist.deleted", default=None)
    """The details for events with this `type`."""

    ip_allowlist_updated: Optional[IPAllowlistUpdated] = FieldInfo(alias="ip_allowlist.updated", default=None)
    """The details for events with this `type`."""

    login_failed: Optional[LoginFailed] = FieldInfo(alias="login.failed", default=None)
    """The details for events with this `type`."""

    login_succeeded: Optional[object] = FieldInfo(alias="login.succeeded", default=None)
    """This event has no additional fields beyond the standard audit log attributes."""

    logout_failed: Optional[LogoutFailed] = FieldInfo(alias="logout.failed", default=None)
    """The details for events with this `type`."""

    logout_succeeded: Optional[object] = FieldInfo(alias="logout.succeeded", default=None)
    """This event has no additional fields beyond the standard audit log attributes."""

    organization_updated: Optional[OrganizationUpdated] = FieldInfo(alias="organization.updated", default=None)
    """The details for events with this `type`."""

    project: Optional[Project] = None
    """The project that the action was scoped to.

    Absent for actions not scoped to projects. Note that any admin actions taken via
    Admin API keys are associated with the default project.
    """

    project_archived: Optional[ProjectArchived] = FieldInfo(alias="project.archived", default=None)
    """The details for events with this `type`."""

    project_created: Optional[ProjectCreated] = FieldInfo(alias="project.created", default=None)
    """The details for events with this `type`."""

    project_deleted: Optional[ProjectDeleted] = FieldInfo(alias="project.deleted", default=None)
    """The details for events with this `type`."""

    project_updated: Optional[ProjectUpdated] = FieldInfo(alias="project.updated", default=None)
    """The details for events with this `type`."""

    rate_limit_deleted: Optional[RateLimitDeleted] = FieldInfo(alias="rate_limit.deleted", default=None)
    """The details for events with this `type`."""

    rate_limit_updated: Optional[RateLimitUpdated] = FieldInfo(alias="rate_limit.updated", default=None)
    """The details for events with this `type`."""

    role_assignment_created: Optional[RoleAssignmentCreated] = FieldInfo(alias="role.assignment.created", default=None)
    """The details for events with this `type`."""

    role_assignment_deleted: Optional[RoleAssignmentDeleted] = FieldInfo(alias="role.assignment.deleted", default=None)
    """The details for events with this `type`."""

    role_created: Optional[RoleCreated] = FieldInfo(alias="role.created", default=None)
    """The details for events with this `type`."""

    role_deleted: Optional[RoleDeleted] = FieldInfo(alias="role.deleted", default=None)
    """The details for events with this `type`."""

    role_updated: Optional[RoleUpdated] = FieldInfo(alias="role.updated", default=None)
    """The details for events with this `type`."""

    scim_disabled: Optional[ScimDisabled] = FieldInfo(alias="scim.disabled", default=None)
    """The details for events with this `type`."""

    scim_enabled: Optional[ScimEnabled] = FieldInfo(alias="scim.enabled", default=None)
    """The details for events with this `type`."""

    service_account_created: Optional[ServiceAccountCreated] = FieldInfo(alias="service_account.created", default=None)
    """The details for events with this `type`."""

    service_account_deleted: Optional[ServiceAccountDeleted] = FieldInfo(alias="service_account.deleted", default=None)
    """The details for events with this `type`."""

    service_account_updated: Optional[ServiceAccountUpdated] = FieldInfo(alias="service_account.updated", default=None)
    """The details for events with this `type`."""

    user_added: Optional[UserAdded] = FieldInfo(alias="user.added", default=None)
    """The details for events with this `type`."""

    user_deleted: Optional[UserDeleted] = FieldInfo(alias="user.deleted", default=None)
    """The details for events with this `type`."""

    user_updated: Optional[UserUpdated] = FieldInfo(alias="user.updated", default=None)
    """The details for events with this `type`."""
