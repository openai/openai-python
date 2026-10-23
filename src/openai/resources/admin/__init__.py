# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

import typing as _t

if _t.TYPE_CHECKING:
    from .admin import (
        Admin as Admin,
        AsyncAdmin as AsyncAdmin,
        AdminWithRawResponse as AdminWithRawResponse,
        AsyncAdminWithRawResponse as AsyncAdminWithRawResponse,
        AdminWithStreamingResponse as AdminWithStreamingResponse,
        AsyncAdminWithStreamingResponse as AsyncAdminWithStreamingResponse,
    )
    from .organization import (
        Organization as Organization,
        AsyncOrganization as AsyncOrganization,
        OrganizationWithRawResponse as OrganizationWithRawResponse,
        AsyncOrganizationWithRawResponse as AsyncOrganizationWithRawResponse,
        OrganizationWithStreamingResponse as OrganizationWithStreamingResponse,
        AsyncOrganizationWithStreamingResponse as AsyncOrganizationWithStreamingResponse,
    )

else:
    _EXPORTS = {
        "Organization": (".organization", "Organization"),
        "AsyncOrganization": (".organization", "AsyncOrganization"),
        "OrganizationWithRawResponse": (".organization", "OrganizationWithRawResponse"),
        "AsyncOrganizationWithRawResponse": (".organization", "AsyncOrganizationWithRawResponse"),
        "OrganizationWithStreamingResponse": (".organization", "OrganizationWithStreamingResponse"),
        "AsyncOrganizationWithStreamingResponse": (".organization", "AsyncOrganizationWithStreamingResponse"),
        "Admin": (".admin", "Admin"),
        "AsyncAdmin": (".admin", "AsyncAdmin"),
        "AdminWithRawResponse": (".admin", "AdminWithRawResponse"),
        "AsyncAdminWithRawResponse": (".admin", "AsyncAdminWithRawResponse"),
        "AdminWithStreamingResponse": (".admin", "AdminWithStreamingResponse"),
        "AsyncAdminWithStreamingResponse": (".admin", "AsyncAdminWithStreamingResponse"),
    }
    _SUBMODULES = {
        "admin",
        "organization",
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
    "Organization",
    "AsyncOrganization",
    "OrganizationWithRawResponse",
    "AsyncOrganizationWithRawResponse",
    "OrganizationWithStreamingResponse",
    "AsyncOrganizationWithStreamingResponse",
    "Admin",
    "AsyncAdmin",
    "AdminWithRawResponse",
    "AsyncAdminWithRawResponse",
    "AdminWithStreamingResponse",
    "AsyncAdminWithStreamingResponse",
]
