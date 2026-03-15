"""Tests for shell tool network_policy allowlist validation and serialization.

Covers https://github.com/openai/openai-python/issues/2920
"""

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

import openai
from openai._utils import maybe_transform
from openai.lib._validation import (
    validate_tools,
    validate_shell_tool,
    validate_network_policy_allowlist,
)
from openai.types.responses.response_create_params import ResponseCreateParamsNonStreaming

# ---------------------------------------------------------------------------
# Validation unit tests
# ---------------------------------------------------------------------------


class TestValidateNetworkPolicyAllowlist:
    def test_valid_single_domain(self) -> None:
        validate_network_policy_allowlist(["example.com"])

    def test_valid_multiple_domains(self) -> None:
        validate_network_policy_allowlist(["pypi.org", "files.pythonhosted.org", "github.com"])

    def test_valid_subdomain(self) -> None:
        validate_network_policy_allowlist(["api.example.com"])

    def test_empty_list_raises(self) -> None:
        with pytest.raises(ValueError, match="must contain at least one domain"):
            validate_network_policy_allowlist([])

    def test_http_prefix_raises(self) -> None:
        with pytest.raises(ValueError, match="bare domain without a protocol prefix"):
            validate_network_policy_allowlist(["http://example.com"])

    def test_https_prefix_raises(self) -> None:
        with pytest.raises(ValueError, match="bare domain without a protocol prefix"):
            validate_network_policy_allowlist(["https://example.com"])

    def test_protocol_suggestion_strips_prefix(self) -> None:
        with pytest.raises(ValueError, match=r"Use 'example\.com' instead"):
            validate_network_policy_allowlist(["https://example.com"])

    def test_domain_with_path_raises(self) -> None:
        with pytest.raises(ValueError, match="without a path"):
            validate_network_policy_allowlist(["example.com/api/v1"])

    def test_domain_with_trailing_slash_raises(self) -> None:
        with pytest.raises(ValueError, match="without a path"):
            validate_network_policy_allowlist(["example.com/"])

    def test_empty_string_raises(self) -> None:
        with pytest.raises(ValueError, match="invalid entry"):
            validate_network_policy_allowlist([""])

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(ValueError, match="invalid entry"):
            validate_network_policy_allowlist(["   "])


class TestValidateShellTool:
    def test_valid_shell_tool_with_allowlist(self) -> None:
        validate_shell_tool({
            "type": "shell",
            "environment": {
                "type": "container_auto",
                "network_policy": {
                    "type": "allowlist",
                    "allowed_domains": ["google.com"],
                },
            },
        })

    def test_shell_tool_with_disabled_policy(self) -> None:
        validate_shell_tool({
            "type": "shell",
            "environment": {
                "type": "container_auto",
                "network_policy": {"type": "disabled"},
            },
        })

    def test_shell_tool_without_environment(self) -> None:
        validate_shell_tool({"type": "shell"})

    def test_shell_tool_without_network_policy(self) -> None:
        validate_shell_tool({
            "type": "shell",
            "environment": {"type": "container_auto"},
        })

    def test_shell_tool_with_bad_domain_raises(self) -> None:
        with pytest.raises(ValueError, match="protocol prefix"):
            validate_shell_tool({
                "type": "shell",
                "environment": {
                    "type": "container_auto",
                    "network_policy": {
                        "type": "allowlist",
                        "allowed_domains": ["https://example.com"],
                    },
                },
            })


class TestValidateTools:
    def test_valid_tools_pass(self) -> None:
        validate_tools([
            {
                "type": "shell",
                "environment": {
                    "type": "container_auto",
                    "network_policy": {
                        "type": "allowlist",
                        "allowed_domains": ["example.com"],
                    },
                },
            },
            {"type": "web_search"},
        ])

    def test_non_dict_tools_are_skipped(self) -> None:
        validate_tools(["not_a_dict"])  # type: ignore[list-item]

    def test_code_interpreter_allowlist_validated(self) -> None:
        with pytest.raises(ValueError, match="protocol prefix"):
            validate_tools([
                {
                    "type": "code_interpreter",
                    "container": {
                        "network_policy": {
                            "type": "allowlist",
                            "allowed_domains": ["https://pypi.org"],
                        },
                    },
                }
            ])


# ---------------------------------------------------------------------------
# Serialization tests — prove the library sends the correct JSON
# ---------------------------------------------------------------------------


