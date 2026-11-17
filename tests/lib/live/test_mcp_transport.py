from __future__ import annotations

import json

import httpx2
import pytest
from websockets.sync.server import ServerConnection

from openai import OpenAI
from openai.types.live import SessionStartedEvent, SessionUpdatedEvent
from openai.types.live.session_resource import DelegationResponses
from openai.types.live.responses_delegation_config import (
    ToolMcp,
    ToolMcpAllowedToolsLiveMCPToolFilterParam,
    ToolMcpRequireApprovalLiveMCPRequireApprovalFilterParam,
)

from ..responses.test_websocket_session import script_server


def test_mcp_fields_survive_session_event_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NO_PROXY", "127.0.0.1")
    monkeypatch.setenv("no_proxy", "127.0.0.1")
    tools = json.loads(
        '[{"type":"mcp","server_label":"fixture","server_url":"https://example.test/mcp","server_description":"MCP response fixture","connector_id":"connector_dropbox","tunnel_id":"tunnel_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","allowed_callers":["direct"],"defer_loading":false,"allowed_tools":{"tool_names":["lookup"],"read_only":true},"require_approval":{"always":{"tool_names":["write"],"read_only":false},"never":{"tool_names":["lookup"],"read_only":true}}},{"type":"mcp","server_url":null,"server_description":null,"connector_id":null,"tunnel_id":null,"allowed_callers":null,"defer_loading":null,"allowed_tools":null,"require_approval":null},{"type":"mcp"},{"type":"mcp","allowed_tools":{"tool_names":null,"read_only":null},"require_approval":{"always":null,"never":null}},{"type":"mcp","allowed_tools":{},"require_approval":{}}]'
    )
    exercised = []

    def script(socket: ServerConnection) -> None:
        for kind in ("session.started", "session.updated"):
            exercised.append(json.loads(socket.recv(timeout=5))["type"])
            socket.send(
                json.dumps(
                    {
                        "type": kind,
                        "event_id": "event_fixture",
                        "session": {
                            "id": "live_fixture",
                            "model": "gpt-live-1",
                            "status": "active",
                            "expires_at": 123,
                            "delegation": {
                                "type": "responses",
                                "responses": {"model": "model_fixture", "tools": tools},
                            },
                        },
                    }
                )
            )

    with script_server(script) as url:
        with OpenAI(api_key="fake-live-key", base_url=url, http_client=httpx2.Client(trust_env=False)) as client:
            with client.live.connect() as connection:
                for kind in ("session.started", "session.updated"):
                    if kind == "session.started":
                        connection.session.start(session={"model": "gpt-live-1"})
                    else:
                        connection.session.update(session={})
                    event = connection.recv()
                    assert isinstance(event, (SessionStartedEvent, SessionUpdatedEvent))
                    assert event.type == kind
                    assert isinstance(event.session.delegation, DelegationResponses)
                    observed = event.session.delegation.responses.tools
                    assert observed is not None
                    tool = observed[0]
                    assert isinstance(tool, ToolMcp)
                    assert tool.server_label == "fixture"
                    assert tool.server_description == "MCP response fixture"
                    assert tool.server_url == "https://example.test/mcp"
                    assert tool.connector_id == "connector_dropbox"
                    assert tool.tunnel_id == "tunnel_" + "a" * 32
                    assert tool.allowed_callers == ["direct"]
                    assert tool.defer_loading is False
                    assert isinstance(tool.allowed_tools, ToolMcpAllowedToolsLiveMCPToolFilterParam)
                    assert tool.allowed_tools.tool_names == ["lookup"]
                    assert tool.allowed_tools.read_only is True
                    assert isinstance(tool.require_approval, ToolMcpRequireApprovalLiveMCPRequireApprovalFilterParam)
                    assert tool.require_approval.always is not None
                    assert tool.require_approval.always.tool_names == ["write"]
                    assert tool.require_approval.always.read_only is False
                    assert tool.require_approval.never is not None
                    assert tool.require_approval.never.tool_names == ["lookup"]
                    assert tool.require_approval.never.read_only is True
                    for absent in observed[1:3]:
                        assert isinstance(absent, ToolMcp)
                        assert absent.server_description is None
                        assert absent.server_url is None
                        assert absent.connector_id is None
                        assert absent.tunnel_id is None
                        assert absent.allowed_callers is None
                        assert absent.defer_loading is None
                        assert absent.allowed_tools is None
                        assert absent.require_approval is None
                    for nested in observed[3:]:
                        assert isinstance(nested, ToolMcp)
                        assert isinstance(nested.allowed_tools, ToolMcpAllowedToolsLiveMCPToolFilterParam)
                        assert nested.allowed_tools.tool_names is None
                        assert nested.allowed_tools.read_only is None
                        assert isinstance(
                            nested.require_approval, ToolMcpRequireApprovalLiveMCPRequireApprovalFilterParam
                        )
                        assert nested.require_approval.always is None
                        assert nested.require_approval.never is None
    assert exercised == ["session.start", "session.update"]
