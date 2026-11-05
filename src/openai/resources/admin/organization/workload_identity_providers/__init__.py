# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

import typing as _t

if _t.TYPE_CHECKING:
    from .federation_rules import (
        FederationRules as FederationRules,
        AsyncFederationRules as AsyncFederationRules,
        FederationRulesWithRawResponse as FederationRulesWithRawResponse,
        AsyncFederationRulesWithRawResponse as AsyncFederationRulesWithRawResponse,
        FederationRulesWithStreamingResponse as FederationRulesWithStreamingResponse,
        AsyncFederationRulesWithStreamingResponse as AsyncFederationRulesWithStreamingResponse,
    )
    from .workload_identity_providers import (
        WorkloadIdentityProviders as WorkloadIdentityProviders,
        AsyncWorkloadIdentityProviders as AsyncWorkloadIdentityProviders,
        WorkloadIdentityProvidersWithRawResponse as WorkloadIdentityProvidersWithRawResponse,
        AsyncWorkloadIdentityProvidersWithRawResponse as AsyncWorkloadIdentityProvidersWithRawResponse,
        WorkloadIdentityProvidersWithStreamingResponse as WorkloadIdentityProvidersWithStreamingResponse,
        AsyncWorkloadIdentityProvidersWithStreamingResponse as AsyncWorkloadIdentityProvidersWithStreamingResponse,
    )

else:
    _EXPORTS = {
        "FederationRules": (".federation_rules", "FederationRules"),
        "AsyncFederationRules": (".federation_rules", "AsyncFederationRules"),
        "FederationRulesWithRawResponse": (".federation_rules", "FederationRulesWithRawResponse"),
        "AsyncFederationRulesWithRawResponse": (".federation_rules", "AsyncFederationRulesWithRawResponse"),
        "FederationRulesWithStreamingResponse": (".federation_rules", "FederationRulesWithStreamingResponse"),
        "AsyncFederationRulesWithStreamingResponse": (".federation_rules", "AsyncFederationRulesWithStreamingResponse"),
        "WorkloadIdentityProviders": (".workload_identity_providers", "WorkloadIdentityProviders"),
        "AsyncWorkloadIdentityProviders": (".workload_identity_providers", "AsyncWorkloadIdentityProviders"),
        "WorkloadIdentityProvidersWithRawResponse": (
            ".workload_identity_providers",
            "WorkloadIdentityProvidersWithRawResponse",
        ),
        "AsyncWorkloadIdentityProvidersWithRawResponse": (
            ".workload_identity_providers",
            "AsyncWorkloadIdentityProvidersWithRawResponse",
        ),
        "WorkloadIdentityProvidersWithStreamingResponse": (
            ".workload_identity_providers",
            "WorkloadIdentityProvidersWithStreamingResponse",
        ),
        "AsyncWorkloadIdentityProvidersWithStreamingResponse": (
            ".workload_identity_providers",
            "AsyncWorkloadIdentityProvidersWithStreamingResponse",
        ),
    }
    _SUBMODULES = {
        "federation_rules",
        "workload_identity_providers",
    }

    def __getattr__(name: str) -> _t.Any:
        import importlib

        if name in _EXPORTS:
            module_name, symbol_name = _EXPORTS[name]
            value = getattr(importlib.import_module(module_name, __name__), symbol_name)
        elif name in _SUBMODULES:
            value = importlib.import_module(f".{name}", __name__)
        else:
            raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
        globals()[name] = value
        return value

    def __dir__() -> list[str]:
        return sorted(set(globals()) | set(_EXPORTS) | _SUBMODULES)


__all__ = [
    "FederationRules",
    "AsyncFederationRules",
    "FederationRulesWithRawResponse",
    "AsyncFederationRulesWithRawResponse",
    "FederationRulesWithStreamingResponse",
    "AsyncFederationRulesWithStreamingResponse",
    "WorkloadIdentityProviders",
    "AsyncWorkloadIdentityProviders",
    "WorkloadIdentityProvidersWithRawResponse",
    "AsyncWorkloadIdentityProvidersWithRawResponse",
    "WorkloadIdentityProvidersWithStreamingResponse",
    "AsyncWorkloadIdentityProvidersWithStreamingResponse",
]
