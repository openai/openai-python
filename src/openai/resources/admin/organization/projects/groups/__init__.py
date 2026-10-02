# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

import typing as _t

if _t.TYPE_CHECKING:
    from .roles import (
        Roles as Roles,
        AsyncRoles as AsyncRoles,
        RolesWithRawResponse as RolesWithRawResponse,
        AsyncRolesWithRawResponse as AsyncRolesWithRawResponse,
        RolesWithStreamingResponse as RolesWithStreamingResponse,
        AsyncRolesWithStreamingResponse as AsyncRolesWithStreamingResponse,
    )
    from .groups import (
        Groups as Groups,
        AsyncGroups as AsyncGroups,
        GroupsWithRawResponse as GroupsWithRawResponse,
        AsyncGroupsWithRawResponse as AsyncGroupsWithRawResponse,
        GroupsWithStreamingResponse as GroupsWithStreamingResponse,
        AsyncGroupsWithStreamingResponse as AsyncGroupsWithStreamingResponse,
    )

else:
    _EXPORTS = {
        "Roles": (".roles", "Roles"),
        "AsyncRoles": (".roles", "AsyncRoles"),
        "RolesWithRawResponse": (".roles", "RolesWithRawResponse"),
        "AsyncRolesWithRawResponse": (".roles", "AsyncRolesWithRawResponse"),
        "RolesWithStreamingResponse": (".roles", "RolesWithStreamingResponse"),
        "AsyncRolesWithStreamingResponse": (".roles", "AsyncRolesWithStreamingResponse"),
        "Groups": (".groups", "Groups"),
        "AsyncGroups": (".groups", "AsyncGroups"),
        "GroupsWithRawResponse": (".groups", "GroupsWithRawResponse"),
        "AsyncGroupsWithRawResponse": (".groups", "AsyncGroupsWithRawResponse"),
        "GroupsWithStreamingResponse": (".groups", "GroupsWithStreamingResponse"),
        "AsyncGroupsWithStreamingResponse": (".groups", "AsyncGroupsWithStreamingResponse"),
    }
    _SUBMODULES = {
        "groups",
        "roles",
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
    "Roles",
    "AsyncRoles",
    "RolesWithRawResponse",
    "AsyncRolesWithRawResponse",
    "RolesWithStreamingResponse",
    "AsyncRolesWithStreamingResponse",
    "Groups",
    "AsyncGroups",
    "GroupsWithRawResponse",
    "AsyncGroupsWithRawResponse",
    "GroupsWithStreamingResponse",
    "AsyncGroupsWithStreamingResponse",
]
