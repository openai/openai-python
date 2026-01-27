# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

import requestx

RAW_RESPONSE_HEADER = "X-Stainless-Raw-Response"
OVERRIDE_CAST_TO_HEADER = "____stainless_override_cast_to"

# default timeout is 10 minutes
DEFAULT_TIMEOUT = requestx.Timeout(timeout=600, connect=5.0)
DEFAULT_MAX_RETRIES = 2


class Limits:
    """Connection limits configuration for requestx clients."""

    def __init__(
        self,
        *,
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
    ) -> None:
        self.max_connections = max_connections
        self.max_keepalive_connections = max_keepalive_connections


DEFAULT_CONNECTION_LIMITS = Limits(max_connections=1000, max_keepalive_connections=100)

INITIAL_RETRY_DELAY = 0.5
MAX_RETRY_DELAY = 8.0
