# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.pagination import SyncConversationCursorPage, AsyncConversationCursorPage
from openai.types.admin.organization.projects import (
    ProjectSpendAlert,
    ProjectSpendAlertDeleted,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSpendAlerts:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        spend_alert = client.admin.organization.projects.spend_alerts.create(
            project_id="project_id",
            currency="USD",
            interval="month",
            notification_channel={
                "recipients": ["string"],
                "type": "email",
            },
            threshold_amount=0,
        )
        assert_matches_type(ProjectSpendAlert, spend_alert, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        spend_alert = client.admin.organization.projects.spend_alerts.create(
            project_id="project_id",
            currency="USD",
            interval="month",
            notification_channel={
                "recipients": ["string"],
                "type": "email",
                "subject_prefix": "subject_prefix",
            },
            threshold_amount=0,
        )
        assert_matches_type(ProjectSpendAlert, spend_alert, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.admin.organization.projects.spend_alerts.with_raw_response.create(
            project_id="project_id",
            currency="USD",
            interval="month",
            notification_channel={
                "recipients": ["string"],
                "type": "email",
            },
            threshold_amount=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        spend_alert = response.parse()
        assert_matches_type(ProjectSpendAlert, spend_alert, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.admin.organization.projects.spend_alerts.with_streaming_response.create(
            project_id="project_id",
            currency="USD",
            interval="month",
            notification_channel={
                "recipients": ["string"],
                "type": "email",
            },
            threshold_amount=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            spend_alert = response.parse()
            assert_matches_type(ProjectSpendAlert, spend_alert, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_create(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.admin.organization.projects.spend_alerts.with_raw_response.create(
                project_id="",
                currency="USD",
                interval="month",
                notification_channel={
                    "recipients": ["string"],
                    "type": "email",
                },
                threshold_amount=0,
            )

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        spend_alert = client.admin.organization.projects.spend_alerts.retrieve(
            alert_id="alert_id",
            project_id="project_id",
        )
        assert_matches_type(ProjectSpendAlert, spend_alert, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.admin.organization.projects.spend_alerts.with_raw_response.retrieve(
            alert_id="alert_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        spend_alert = response.parse()
        assert_matches_type(ProjectSpendAlert, spend_alert, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.admin.organization.projects.spend_alerts.with_streaming_response.retrieve(
            alert_id="alert_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            spend_alert = response.parse()
            assert_matches_type(ProjectSpendAlert, spend_alert, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.admin.organization.projects.spend_alerts.with_raw_response.retrieve(
                alert_id="alert_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `alert_id` but received ''"):
            client.admin.organization.projects.spend_alerts.with_raw_response.retrieve(
                alert_id="",
                project_id="project_id",
            )

    @parametrize
    def test_method_update(self, client: OpenAI) -> None:
        spend_alert = client.admin.organization.projects.spend_alerts.update(
            alert_id="alert_id",
            project_id="project_id",
            currency="USD",
            interval="month",
            notification_channel={
                "recipients": ["string"],
                "type": "email",
            },
            threshold_amount=0,
        )
        assert_matches_type(ProjectSpendAlert, spend_alert, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: OpenAI) -> None:
        spend_alert = client.admin.organization.projects.spend_alerts.update(
            alert_id="alert_id",
            project_id="project_id",
            currency="USD",
            interval="month",
            notification_channel={
                "recipients": ["string"],
                "type": "email",
                "subject_prefix": "subject_prefix",
            },
            threshold_amount=0,
        )
        assert_matches_type(ProjectSpendAlert, spend_alert, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: OpenAI) -> None:
        response = client.admin.organization.projects.spend_alerts.with_raw_response.update(
            alert_id="alert_id",
            project_id="project_id",
            currency="USD",
            interval="month",
            notification_channel={
                "recipients": ["string"],
                "type": "email",
            },
            threshold_amount=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        spend_alert = response.parse()
        assert_matches_type(ProjectSpendAlert, spend_alert, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: OpenAI) -> None:
        with client.admin.organization.projects.spend_alerts.with_streaming_response.update(
            alert_id="alert_id",
            project_id="project_id",
            currency="USD",
            interval="month",
            notification_channel={
                "recipients": ["string"],
                "type": "email",
            },
            threshold_amount=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            spend_alert = response.parse()
            assert_matches_type(ProjectSpendAlert, spend_alert, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.admin.organization.projects.spend_alerts.with_raw_response.update(
                alert_id="alert_id",
                project_id="",
                currency="USD",
                interval="month",
                notification_channel={
                    "recipients": ["string"],
                    "type": "email",
                },
                threshold_amount=0,
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `alert_id` but received ''"):
            client.admin.organization.projects.spend_alerts.with_raw_response.update(
                alert_id="",
                project_id="project_id",
                currency="USD",
                interval="month",
                notification_channel={
                    "recipients": ["string"],
                    "type": "email",
                },
                threshold_amount=0,
            )

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        spend_alert = client.admin.organization.projects.spend_alerts.list(
            project_id="project_id",
        )
        assert_matches_type(SyncConversationCursorPage[ProjectSpendAlert], spend_alert, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        spend_alert = client.admin.organization.projects.spend_alerts.list(
            project_id="project_id",
            after="after",
            before="before",
            limit=0,
            order="asc",
        )
        assert_matches_type(SyncConversationCursorPage[ProjectSpendAlert], spend_alert, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.admin.organization.projects.spend_alerts.with_raw_response.list(
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        spend_alert = response.parse()
        assert_matches_type(SyncConversationCursorPage[ProjectSpendAlert], spend_alert, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.admin.organization.projects.spend_alerts.with_streaming_response.list(
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            spend_alert = response.parse()
            assert_matches_type(SyncConversationCursorPage[ProjectSpendAlert], spend_alert, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.admin.organization.projects.spend_alerts.with_raw_response.list(
                project_id="",
            )

    @parametrize
    def test_method_delete(self, client: OpenAI) -> None:
        spend_alert = client.admin.organization.projects.spend_alerts.delete(
            alert_id="alert_id",
            project_id="project_id",
        )
        assert_matches_type(ProjectSpendAlertDeleted, spend_alert, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: OpenAI) -> None:
        response = client.admin.organization.projects.spend_alerts.with_raw_response.delete(
            alert_id="alert_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        spend_alert = response.parse()
        assert_matches_type(ProjectSpendAlertDeleted, spend_alert, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: OpenAI) -> None:
        with client.admin.organization.projects.spend_alerts.with_streaming_response.delete(
            alert_id="alert_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            spend_alert = response.parse()
            assert_matches_type(ProjectSpendAlertDeleted, spend_alert, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            client.admin.organization.projects.spend_alerts.with_raw_response.delete(
                alert_id="alert_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `alert_id` but received ''"):
            client.admin.organization.projects.spend_alerts.with_raw_response.delete(
                alert_id="",
                project_id="project_id",
            )


class TestAsyncSpendAlerts:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        spend_alert = await async_client.admin.organization.projects.spend_alerts.create(
            project_id="project_id",
            currency="USD",
            interval="month",
            notification_channel={
                "recipients": ["string"],
                "type": "email",
            },
            threshold_amount=0,
        )
        assert_matches_type(ProjectSpendAlert, spend_alert, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncOpenAI) -> None:
        spend_alert = await async_client.admin.organization.projects.spend_alerts.create(
            project_id="project_id",
            currency="USD",
            interval="month",
            notification_channel={
                "recipients": ["string"],
                "type": "email",
                "subject_prefix": "subject_prefix",
            },
            threshold_amount=0,
        )
        assert_matches_type(ProjectSpendAlert, spend_alert, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.projects.spend_alerts.with_raw_response.create(
            project_id="project_id",
            currency="USD",
            interval="month",
            notification_channel={
                "recipients": ["string"],
                "type": "email",
            },
            threshold_amount=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        spend_alert = response.parse()
        assert_matches_type(ProjectSpendAlert, spend_alert, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.projects.spend_alerts.with_streaming_response.create(
            project_id="project_id",
            currency="USD",
            interval="month",
            notification_channel={
                "recipients": ["string"],
                "type": "email",
            },
            threshold_amount=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            spend_alert = await response.parse()
            assert_matches_type(ProjectSpendAlert, spend_alert, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_create(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.admin.organization.projects.spend_alerts.with_raw_response.create(
                project_id="",
                currency="USD",
                interval="month",
                notification_channel={
                    "recipients": ["string"],
                    "type": "email",
                },
                threshold_amount=0,
            )

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        spend_alert = await async_client.admin.organization.projects.spend_alerts.retrieve(
            alert_id="alert_id",
            project_id="project_id",
        )
        assert_matches_type(ProjectSpendAlert, spend_alert, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.projects.spend_alerts.with_raw_response.retrieve(
            alert_id="alert_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        spend_alert = response.parse()
        assert_matches_type(ProjectSpendAlert, spend_alert, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.projects.spend_alerts.with_streaming_response.retrieve(
            alert_id="alert_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            spend_alert = await response.parse()
            assert_matches_type(ProjectSpendAlert, spend_alert, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.admin.organization.projects.spend_alerts.with_raw_response.retrieve(
                alert_id="alert_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `alert_id` but received ''"):
            await async_client.admin.organization.projects.spend_alerts.with_raw_response.retrieve(
                alert_id="",
                project_id="project_id",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncOpenAI) -> None:
        spend_alert = await async_client.admin.organization.projects.spend_alerts.update(
            alert_id="alert_id",
            project_id="project_id",
            currency="USD",
            interval="month",
            notification_channel={
                "recipients": ["string"],
                "type": "email",
            },
            threshold_amount=0,
        )
        assert_matches_type(ProjectSpendAlert, spend_alert, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncOpenAI) -> None:
        spend_alert = await async_client.admin.organization.projects.spend_alerts.update(
            alert_id="alert_id",
            project_id="project_id",
            currency="USD",
            interval="month",
            notification_channel={
                "recipients": ["string"],
                "type": "email",
                "subject_prefix": "subject_prefix",
            },
            threshold_amount=0,
        )
        assert_matches_type(ProjectSpendAlert, spend_alert, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.projects.spend_alerts.with_raw_response.update(
            alert_id="alert_id",
            project_id="project_id",
            currency="USD",
            interval="month",
            notification_channel={
                "recipients": ["string"],
                "type": "email",
            },
            threshold_amount=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        spend_alert = response.parse()
        assert_matches_type(ProjectSpendAlert, spend_alert, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.projects.spend_alerts.with_streaming_response.update(
            alert_id="alert_id",
            project_id="project_id",
            currency="USD",
            interval="month",
            notification_channel={
                "recipients": ["string"],
                "type": "email",
            },
            threshold_amount=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            spend_alert = await response.parse()
            assert_matches_type(ProjectSpendAlert, spend_alert, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.admin.organization.projects.spend_alerts.with_raw_response.update(
                alert_id="alert_id",
                project_id="",
                currency="USD",
                interval="month",
                notification_channel={
                    "recipients": ["string"],
                    "type": "email",
                },
                threshold_amount=0,
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `alert_id` but received ''"):
            await async_client.admin.organization.projects.spend_alerts.with_raw_response.update(
                alert_id="",
                project_id="project_id",
                currency="USD",
                interval="month",
                notification_channel={
                    "recipients": ["string"],
                    "type": "email",
                },
                threshold_amount=0,
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        spend_alert = await async_client.admin.organization.projects.spend_alerts.list(
            project_id="project_id",
        )
        assert_matches_type(AsyncConversationCursorPage[ProjectSpendAlert], spend_alert, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        spend_alert = await async_client.admin.organization.projects.spend_alerts.list(
            project_id="project_id",
            after="after",
            before="before",
            limit=0,
            order="asc",
        )
        assert_matches_type(AsyncConversationCursorPage[ProjectSpendAlert], spend_alert, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.projects.spend_alerts.with_raw_response.list(
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        spend_alert = response.parse()
        assert_matches_type(AsyncConversationCursorPage[ProjectSpendAlert], spend_alert, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.projects.spend_alerts.with_streaming_response.list(
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            spend_alert = await response.parse()
            assert_matches_type(AsyncConversationCursorPage[ProjectSpendAlert], spend_alert, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.admin.organization.projects.spend_alerts.with_raw_response.list(
                project_id="",
            )

    @parametrize
    async def test_method_delete(self, async_client: AsyncOpenAI) -> None:
        spend_alert = await async_client.admin.organization.projects.spend_alerts.delete(
            alert_id="alert_id",
            project_id="project_id",
        )
        assert_matches_type(ProjectSpendAlertDeleted, spend_alert, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.admin.organization.projects.spend_alerts.with_raw_response.delete(
            alert_id="alert_id",
            project_id="project_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        spend_alert = response.parse()
        assert_matches_type(ProjectSpendAlertDeleted, spend_alert, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncOpenAI) -> None:
        async with async_client.admin.organization.projects.spend_alerts.with_streaming_response.delete(
            alert_id="alert_id",
            project_id="project_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            spend_alert = await response.parse()
            assert_matches_type(ProjectSpendAlertDeleted, spend_alert, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `project_id` but received ''"):
            await async_client.admin.organization.projects.spend_alerts.with_raw_response.delete(
                alert_id="alert_id",
                project_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `alert_id` but received ''"):
            await async_client.admin.organization.projects.spend_alerts.with_raw_response.delete(
                alert_id="",
                project_id="project_id",
            )