class _CaptureTransport(httpx.BaseTransport):
    """Transport that records the last request and returns a minimal valid response."""

    last_request: httpx.Request | None = None

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        self.last_request = request
        return httpx.Response(200, json={
            "id": "resp_test",
            "object": "response",
            "created_at": 1234567890,
            "status": "completed",
            "model": "gpt-5.2",
            "output": [],
            "output_text": "",
            "parallel_tool_calls": True,
            "tool_choice": "auto",
            "tools": [],
        })


def _captured_body(transport: _CaptureTransport) -> dict[str, Any]:
    assert transport.last_request is not None
    return json.loads(transport.last_request.content)


class TestShellToolSerialization:
    """Ensure shell tool with allowlist is serialized exactly as the API expects."""

    def _make_client(self) -> tuple[openai.OpenAI, _CaptureTransport]:
        transport = _CaptureTransport()
        client = openai.OpenAI(
            api_key="test-key",
            http_client=httpx.Client(transport=transport),
        )
        return client, transport

    def test_allowlist_network_policy_serialization(self) -> None:
        client, transport = self._make_client()
        client.responses.create(
            model="gpt-5.2",
            input="test",
            tools=[{
                "type": "shell",
                "environment": {
                    "type": "container_auto",
                    "network_policy": {
                        "type": "allowlist",
                        "allowed_domains": ["google.com"],
                    },
                },
            }],
        )
        body = _captured_body(transport)
        tool = body["tools"][0]
        assert tool["type"] == "shell"
        assert tool["environment"]["type"] == "container_auto"
        policy = tool["environment"]["network_policy"]
        assert policy["type"] == "allowlist"
        assert policy["allowed_domains"] == ["google.com"]

    def test_allowlist_with_multiple_domains(self) -> None:
        client, transport = self._make_client()
        domains = ["pypi.org", "files.pythonhosted.org", "github.com"]
        client.responses.create(
            model="gpt-5.2",
            input="test",
            tools=[{
                "type": "shell",
                "environment": {
                    "type": "container_auto",
                    "network_policy": {
                        "type": "allowlist",
                        "allowed_domains": domains,
                    },
                },
            }],
        )
        body = _captured_body(transport)
        assert body["tools"][0]["environment"]["network_policy"]["allowed_domains"] == domains

    def test_allowlist_with_domain_secrets(self) -> None:
        client, transport = self._make_client()
        client.responses.create(
            model="gpt-5.2",
            input="test",
            tools=[{
                "type": "shell",
                "environment": {
                    "type": "container_auto",
                    "network_policy": {
                        "type": "allowlist",
                        "allowed_domains": ["httpbin.org"],
                        "domain_secrets": [
                            {"domain": "httpbin.org", "name": "API_KEY", "value": "secret-123"},
                        ],
                    },
                },
            }],
        )
        body = _captured_body(transport)
        policy = body["tools"][0]["environment"]["network_policy"]
        assert policy["type"] == "allowlist"
        assert policy["allowed_domains"] == ["httpbin.org"]
        assert policy["domain_secrets"] == [
            {"domain": "httpbin.org", "name": "API_KEY", "value": "secret-123"},
        ]

    def test_disabled_network_policy_serialization(self) -> None:
        client, transport = self._make_client()
        client.responses.create(
            model="gpt-5.2",
            input="test",
            tools=[{
                "type": "shell",
                "environment": {
                    "type": "container_auto",
                    "network_policy": {"type": "disabled"},
                },
            }],
        )
        body = _captured_body(transport)
        assert body["tools"][0]["environment"]["network_policy"] == {"type": "disabled"}

    def test_shell_without_environment_serialization(self) -> None:
        client, transport = self._make_client()
        client.responses.create(
            model="gpt-5.2",
            input="test",
            tools=[{"type": "shell"}],
        )
        body = _captured_body(transport)
        assert body["tools"][0] == {"type": "shell"}


class TestTransformAllowlist:
    """Verify that maybe_transform preserves allowlist fields exactly."""

    def test_transform_preserves_all_fields(self) -> None:
        params = {
            "model": "gpt-5.2",
            "input": "test",
            "tools": [
                {
                    "type": "shell",
                    "environment": {
                        "type": "container_auto",
                        "network_policy": {
                            "type": "allowlist",
                            "allowed_domains": ["example.com", "api.example.com"],
                        },
                    },
                }
            ],
        }
        result = maybe_transform(params, ResponseCreateParamsNonStreaming)
        tool = result["tools"][0]
        assert tool["environment"]["network_policy"] == {
            "type": "allowlist",
            "allowed_domains": ["example.com", "api.example.com"],
        }
