from __future__ import annotations

from ._workload import (
    WorkloadIdentity as WorkloadIdentity,
    SubjectTokenProvider as SubjectTokenProvider,
    WorkloadIdentityAuth as WorkloadIdentityAuth,
    X509WorkloadIdentity as X509WorkloadIdentity,
    SubjectTokenWorkloadIdentity as SubjectTokenWorkloadIdentity,
    gcp_id_token_provider as gcp_id_token_provider,
    x509_workload_identity as x509_workload_identity,
    k8s_service_account_token_provider as k8s_service_account_token_provider,
    azure_managed_identity_token_provider as azure_managed_identity_token_provider,
)

__all__ = [
    "SubjectTokenProvider",
    "WorkloadIdentity",
    "SubjectTokenWorkloadIdentity",
    "X509WorkloadIdentity",
    "WorkloadIdentityAuth",
    "x509_workload_identity",
    "k8s_service_account_token_provider",
    "azure_managed_identity_token_provider",
    "gcp_id_token_provider",
]
