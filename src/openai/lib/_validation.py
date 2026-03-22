"""Client-side validation helpers for API request parameters.

These catch common configuration mistakes early, before sending the request
to the API, and surface clear error messages instead of opaque 500 errors.
"""

from __future__ import annotations

import re
from typing import Iterable, cast

from openai.types.responses.tool_param import (
    ParseableToolParam,
)
from openai.types.responses.container_auto_param import ContainerAutoParam
from openai.types.responses.function_shell_tool_param import FunctionShellToolParam
from openai.types.responses.container_network_policy_allowlist_param import ContainerNetworkPolicyAllowlistParam

_PROTOCOL_RE = re.compile(r"^https?://", re.IGNORECASE)
_PATH_RE = re.compile(r"/.*$")


def validate_network_policy_allowlist(
    allowed_domains: Iterable[object],
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


def validate_shell_tool(tool: FunctionShellToolParam) -> None:
    """Run validation checks on a shell tool dict before it is sent to the API.

    Currently validates the ``network_policy.allowed_domains`` field when
    an allowlist policy is specified.
    """
    environment = tool.get("environment")
    if environment is None:
        return

    if environment.get("type") != "container_auto":
        return

    container_auto = cast(ContainerAutoParam, environment)
    policy = container_auto.get("network_policy")
    if policy is None or policy.get("type") != "allowlist":
        return

    allowlist = cast(ContainerNetworkPolicyAllowlistParam, policy)
    validate_network_policy_allowlist(
        allowlist["allowed_domains"],
        source="shell tool network_policy.allowed_domains",
    )


def validate_tools(tools: Iterable[object]) -> None:
    """Validate a list of tool dicts before they are sent to the API."""
    for tool in tools:
        if not isinstance(tool, dict):
            continue

        typed_tool = cast(ParseableToolParam, tool)

        if typed_tool["type"] == "shell":
            validate_shell_tool(typed_tool)
        elif typed_tool["type"] == "code_interpreter":
            container = typed_tool["container"]
            if isinstance(container, dict):
                if container.get("type") != "auto":
                    continue

                policy = container.get("network_policy")
                if policy is not None and policy.get("type") == "allowlist":
                    allowlist = cast(ContainerNetworkPolicyAllowlistParam, policy)
                    validate_network_policy_allowlist(
                        allowlist["allowed_domains"],
                        source="code_interpreter container network_policy.allowed_domains",
                    )
