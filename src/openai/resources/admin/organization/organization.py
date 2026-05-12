# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .roles import (
    Roles,
    AsyncRoles,
    RolesWithRawResponse,
    AsyncRolesWithRawResponse,
    RolesWithStreamingResponse,
    AsyncRolesWithStreamingResponse,
)
from .usage import (
    Usage,
    AsyncUsage,
    UsageWithRawResponse,
    AsyncUsageWithRawResponse,
    UsageWithStreamingResponse,
    AsyncUsageWithStreamingResponse,
)
from .invites import (
    Invites,
    AsyncInvites,
    InvitesWithRawResponse,
    AsyncInvitesWithRawResponse,
    InvitesWithStreamingResponse,
    AsyncInvitesWithStreamingResponse,
)
from ...._compat import cached_property
from .audit_logs import (
    AuditLogs,
    AsyncAuditLogs,
    AuditLogsWithRawResponse,
    AsyncAuditLogsWithRawResponse,
    AuditLogsWithStreamingResponse,
    AsyncAuditLogsWithStreamingResponse,
)
from .users.users import (
    Users,
    AsyncUsers,
    UsersWithRawResponse,
    AsyncUsersWithRawResponse,
    UsersWithStreamingResponse,
    AsyncUsersWithStreamingResponse,
)
from ...._resource import SyncAPIResource, AsyncAPIResource
from .certificates import (
    Certificates,
    AsyncCertificates,
    CertificatesWithRawResponse,
    AsyncCertificatesWithRawResponse,
    CertificatesWithStreamingResponse,
    AsyncCertificatesWithStreamingResponse,
)
from .groups.groups import (
    Groups,
    AsyncGroups,
    GroupsWithRawResponse,
    AsyncGroupsWithRawResponse,
    GroupsWithStreamingResponse,
    AsyncGroupsWithStreamingResponse,
)
from .admin_api_keys import (
    AdminAPIKeys,
    AsyncAdminAPIKeys,
    AdminAPIKeysWithRawResponse,
    AsyncAdminAPIKeysWithRawResponse,
    AdminAPIKeysWithStreamingResponse,
    AsyncAdminAPIKeysWithStreamingResponse,
)
from .projects.projects import (
    Projects,
    AsyncProjects,
    ProjectsWithRawResponse,
    AsyncProjectsWithRawResponse,
    ProjectsWithStreamingResponse,
    AsyncProjectsWithStreamingResponse,
)

__all__ = ["Organization", "AsyncOrganization"]


class Organization(SyncAPIResource):
    @cached_property
    def audit_logs(self) -> AuditLogs:
        """List user actions and configuration changes within this organization."""
        return AuditLogs(self._client)

    @cached_property
    def admin_api_keys(self) -> AdminAPIKeys:
        return AdminAPIKeys(self._client)

    @cached_property
    def usage(self) -> Usage:
        return Usage(self._client)

    @cached_property
    def invites(self) -> Invites:
        return Invites(self._client)

    @cached_property
    def users(self) -> Users:
        return Users(self._client)

    @cached_property
    def groups(self) -> Groups:
        return Groups(self._client)

    @cached_property
    def roles(self) -> Roles:
        return Roles(self._client)

    @cached_property
    def certificates(self) -> Certificates:
        return Certificates(self._client)

    @cached_property
    def projects(self) -> Projects:
        return Projects(self._client)

    @cached_property
    def with_raw_response(self) -> OrganizationWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return OrganizationWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OrganizationWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return OrganizationWithStreamingResponse(self)


