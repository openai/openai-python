from __future__ import annotations

from ._workload import (
    WorkloadIdentity as WorkloadIdentity,
    SubjectTokenProvider as SubjectTokenProvider,
    WorkloadIdentityAuth as WorkloadIdentityAuth,
    gcp_id_token_provider as gcp_id_token_provider,
    k8s_service_account_token_provider as k8s_service_account_token_provider,
    azure_managed_identity_token_provider as azure_managed_identity_token_provider,
)

__all__ = [
    "SubjectTokenProvider",
    "WorkloadIdentity",
    "WorkloadIdentityAuth",
    "k8s_service_account_token_provider",
    "azure_managed_identity_token_provider",
    "gcp_id_token_provider",
]
