# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

import httpx2

RAW_RESPONSE_HEADER = "X-Stainless-Raw-Response"
OVERRIDE_CAST_TO_HEADER = "____stainless_override_cast_to"

# default timeout is 10 minutes
DEFAULT_TIMEOUT = httpx2.Timeout(timeout=600, connect=5.0)
DEFAULT_MAX_RETRIES = 2
DEFAULT_CONNECTION_LIMITS = httpx2.Limits(max_connections=1000, max_keepalive_connections=100)

INITIAL_RETRY_DELAY = 0.5
MAX_RETRY_DELAY = 8.0
MAX_RETRY_AFTER_DELAY = 2 * 60
