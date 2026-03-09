"""Client-side validation helpers for API request parameters.

These catch common configuration mistakes early, before sending the request
to the API, and surface clear error messages instead of opaque 500 errors.
"""

from __future__ import annotations

import re
from typing import Any, Iterable, Optional

_PROTOCOL_RE = re.compile(r"^https?://", re.IGNORECASE)
_PATH_RE = re.compile(r"/.*$")


def validate_network_policy_allowlist(
    allowed_domains: Iterable[str],
    *,
    source: str = "network_policy.allowed_domains",
) -> None:
    """Validate ``allowed_domains`` entries before sending to the API.

    Raises :class:`ValueError` when common configuration mistakes are
    detected, such as:

    * an empty domain list
    * entries that include a protocol prefix (``http://`` / ``https://``)
    * entries that include a URL path

    These mistakes would otherwise surface as an opaque ``500`` server error
    (see https://github.com/openai/openai-python/issues/2920).
    """
    domains = list(allowed_domains)

    if not domains:
        raise ValueError(
            f"{source} must contain at least one domain. "
            "If you do not need network access, omit the network_policy "
            "or use {\"type\": \"disabled\"} instead."
        )

    for domain in domains:
        if not isinstance(domain, str) or not domain.strip():
            raise ValueError(
                f"{source} contains an invalid entry: {domain!r}. "
                "Each entry must be a non-empty domain string (e.g. \"example.com\")."
            )

        if _PROTOCOL_RE.match(domain):
            bare = _PROTOCOL_RE.sub("", domain).rstrip("/")
            raise ValueError(
                f"{source} entry {domain!r} must be a bare domain without "
                f"a protocol prefix. Use {bare!r} instead."
            )

        if _PATH_RE.search(domain):
            raise ValueError(
                f"{source} entry {domain!r} must be a domain name "
                "without a path (e.g. \"example.com\", not \"example.com/path\")."
            )


def validate_shell_tool(tool: Any) -> None:
    """Run validation checks on a shell tool dict before it is sent to the API.

    Currently validates the ``network_policy.allowed_domains`` field when
    an allowlist policy is specified.
    """
    if not isinstance(tool, dict):
        return

    env: Optional[dict[str, Any]] = tool.get("environment")
    if not isinstance(env, dict):
        return

    policy: Optional[dict[str, Any]] = env.get("network_policy")
    if not isinstance(policy, dict):
        return

    if policy.get("type") != "allowlist":
        return

    domains = policy.get("allowed_domains")
    if domains is not None:
        validate_network_policy_allowlist(
            domains,
            source="shell tool network_policy.allowed_domains",
        )


def validate_tools(tools: Iterable[Any]) -> None:
    """Validate a list of tool dicts before they are sent to the API."""
    for tool in tools:
        if not isinstance(tool, dict):
            continue

        tool_type = tool.get("type")
        if tool_type == "shell":
            validate_shell_tool(tool)
        elif tool_type == "code_interpreter":
            container = tool.get("container")
            if isinstance(container, dict):
                policy = container.get("network_policy")
                if isinstance(policy, dict) and policy.get("type") == "allowlist":
                    domains = policy.get("allowed_domains")
                    if domains is not None:
                        validate_network_policy_allowlist(
                            domains,
                            source="code_interpreter container network_policy.allowed_domains",
                        )