class AsyncOrganization(AsyncAPIResource):
    @cached_property
    def audit_logs(self) -> AsyncAuditLogs:
        """List user actions and configuration changes within this organization."""
        return AsyncAuditLogs(self._client)

    @cached_property
    def admin_api_keys(self) -> AsyncAdminAPIKeys:
        return AsyncAdminAPIKeys(self._client)

    @cached_property
    def usage(self) -> AsyncUsage:
        return AsyncUsage(self._client)

    @cached_property
    def invites(self) -> AsyncInvites:
        return AsyncInvites(self._client)

    @cached_property
    def users(self) -> AsyncUsers:
        return AsyncUsers(self._client)

    @cached_property
    def groups(self) -> AsyncGroups:
        return AsyncGroups(self._client)

    @cached_property
    def roles(self) -> AsyncRoles:
        return AsyncRoles(self._client)

    @cached_property
    def certificates(self) -> AsyncCertificates:
        return AsyncCertificates(self._client)

    @cached_property
    def projects(self) -> AsyncProjects:
        return AsyncProjects(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncOrganizationWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncOrganizationWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOrganizationWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncOrganizationWithStreamingResponse(self)


class OrganizationWithRawResponse:
    def __init__(self, organization: Organization) -> None:
        self._organization = organization

    @cached_property
    def audit_logs(self) -> AuditLogsWithRawResponse:
        """List user actions and configuration changes within this organization."""
        return AuditLogsWithRawResponse(self._organization.audit_logs)

    @cached_property
    def admin_api_keys(self) -> AdminAPIKeysWithRawResponse:
        return AdminAPIKeysWithRawResponse(self._organization.admin_api_keys)

    @cached_property
    def usage(self) -> UsageWithRawResponse:
        return UsageWithRawResponse(self._organization.usage)

    @cached_property
    def invites(self) -> InvitesWithRawResponse:
        return InvitesWithRawResponse(self._organization.invites)

    @cached_property
    def users(self) -> UsersWithRawResponse:
        return UsersWithRawResponse(self._organization.users)

    @cached_property
    def groups(self) -> GroupsWithRawResponse:
        return GroupsWithRawResponse(self._organization.groups)

    @cached_property
    def roles(self) -> RolesWithRawResponse:
        return RolesWithRawResponse(self._organization.roles)

    @cached_property
    def certificates(self) -> CertificatesWithRawResponse:
        return CertificatesWithRawResponse(self._organization.certificates)

    @cached_property
    def projects(self) -> ProjectsWithRawResponse:
        return ProjectsWithRawResponse(self._organization.projects)


class AsyncOrganizationWithRawResponse:
    def __init__(self, organization: AsyncOrganization) -> None:
        self._organization = organization

    @cached_property
    def audit_logs(self) -> AsyncAuditLogsWithRawResponse:
        """List user actions and configuration changes within this organization."""
        return AsyncAuditLogsWithRawResponse(self._organization.audit_logs)

    @cached_property
    def admin_api_keys(self) -> AsyncAdminAPIKeysWithRawResponse:
        return AsyncAdminAPIKeysWithRawResponse(self._organization.admin_api_keys)

    @cached_property
    def usage(self) -> AsyncUsageWithRawResponse:
        return AsyncUsageWithRawResponse(self._organization.usage)

    @cached_property
    def invites(self) -> AsyncInvitesWithRawResponse:
        return AsyncInvitesWithRawResponse(self._organization.invites)

    @cached_property
    def users(self) -> AsyncUsersWithRawResponse:
        return AsyncUsersWithRawResponse(self._organization.users)

    @cached_property
    def groups(self) -> AsyncGroupsWithRawResponse:
        return AsyncGroupsWithRawResponse(self._organization.groups)

    @cached_property
    def roles(self) -> AsyncRolesWithRawResponse:
        return AsyncRolesWithRawResponse(self._organization.roles)

    @cached_property
    def certificates(self) -> AsyncCertificatesWithRawResponse:
        return AsyncCertificatesWithRawResponse(self._organization.certificates)

    @cached_property
    def projects(self) -> AsyncProjectsWithRawResponse:
        return AsyncProjectsWithRawResponse(self._organization.projects)


class OrganizationWithStreamingResponse:
    def __init__(self, organization: Organization) -> None:
        self._organization = organization

    @cached_property
    def audit_logs(self) -> AuditLogsWithStreamingResponse:
        """List user actions and configuration changes within this organization."""
        return AuditLogsWithStreamingResponse(self._organization.audit_logs)

    @cached_property
    def admin_api_keys(self) -> AdminAPIKeysWithStreamingResponse:
        return AdminAPIKeysWithStreamingResponse(self._organization.admin_api_keys)

    @cached_property
    def usage(self) -> UsageWithStreamingResponse:
        return UsageWithStreamingResponse(self._organization.usage)

    @cached_property
    def invites(self) -> InvitesWithStreamingResponse:
        return InvitesWithStreamingResponse(self._organization.invites)

    @cached_property
    def users(self) -> UsersWithStreamingResponse:
        return UsersWithStreamingResponse(self._organization.users)

    @cached_property
    def groups(self) -> GroupsWithStreamingResponse:
        return GroupsWithStreamingResponse(self._organization.groups)

    @cached_property
    def roles(self) -> RolesWithStreamingResponse:
        return RolesWithStreamingResponse(self._organization.roles)

    @cached_property
    def certificates(self) -> CertificatesWithStreamingResponse:
        return CertificatesWithStreamingResponse(self._organization.certificates)

    @cached_property
    def projects(self) -> ProjectsWithStreamingResponse:
        return ProjectsWithStreamingResponse(self._organization.projects)


class AsyncOrganizationWithStreamingResponse:
    def __init__(self, organization: AsyncOrganization) -> None:
        self._organization = organization

    @cached_property
    def audit_logs(self) -> AsyncAuditLogsWithStreamingResponse:
        """List user actions and configuration changes within this organization."""
        return AsyncAuditLogsWithStreamingResponse(self._organization.audit_logs)

    @cached_property
    def admin_api_keys(self) -> AsyncAdminAPIKeysWithStreamingResponse:
        return AsyncAdminAPIKeysWithStreamingResponse(self._organization.admin_api_keys)

    @cached_property
    def usage(self) -> AsyncUsageWithStreamingResponse:
        return AsyncUsageWithStreamingResponse(self._organization.usage)

    @cached_property
    def invites(self) -> AsyncInvitesWithStreamingResponse:
        return AsyncInvitesWithStreamingResponse(self._organization.invites)

    @cached_property
    def users(self) -> AsyncUsersWithStreamingResponse:
        return AsyncUsersWithStreamingResponse(self._organization.users)

    @cached_property
    def groups(self) -> AsyncGroupsWithStreamingResponse:
        return AsyncGroupsWithStreamingResponse(self._organization.groups)

    @cached_property
    def roles(self) -> AsyncRolesWithStreamingResponse:
        return AsyncRolesWithStreamingResponse(self._organization.roles)

    @cached_property
    def certificates(self) -> AsyncCertificatesWithStreamingResponse:
        return AsyncCertificatesWithStreamingResponse(self._organization.certificates)

    @cached_property
    def projects(self) -> AsyncProjectsWithStreamingResponse:
        return AsyncProjectsWithStreamingResponse(self._organization.projects)
