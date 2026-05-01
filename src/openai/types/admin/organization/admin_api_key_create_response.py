# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .admin_api_key import AdminAPIKey

__all__ = ["AdminAPIKeyCreateResponse"]


class AdminAPIKeyCreateResponse(AdminAPIKey):
    """Represents an individual Admin API key in an org."""

    value: str
    """The value of the API key. Only shown on create."""
