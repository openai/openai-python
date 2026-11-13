from __future__ import annotations

import asyncio
from typing import Any
from collections.abc import AsyncGenerator

import pytest

from openai.helpers import local_audio_player


class SilentOutputStream:
    def __init__(self, **kwargs: Any) -> None:
        pass

    def __enter__(self) -> SilentOutputStream:
        return self

    def __exit__(self, *args: Any) -> None:
        pass


async def test_play_stream_propagates_producer_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    async def broken_stream() -> AsyncGenerator[None, None]:
        if asyncio.current_task() is None:
            yield None
        raise RuntimeError("synthetic producer failure")

    monkeypatch.setattr(local_audio_player.sd, "OutputStream", SilentOutputStream)

    with pytest.raises(RuntimeError, match="synthetic producer failure"):
        await asyncio.wait_for(
            local_audio_player.LocalAudioPlayer().play_stream(broken_stream()),
            timeout=1,
        )
