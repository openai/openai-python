# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import httpx
import pytest
from respx import MockRouter

import openai._legacy_response as _legacy_response
from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types import (
    Video,
    VideoDeleteResponse,
)
from openai._utils import assert_signatures_in_sync
from openai.pagination import SyncConversationCursorPage, AsyncConversationCursorPage

# pyright: reportDeprecated=false

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


def _build_video(status: str, progress: int) -> Video:
    return Video.model_validate(
        {
            "id": "video_123",
            "created_at": 0,
            "model": "sora-2",
            "object": "video",
            "progress": progress,
            "seconds": "4",
            "size": "720x1280",
            "status": status,
        }
    )


class TestVideos:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        video = client.videos.create(
            prompt="x",
        )
        assert_matches_type(Video, video, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        video = client.videos.create(
            prompt="x",
            input_reference=b"raw file contents",
            model="string",
            seconds="4",
            size="720x1280",
        )
        assert_matches_type(Video, video, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.videos.with_raw_response.create(
            prompt="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        video = response.parse()
        assert_matches_type(Video, video, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.videos.with_streaming_response.create(
            prompt="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            video = response.parse()
            assert_matches_type(Video, video, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        video = client.videos.retrieve(
            "video_123",
        )
        assert_matches_type(Video, video, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.videos.with_raw_response.retrieve(
            "video_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        video = response.parse()
        assert_matches_type(Video, video, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.videos.with_streaming_response.retrieve(
            "video_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            video = response.parse()
            assert_matches_type(Video, video, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `video_id` but received ''"):
            client.videos.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        video = client.videos.list()
        assert_matches_type(SyncConversationCursorPage[Video], video, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        video = client.videos.list(
            after="after",
            limit=0,
            order="asc",
        )
        assert_matches_type(SyncConversationCursorPage[Video], video, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.videos.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        video = response.parse()
        assert_matches_type(SyncConversationCursorPage[Video], video, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.videos.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            video = response.parse()
            assert_matches_type(SyncConversationCursorPage[Video], video, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: OpenAI) -> None:
        video = client.videos.delete(
            "video_123",
        )
        assert_matches_type(VideoDeleteResponse, video, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: OpenAI) -> None:
        response = client.videos.with_raw_response.delete(
            "video_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        video = response.parse()
        assert_matches_type(VideoDeleteResponse, video, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: OpenAI) -> None:
        with client.videos.with_streaming_response.delete(
            "video_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            video = response.parse()
            assert_matches_type(VideoDeleteResponse, video, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `video_id` but received ''"):
            client.videos.with_raw_response.delete(
                "",
            )

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_download_content(self, client: OpenAI, respx_mock: MockRouter) -> None:
        respx_mock.get("/videos/video_123/content").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        video = client.videos.download_content(
            video_id="video_123",
        )
        assert isinstance(video, _legacy_response.HttpxBinaryResponseContent)
        assert video.json() == {"foo": "bar"}

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_download_content_with_all_params(self, client: OpenAI, respx_mock: MockRouter) -> None:
        respx_mock.get("/videos/video_123/content").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        video = client.videos.download_content(
            video_id="video_123",
            variant="video",
        )
        assert isinstance(video, _legacy_response.HttpxBinaryResponseContent)
        assert video.json() == {"foo": "bar"}

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_download_content(self, client: OpenAI, respx_mock: MockRouter) -> None:
        respx_mock.get("/videos/video_123/content").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        response = client.videos.with_raw_response.download_content(
            video_id="video_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        video = response.parse()
        assert_matches_type(_legacy_response.HttpxBinaryResponseContent, video, path=["response"])

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_download_content(self, client: OpenAI, respx_mock: MockRouter) -> None:
        respx_mock.get("/videos/video_123/content").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        with client.videos.with_streaming_response.download_content(
            video_id="video_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            video = response.parse()
            assert_matches_type(bytes, video, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_path_params_download_content(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `video_id` but received ''"):
            client.videos.with_raw_response.download_content(
                video_id="",
            )

    @parametrize
    def test_method_remix(self, client: OpenAI) -> None:
        video = client.videos.remix(
            video_id="video_123",
            prompt="x",
        )
        assert_matches_type(Video, video, path=["response"])

    @parametrize
    def test_raw_response_remix(self, client: OpenAI) -> None:
        response = client.videos.with_raw_response.remix(
            video_id="video_123",
            prompt="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        video = response.parse()
        assert_matches_type(Video, video, path=["response"])

    @parametrize
    def test_streaming_response_remix(self, client: OpenAI) -> None:
        with client.videos.with_streaming_response.remix(
            video_id="video_123",
            prompt="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            video = response.parse()
            assert_matches_type(Video, video, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_remix(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `video_id` but received ''"):
            client.videos.with_raw_response.remix(
                video_id="",
                prompt="x",
            )

    @parametrize
    def test_create_and_poll_respects_timeout(self, client: OpenAI, monkeypatch: pytest.MonkeyPatch) -> None:
        captured_timeouts: list[object] = []
        create_kwargs: dict[str, object] = {}
        create_video = _build_video("queued", 0)
        poll_responses = [
            (_build_video("in_progress", 50), {"openai-poll-after-ms": "10"}),
            (_build_video("completed", 100), {}),
        ]

        def fake_create(**kwargs: object) -> Video:
            create_kwargs.update(kwargs)
            return create_video

        class FakeResponse:
            def __init__(self, video: Video, headers: dict[str, str]) -> None:
                self._video = video
                self.headers = headers

            def parse(self) -> Video:
                return self._video

        def fake_retrieve(video_id: str, *, extra_headers: object, timeout: object) -> FakeResponse:
            video, headers = poll_responses.pop(0)
            captured_timeouts.append(timeout)
            return FakeResponse(video, headers)

        monkeypatch.setattr(client.videos, "create", fake_create)
        monkeypatch.setattr(client.videos.with_raw_response, "retrieve", fake_retrieve)
        monkeypatch.setattr(client.videos, "_sleep", lambda _: None)

        timeout_value = 123.0
        final_video = client.videos.create_and_poll(prompt="x", timeout=timeout_value)

        assert final_video.status == "completed"
        assert captured_timeouts == [timeout_value, timeout_value]
        assert poll_responses == []
        assert create_kwargs.get("timeout") == timeout_value

    @parametrize
    def test_remix_passes_timeout(self, client: OpenAI, monkeypatch: pytest.MonkeyPatch) -> None:
        captured: dict[str, object] = {}

        def fake_post(
            path: str,
            *,
            body: object,
            options: dict[str, object],
            cast_to: object,
            **kwargs: object,
        ) -> Video:
            captured["path"] = path
            captured["timeout"] = options.get("timeout")
            return _build_video("completed", 100)

        monkeypatch.setattr(client.videos, "_post", fake_post)

        timeout_value = 0.5
        video = client.videos.remix(video_id="video_123", prompt="x", timeout=timeout_value)

        assert video.status == "completed"
        assert captured["path"] == "/videos/video_123/remix"
        assert captured["timeout"] == timeout_value


class TestAsyncVideos:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        video = await async_client.videos.create(
            prompt="x",
        )
        assert_matches_type(Video, video, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncOpenAI) -> None:
        video = await async_client.videos.create(
            prompt="x",
            input_reference=b"raw file contents",
            model="string",
            seconds="4",
            size="720x1280",
        )
        assert_matches_type(Video, video, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.videos.with_raw_response.create(
            prompt="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        video = response.parse()
        assert_matches_type(Video, video, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.videos.with_streaming_response.create(
            prompt="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            video = await response.parse()
            assert_matches_type(Video, video, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        video = await async_client.videos.retrieve(
            "video_123",
        )
        assert_matches_type(Video, video, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.videos.with_raw_response.retrieve(
            "video_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        video = response.parse()
        assert_matches_type(Video, video, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.videos.with_streaming_response.retrieve(
            "video_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            video = await response.parse()
            assert_matches_type(Video, video, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `video_id` but received ''"):
            await async_client.videos.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        video = await async_client.videos.list()
        assert_matches_type(AsyncConversationCursorPage[Video], video, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        video = await async_client.videos.list(
            after="after",
            limit=0,
            order="asc",
        )
        assert_matches_type(AsyncConversationCursorPage[Video], video, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.videos.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        video = response.parse()
        assert_matches_type(AsyncConversationCursorPage[Video], video, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.videos.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            video = await response.parse()
            assert_matches_type(AsyncConversationCursorPage[Video], video, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, async_client: AsyncOpenAI) -> None:
        video = await async_client.videos.delete(
            "video_123",
        )
        assert_matches_type(VideoDeleteResponse, video, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.videos.with_raw_response.delete(
            "video_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        video = response.parse()
        assert_matches_type(VideoDeleteResponse, video, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncOpenAI) -> None:
        async with async_client.videos.with_streaming_response.delete(
            "video_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            video = await response.parse()
            assert_matches_type(VideoDeleteResponse, video, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `video_id` but received ''"):
            await async_client.videos.with_raw_response.delete(
                "",
            )

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_download_content(self, async_client: AsyncOpenAI, respx_mock: MockRouter) -> None:
        respx_mock.get("/videos/video_123/content").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        video = await async_client.videos.download_content(
            video_id="video_123",
        )
        assert isinstance(video, _legacy_response.HttpxBinaryResponseContent)
        assert video.json() == {"foo": "bar"}

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_download_content_with_all_params(
        self, async_client: AsyncOpenAI, respx_mock: MockRouter
    ) -> None:
        respx_mock.get("/videos/video_123/content").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        video = await async_client.videos.download_content(
            video_id="video_123",
            variant="video",
        )
        assert isinstance(video, _legacy_response.HttpxBinaryResponseContent)
        assert video.json() == {"foo": "bar"}

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_download_content(self, async_client: AsyncOpenAI, respx_mock: MockRouter) -> None:
        respx_mock.get("/videos/video_123/content").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        response = await async_client.videos.with_raw_response.download_content(
            video_id="video_123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        video = response.parse()
        assert_matches_type(_legacy_response.HttpxBinaryResponseContent, video, path=["response"])

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_download_content(self, async_client: AsyncOpenAI, respx_mock: MockRouter) -> None:
        respx_mock.get("/videos/video_123/content").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        async with async_client.videos.with_streaming_response.download_content(
            video_id="video_123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            video = await response.parse()
            assert_matches_type(bytes, video, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_path_params_download_content(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `video_id` but received ''"):
            await async_client.videos.with_raw_response.download_content(
                video_id="",
            )

    @parametrize
    async def test_method_remix(self, async_client: AsyncOpenAI) -> None:
        video = await async_client.videos.remix(
            video_id="video_123",
            prompt="x",
        )
        assert_matches_type(Video, video, path=["response"])

    @parametrize
    async def test_raw_response_remix(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.videos.with_raw_response.remix(
            video_id="video_123",
            prompt="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        video = response.parse()
        assert_matches_type(Video, video, path=["response"])

    @parametrize
    async def test_streaming_response_remix(self, async_client: AsyncOpenAI) -> None:
        async with async_client.videos.with_streaming_response.remix(
            video_id="video_123",
            prompt="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            video = await response.parse()
            assert_matches_type(Video, video, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_remix(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `video_id` but received ''"):
            await async_client.videos.with_raw_response.remix(
                video_id="",
                prompt="x",
            )

    @parametrize
    async def test_create_and_poll_respects_timeout(
        self, async_client: AsyncOpenAI, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        captured_timeouts: list[object] = []
        create_kwargs: dict[str, object] = {}
        create_video = _build_video("queued", 0)
        poll_responses = [
            (_build_video("in_progress", 50), {"openai-poll-after-ms": "10"}),
            (_build_video("completed", 100), {}),
        ]

        async def fake_create(**kwargs: object) -> Video:
            create_kwargs.update(kwargs)
            return create_video

        class FakeResponse:
            def __init__(self, video: Video, headers: dict[str, str]) -> None:
                self._video = video
                self.headers = headers

            def parse(self) -> Video:
                return self._video

        async def fake_retrieve(video_id: str, *, extra_headers: object, timeout: object) -> FakeResponse:
            video, headers = poll_responses.pop(0)
            captured_timeouts.append(timeout)
            return FakeResponse(video, headers)

        async def fake_sleep(_: float) -> None:
            return None

        monkeypatch.setattr(async_client.videos, "create", fake_create)
        monkeypatch.setattr(async_client.videos.with_raw_response, "retrieve", fake_retrieve)
        monkeypatch.setattr(async_client.videos, "_sleep", fake_sleep)

        timeout_value = 123.0
        final_video = await async_client.videos.create_and_poll(prompt="x", timeout=timeout_value)

        assert final_video.status == "completed"
        assert captured_timeouts == [timeout_value, timeout_value]
        assert poll_responses == []
        assert create_kwargs.get("timeout") == timeout_value

    @parametrize
    async def test_remix_passes_timeout(self, async_client: AsyncOpenAI, monkeypatch: pytest.MonkeyPatch) -> None:
        captured: dict[str, object] = {}

        async def fake_post(
            path: str,
            *,
            body: object,
            options: dict[str, object],
            cast_to: object,
            **kwargs: object,
        ) -> Video:
            captured["path"] = path
            captured["timeout"] = options.get("timeout")
            return _build_video("completed", 100)

        monkeypatch.setattr(async_client.videos, "_post", fake_post)

        timeout_value = 0.5
        video = await async_client.videos.remix(video_id="video_123", prompt="x", timeout=timeout_value)

        assert video.status == "completed"
        assert captured["path"] == "/videos/video_123/remix"
        assert captured["timeout"] == timeout_value


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_create_and_poll_method_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    assert_signatures_in_sync(
        checking_client.videos.create,
        checking_client.videos.create_and_poll,
        exclude_params={"extra_headers", "extra_query", "extra_body", "timeout"},
    )
