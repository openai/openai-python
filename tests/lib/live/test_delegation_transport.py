from __future__ import annotations

import json

import httpx2
import pytest
from websockets.sync.server import ServerConnection

from openai import OpenAI
from openai.types.live import SessionStartedEvent, SessionUpdatedEvent
from openai.types.live.session_resource import DelegationResponses
from openai.types.live.responses_delegation_config import (
    ToolShell,
    ToolShellEnvironmentLocal,
    ToolShellEnvironmentContainerAuto,
    ToolChoiceLiveAllowedToolsChoiceParam,
    ToolShellEnvironmentContainerAutoSkillSkillReference,
    ToolShellEnvironmentContainerAutoNetworkPolicyAllowlist,
)

from ..responses.test_websocket_session import script_server


def test_live_delegation_response_fields_survive_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NO_PROXY", "127.0.0.1")
    monkeypatch.setenv("no_proxy", "127.0.0.1")

    def send_session(socket: ServerConnection, event_type: str, fields: dict[str, object]) -> None:
        socket.send(
            json.dumps(
                {
                    "type": event_type,
                    "event_id": "event_fixture",
                    "session": {
                        "id": "live_fixture",
                        "model": "gpt-live-1",
                        "status": "active",
                        "expires_at": 123,
                        "delegation": {"type": "responses", "responses": {"model": "model_fixture", **fields}},
                    },
                }
            )
        )

    def script(socket: ServerConnection) -> None:
        assert json.loads(socket.recv(timeout=5))["type"] == "session.start"
        send_session(
            socket,
            "session.started",
            {
                "tool_choice": {"type": "allowed_tools", "mode": "required", "tools": [{"type": "file_search"}]},
                "tools": [
                    {
                        "type": "shell",
                        "environment": {
                            "type": "container_auto",
                            "file_ids": ["file_fixture"],
                            "memory_limit": "4g",
                            "network_policy": {"type": "allowlist", "allowed_domains": ["example.test"]},
                            "skills": [{"type": "skill_reference", "skill_id": "skill_fixture", "version": "2"}],
                        },
                    },
                    {
                        "type": "shell",
                        "environment": {
                            "type": "local",
                            "skills": [{"name": "fixture", "description": "test skill", "path": "/fixture"}],
                        },
                    },
                ],
            },
        )
        for fields in ({"tools": None, "tool_choice": None}, {}):
            assert json.loads(socket.recv(timeout=5))["type"] == "session.update"
            send_session(socket, "session.updated", fields)

    with script_server(script) as url:
        with OpenAI(api_key="fake-live-key", base_url=url, http_client=httpx2.Client(trust_env=False)) as client:
            with client.live.connect() as connection:
                connection.session.start(session={"model": "gpt-live-1"})
                started = connection.recv()
                updates = []
                for _ in range(2):
                    connection.session.update(session={})
                    updates.append(connection.recv())

    assert isinstance(started, SessionStartedEvent)
    assert isinstance(started.session.delegation, DelegationResponses)
    responses = started.session.delegation.responses
    assert isinstance(responses.tool_choice, ToolChoiceLiveAllowedToolsChoiceParam)
    assert responses.tool_choice.mode == "required"
    assert responses.tool_choice.tools[0].type == "file_search"
    assert responses.tools is not None
    hosted, local = responses.tools
    assert isinstance(hosted, ToolShell)
    assert isinstance(hosted.environment, ToolShellEnvironmentContainerAuto)
    assert hosted.environment.file_ids == ["file_fixture"]
    assert hosted.environment.memory_limit == "4g"
    assert isinstance(hosted.environment.network_policy, ToolShellEnvironmentContainerAutoNetworkPolicyAllowlist)
    assert hosted.environment.network_policy.allowed_domains == ["example.test"]
    assert hosted.environment.skills is not None
    assert isinstance(hosted.environment.skills[0], ToolShellEnvironmentContainerAutoSkillSkillReference)
    assert hosted.environment.skills[0].version == "2"
    assert isinstance(local, ToolShell)
    assert isinstance(local.environment, ToolShellEnvironmentLocal)
    assert local.environment.skills is not None
    assert local.environment.skills[0].path == "/fixture"

    for updated in updates:
        assert isinstance(updated, SessionUpdatedEvent)
        assert isinstance(updated.session.delegation, DelegationResponses)
        assert updated.session.delegation.responses.tool_choice is None
        assert updated.session.delegation.responses.tools is None
