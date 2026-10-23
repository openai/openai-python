# File generated from our OpenAPI spec by Castiron. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncCursorPage, AsyncCursorPage
from openai.types.beta.agents import (
    Automation,
    AutomationDeleted,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAutomations:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create_overload_1(self, client: OpenAI) -> None:
        automation = client.beta.agents.automations.create(
            expression="x",
            name="x",
            target={
                "environment": {"type": "none"},
                "input": [
                    {
                        "content": [
                            {
                                "text": "text",
                                "type": "input_text",
                            }
                        ],
                        "role": "user",
                    }
                ],
                "type": "new_session",
            },
            timezone="x",
            type="periodic",
        )
        assert_matches_type(Automation, automation, path=["response"])

    @parametrize
    def test_method_create_with_all_params_overload_1(self, client: OpenAI) -> None:
        automation = client.beta.agents.automations.create(
            expression="x",
            name="x",
            target={
                "environment": {"type": "none"},
                "input": [
                    {
                        "content": [
                            {
                                "text": "text",
                                "type": "input_text",
                            }
                        ],
                        "role": "user",
                    }
                ],
                "type": "new_session",
            },
            timezone="x",
            type="periodic",
            metadata={},
        )
        assert_matches_type(Automation, automation, path=["response"])

    @parametrize
    def test_raw_response_create_overload_1(self, client: OpenAI) -> None:
        response = client.beta.agents.automations.with_raw_response.create(
            expression="x",
            name="x",
            target={
                "environment": {"type": "none"},
                "input": [
                    {
                        "content": [
                            {
                                "text": "text",
                                "type": "input_text",
                            }
                        ],
                        "role": "user",
                    }
                ],
                "type": "new_session",
            },
            timezone="x",
            type="periodic",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        automation = response.parse()
        assert_matches_type(Automation, automation, path=["response"])

    @parametrize
    def test_streaming_response_create_overload_1(self, client: OpenAI) -> None:
        with client.beta.agents.automations.with_streaming_response.create(
            expression="x",
            name="x",
            target={
                "environment": {"type": "none"},
                "input": [
                    {
                        "content": [
                            {
                                "text": "text",
                                "type": "input_text",
                            }
                        ],
                        "role": "user",
                    }
                ],
                "type": "new_session",
            },
            timezone="x",
            type="periodic",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            automation = response.parse()
            assert_matches_type(Automation, automation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_create_overload_2(self, client: OpenAI) -> None:
        automation = client.beta.agents.automations.create(
            name="x",
            run_at=1,
            target={
                "environment": {"type": "none"},
                "input": [
                    {
                        "content": [
                            {
                                "text": "text",
                                "type": "input_text",
                            }
                        ],
                        "role": "user",
                    }
                ],
                "type": "new_session",
            },
            type="once",
        )
        assert_matches_type(Automation, automation, path=["response"])

    @parametrize
    def test_method_create_with_all_params_overload_2(self, client: OpenAI) -> None:
        automation = client.beta.agents.automations.create(
            name="x",
            run_at=1,
            target={
                "environment": {"type": "none"},
                "input": [
                    {
                        "content": [
                            {
                                "text": "text",
                                "type": "input_text",
                            }
                        ],
                        "role": "user",
                    }
                ],
                "type": "new_session",
            },
            type="once",
            metadata={},
        )
        assert_matches_type(Automation, automation, path=["response"])

    @parametrize
    def test_raw_response_create_overload_2(self, client: OpenAI) -> None:
        response = client.beta.agents.automations.with_raw_response.create(
            name="x",
            run_at=1,
            target={
                "environment": {"type": "none"},
                "input": [
                    {
                        "content": [
                            {
                                "text": "text",
                                "type": "input_text",
                            }
                        ],
                        "role": "user",
                    }
                ],
                "type": "new_session",
            },
            type="once",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        automation = response.parse()
        assert_matches_type(Automation, automation, path=["response"])

    @parametrize
    def test_streaming_response_create_overload_2(self, client: OpenAI) -> None:
        with client.beta.agents.automations.with_streaming_response.create(
            name="x",
            run_at=1,
            target={
                "environment": {"type": "none"},
                "input": [
                    {
                        "content": [
                            {
                                "text": "text",
                                "type": "input_text",
                            }
                        ],
                        "role": "user",
                    }
                ],
                "type": "new_session",
            },
            type="once",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            automation = response.parse()
            assert_matches_type(Automation, automation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        automation = client.beta.agents.automations.retrieve(
            "automation_id",
        )
        assert_matches_type(Automation, automation, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.beta.agents.automations.with_raw_response.retrieve(
            "automation_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        automation = response.parse()
        assert_matches_type(Automation, automation, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.beta.agents.automations.with_streaming_response.retrieve(
            "automation_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            automation = response.parse()
            assert_matches_type(Automation, automation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `automation_id` but received ''"):
            client.beta.agents.automations.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_update(self, client: OpenAI) -> None:
        automation = client.beta.agents.automations.update(
            automation_id="automation_id",
        )
        assert_matches_type(Automation, automation, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: OpenAI) -> None:
        automation = client.beta.agents.automations.update(
            automation_id="automation_id",
            expression="x",
            metadata={"foo": "string"},
            name="x",
            run_at=0,
            target={
                "environment": {"type": "none"},
                "input": [
                    {
                        "content": [
                            {
                                "text": "text",
                                "type": "input_text",
                            }
                        ],
                        "role": "user",
                        "type": "message",
                    }
                ],
                "type": "new_session",
                "agent": {
                    "instructions": "instructions",
                    "model": "model",
                    "multi_agent": {
                        "enabled": True,
                        "max_concurrent_subagents": 1,
                    },
                    "reasoning": {
                        "effort": "none",
                        "summary": "concise",
                    },
                    "service_tier": "auto",
                    "text": {
                        "format": {"type": "text"},
                        "verbosity": "low",
                    },
                    "tools": [
                        {
                            "description": "description",
                            "name": "name",
                            "parameters": {"foo": "bar"},
                            "type": "function",
                            "defer_loading": True,
                        }
                    ],
                },
                "agent_id": "agent_id",
                "metadata": {"foo": "string"},
                "vault_ids": ["string"],
            },
            timezone="x",
        )
        assert_matches_type(Automation, automation, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: OpenAI) -> None:
        response = client.beta.agents.automations.with_raw_response.update(
            automation_id="automation_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        automation = response.parse()
        assert_matches_type(Automation, automation, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: OpenAI) -> None:
        with client.beta.agents.automations.with_streaming_response.update(
            automation_id="automation_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            automation = response.parse()
            assert_matches_type(Automation, automation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `automation_id` but received ''"):
            client.beta.agents.automations.with_raw_response.update(
                automation_id="",
            )

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        automation = client.beta.agents.automations.list()
        assert_matches_type(SyncCursorPage[Automation], automation, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        automation = client.beta.agents.automations.list(
            after="after",
            limit=1,
            order="asc",
            session_id="session_id",
        )
        assert_matches_type(SyncCursorPage[Automation], automation, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.beta.agents.automations.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        automation = response.parse()
        assert_matches_type(SyncCursorPage[Automation], automation, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.beta.agents.automations.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            automation = response.parse()
            assert_matches_type(SyncCursorPage[Automation], automation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: OpenAI) -> None:
        automation = client.beta.agents.automations.delete(
            "automation_id",
        )
        assert_matches_type(AutomationDeleted, automation, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: OpenAI) -> None:
        response = client.beta.agents.automations.with_raw_response.delete(
            "automation_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        automation = response.parse()
        assert_matches_type(AutomationDeleted, automation, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: OpenAI) -> None:
        with client.beta.agents.automations.with_streaming_response.delete(
            "automation_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            automation = response.parse()
            assert_matches_type(AutomationDeleted, automation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `automation_id` but received ''"):
            client.beta.agents.automations.with_raw_response.delete(
                "",
            )

    @parametrize
    def test_method_pause(self, client: OpenAI) -> None:
        automation = client.beta.agents.automations.pause(
            "automation_id",
        )
        assert_matches_type(Automation, automation, path=["response"])

    @parametrize
    def test_raw_response_pause(self, client: OpenAI) -> None:
        response = client.beta.agents.automations.with_raw_response.pause(
            "automation_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        automation = response.parse()
        assert_matches_type(Automation, automation, path=["response"])

    @parametrize
    def test_streaming_response_pause(self, client: OpenAI) -> None:
        with client.beta.agents.automations.with_streaming_response.pause(
            "automation_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            automation = response.parse()
            assert_matches_type(Automation, automation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_pause(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `automation_id` but received ''"):
            client.beta.agents.automations.with_raw_response.pause(
                "",
            )

    @parametrize
    def test_method_resume(self, client: OpenAI) -> None:
        automation = client.beta.agents.automations.resume(
            "automation_id",
        )
        assert_matches_type(Automation, automation, path=["response"])

    @parametrize
    def test_raw_response_resume(self, client: OpenAI) -> None:
        response = client.beta.agents.automations.with_raw_response.resume(
            "automation_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        automation = response.parse()
        assert_matches_type(Automation, automation, path=["response"])

    @parametrize
    def test_streaming_response_resume(self, client: OpenAI) -> None:
        with client.beta.agents.automations.with_streaming_response.resume(
            "automation_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            automation = response.parse()
            assert_matches_type(Automation, automation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_resume(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `automation_id` but received ''"):
            client.beta.agents.automations.with_raw_response.resume(
                "",
            )


class TestAsyncAutomations:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create_overload_1(self, async_client: AsyncOpenAI) -> None:
        automation = await async_client.beta.agents.automations.create(
            expression="x",
            name="x",
            target={
                "environment": {"type": "none"},
                "input": [
                    {
                        "content": [
                            {
                                "text": "text",
                                "type": "input_text",
                            }
                        ],
                        "role": "user",
                    }
                ],
                "type": "new_session",
            },
            timezone="x",
            type="periodic",
        )
        assert_matches_type(Automation, automation, path=["response"])

    @parametrize
    async def test_method_create_with_all_params_overload_1(self, async_client: AsyncOpenAI) -> None:
        automation = await async_client.beta.agents.automations.create(
            expression="x",
            name="x",
            target={
                "environment": {"type": "none"},
                "input": [
                    {
                        "content": [
                            {
                                "text": "text",
                                "type": "input_text",
                            }
                        ],
                        "role": "user",
                    }
                ],
                "type": "new_session",
            },
            timezone="x",
            type="periodic",
            metadata={},
        )
        assert_matches_type(Automation, automation, path=["response"])

    @parametrize
    async def test_raw_response_create_overload_1(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.automations.with_raw_response.create(
            expression="x",
            name="x",
            target={
                "environment": {"type": "none"},
                "input": [
                    {
                        "content": [
                            {
                                "text": "text",
                                "type": "input_text",
                            }
                        ],
                        "role": "user",
                    }
                ],
                "type": "new_session",
            },
            timezone="x",
            type="periodic",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        automation = response.parse()
        assert_matches_type(Automation, automation, path=["response"])

    @parametrize
    async def test_streaming_response_create_overload_1(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.automations.with_streaming_response.create(
            expression="x",
            name="x",
            target={
                "environment": {"type": "none"},
                "input": [
                    {
                        "content": [
                            {
                                "text": "text",
                                "type": "input_text",
                            }
                        ],
                        "role": "user",
                    }
                ],
                "type": "new_session",
            },
            timezone="x",
            type="periodic",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            automation = await response.parse()
            assert_matches_type(Automation, automation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_create_overload_2(self, async_client: AsyncOpenAI) -> None:
        automation = await async_client.beta.agents.automations.create(
            name="x",
            run_at=1,
            target={
                "environment": {"type": "none"},
                "input": [
                    {
                        "content": [
                            {
                                "text": "text",
                                "type": "input_text",
                            }
                        ],
                        "role": "user",
                    }
                ],
                "type": "new_session",
            },
            type="once",
        )
        assert_matches_type(Automation, automation, path=["response"])

    @parametrize
    async def test_method_create_with_all_params_overload_2(self, async_client: AsyncOpenAI) -> None:
        automation = await async_client.beta.agents.automations.create(
            name="x",
            run_at=1,
            target={
                "environment": {"type": "none"},
                "input": [
                    {
                        "content": [
                            {
                                "text": "text",
                                "type": "input_text",
                            }
                        ],
                        "role": "user",
                    }
                ],
                "type": "new_session",
            },
            type="once",
            metadata={},
        )
        assert_matches_type(Automation, automation, path=["response"])

    @parametrize
    async def test_raw_response_create_overload_2(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.automations.with_raw_response.create(
            name="x",
            run_at=1,
            target={
                "environment": {"type": "none"},
                "input": [
                    {
                        "content": [
                            {
                                "text": "text",
                                "type": "input_text",
                            }
                        ],
                        "role": "user",
                    }
                ],
                "type": "new_session",
            },
            type="once",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        automation = response.parse()
        assert_matches_type(Automation, automation, path=["response"])

    @parametrize
    async def test_streaming_response_create_overload_2(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.automations.with_streaming_response.create(
            name="x",
            run_at=1,
            target={
                "environment": {"type": "none"},
                "input": [
                    {
                        "content": [
                            {
                                "text": "text",
                                "type": "input_text",
                            }
                        ],
                        "role": "user",
                    }
                ],
                "type": "new_session",
            },
            type="once",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            automation = await response.parse()
            assert_matches_type(Automation, automation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        automation = await async_client.beta.agents.automations.retrieve(
            "automation_id",
        )
        assert_matches_type(Automation, automation, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.automations.with_raw_response.retrieve(
            "automation_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        automation = response.parse()
        assert_matches_type(Automation, automation, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.automations.with_streaming_response.retrieve(
            "automation_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            automation = await response.parse()
            assert_matches_type(Automation, automation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `automation_id` but received ''"):
            await async_client.beta.agents.automations.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncOpenAI) -> None:
        automation = await async_client.beta.agents.automations.update(
            automation_id="automation_id",
        )
        assert_matches_type(Automation, automation, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncOpenAI) -> None:
        automation = await async_client.beta.agents.automations.update(
            automation_id="automation_id",
            expression="x",
            metadata={"foo": "string"},
            name="x",
            run_at=0,
            target={
                "environment": {"type": "none"},
                "input": [
                    {
                        "content": [
                            {
                                "text": "text",
                                "type": "input_text",
                            }
                        ],
                        "role": "user",
                        "type": "message",
                    }
                ],
                "type": "new_session",
                "agent": {
                    "instructions": "instructions",
                    "model": "model",
                    "multi_agent": {
                        "enabled": True,
                        "max_concurrent_subagents": 1,
                    },
                    "reasoning": {
                        "effort": "none",
                        "summary": "concise",
                    },
                    "service_tier": "auto",
                    "text": {
                        "format": {"type": "text"},
                        "verbosity": "low",
                    },
                    "tools": [
                        {
                            "description": "description",
                            "name": "name",
                            "parameters": {"foo": "bar"},
                            "type": "function",
                            "defer_loading": True,
                        }
                    ],
                },
                "agent_id": "agent_id",
                "metadata": {"foo": "string"},
                "vault_ids": ["string"],
            },
            timezone="x",
        )
        assert_matches_type(Automation, automation, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.automations.with_raw_response.update(
            automation_id="automation_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        automation = response.parse()
        assert_matches_type(Automation, automation, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.automations.with_streaming_response.update(
            automation_id="automation_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            automation = await response.parse()
            assert_matches_type(Automation, automation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `automation_id` but received ''"):
            await async_client.beta.agents.automations.with_raw_response.update(
                automation_id="",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        automation = await async_client.beta.agents.automations.list()
        assert_matches_type(AsyncCursorPage[Automation], automation, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        automation = await async_client.beta.agents.automations.list(
            after="after",
            limit=1,
            order="asc",
            session_id="session_id",
        )
        assert_matches_type(AsyncCursorPage[Automation], automation, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.automations.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        automation = response.parse()
        assert_matches_type(AsyncCursorPage[Automation], automation, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.automations.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            automation = await response.parse()
            assert_matches_type(AsyncCursorPage[Automation], automation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, async_client: AsyncOpenAI) -> None:
        automation = await async_client.beta.agents.automations.delete(
            "automation_id",
        )
        assert_matches_type(AutomationDeleted, automation, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.automations.with_raw_response.delete(
            "automation_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        automation = response.parse()
        assert_matches_type(AutomationDeleted, automation, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.automations.with_streaming_response.delete(
            "automation_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            automation = await response.parse()
            assert_matches_type(AutomationDeleted, automation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `automation_id` but received ''"):
            await async_client.beta.agents.automations.with_raw_response.delete(
                "",
            )

    @parametrize
    async def test_method_pause(self, async_client: AsyncOpenAI) -> None:
        automation = await async_client.beta.agents.automations.pause(
            "automation_id",
        )
        assert_matches_type(Automation, automation, path=["response"])

    @parametrize
    async def test_raw_response_pause(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.automations.with_raw_response.pause(
            "automation_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        automation = response.parse()
        assert_matches_type(Automation, automation, path=["response"])

    @parametrize
    async def test_streaming_response_pause(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.automations.with_streaming_response.pause(
            "automation_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            automation = await response.parse()
            assert_matches_type(Automation, automation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_pause(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `automation_id` but received ''"):
            await async_client.beta.agents.automations.with_raw_response.pause(
                "",
            )

    @parametrize
    async def test_method_resume(self, async_client: AsyncOpenAI) -> None:
        automation = await async_client.beta.agents.automations.resume(
            "automation_id",
        )
        assert_matches_type(Automation, automation, path=["response"])

    @parametrize
    async def test_raw_response_resume(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.beta.agents.automations.with_raw_response.resume(
            "automation_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        automation = response.parse()
        assert_matches_type(Automation, automation, path=["response"])

    @parametrize
    async def test_streaming_response_resume(self, async_client: AsyncOpenAI) -> None:
        async with async_client.beta.agents.automations.with_streaming_response.resume(
            "automation_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            automation = await response.parse()
            assert_matches_type(Automation, automation, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_resume(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `automation_id` but received ''"):
            await async_client.beta.agents.automations.with_raw_response.resume(
                "",
            )
