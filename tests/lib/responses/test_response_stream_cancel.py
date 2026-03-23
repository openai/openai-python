from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from openai._types import Omit
from openai._streaming import Stream, AsyncStream
from openai.types.responses import Response
from openai.lib.streaming.responses._responses import (
    ResponseStream,
    AsyncResponseStream,
    ResponseStreamState,
)


def _make_state_with_snapshot(response_id: str = "resp_123") -> ResponseStreamState[object]:
    """Create a ResponseStreamState that has a snapshot with a given id."""
    from openai.types.responses.response import Response as RawResponse
    from openai.types.responses.response_created_event import ResponseCreatedEvent

    state = ResponseStreamState(text_format=Omit(), input_tools=Omit())

    raw_response = RawResponse.construct(
        id=response_id,
        object="response",
        created_at=0,
        status="in_progress",
        output=[],
        model="gpt-4o",
        parallel_tool_calls=True,
        tool_choice="auto",
        tools=[],
        temperature=1.0,
        top_p=1.0,
        max_output_tokens=None,
        max_tool_calls=None,
        previous_response_id=None,
        reasoning=None,
        truncation="disabled",
        error=None,
        incomplete_details=None,
        instructions=None,
        metadata={},
        text={"format": {"type": "text"}},
        usage=None,
        user=None,
        background=False,
        store=True,
    )

    event = ResponseCreatedEvent.construct(
        type="response.created",
        response=raw_response,
        sequence_number=0,
    )

    state.handle_event(event)
    return state


class TestResponseStreamCancel:
    def test_response_id_none_initially(self) -> None:
        raw_stream = MagicMock(spec=Stream)
        raw_stream.response = MagicMock()

        stream = ResponseStream(
            raw_stream=raw_stream,
            text_format=Omit(),
            input_tools=Omit(),
            starting_after=None,
        )

        assert stream.response_id is None

    def test_response_id_available_after_event(self) -> None:
        raw_stream = MagicMock(spec=Stream)
        raw_stream.response = MagicMock()

        stream = ResponseStream(
            raw_stream=raw_stream,
            text_format=Omit(),
            input_tools=Omit(),
            starting_after=None,
        )

        stream._state = _make_state_with_snapshot("resp_abc")
        assert stream.response_id == "resp_abc"

    def test_cancel_raises_when_no_response_id(self) -> None:
        raw_stream = MagicMock(spec=Stream)
        raw_stream.response = MagicMock()

        stream = ResponseStream(
            raw_stream=raw_stream,
            text_format=Omit(),
            input_tools=Omit(),
            starting_after=None,
            cancel_response=MagicMock(),
        )

        with pytest.raises(ValueError, match="response ID not yet available"):
            stream.cancel()

    def test_cancel_raises_when_no_callback(self) -> None:
        raw_stream = MagicMock(spec=Stream)
        raw_stream.response = MagicMock()

        stream = ResponseStream(
            raw_stream=raw_stream,
            text_format=Omit(),
            input_tools=Omit(),
            starting_after=None,
        )

        stream._state = _make_state_with_snapshot("resp_abc")

        with pytest.raises(ValueError, match="Cancel not available"):
            stream.cancel()

    def test_cancel_calls_callback_and_closes(self) -> None:
        raw_stream = MagicMock(spec=Stream)
        raw_stream.response = MagicMock()

        mock_response = MagicMock(spec=Response)
        cancel_fn = MagicMock(return_value=mock_response)

        stream = ResponseStream(
            raw_stream=raw_stream,
            text_format=Omit(),
            input_tools=Omit(),
            starting_after=None,
            cancel_response=cancel_fn,
        )

        stream._state = _make_state_with_snapshot("resp_xyz")

        result = stream.cancel()

        cancel_fn.assert_called_once_with("resp_xyz")
        raw_stream.response.close.assert_called_once()
        assert result is mock_response


class TestAsyncResponseStreamCancel:
    def test_response_id_none_initially(self) -> None:
        raw_stream = MagicMock(spec=AsyncStream)
        raw_stream.response = MagicMock()

        stream = AsyncResponseStream(
            raw_stream=raw_stream,
            text_format=Omit(),
            input_tools=Omit(),
            starting_after=None,
        )

        assert stream.response_id is None

    def test_response_id_available_after_event(self) -> None:
        raw_stream = MagicMock(spec=AsyncStream)
        raw_stream.response = MagicMock()

        stream = AsyncResponseStream(
            raw_stream=raw_stream,
            text_format=Omit(),
            input_tools=Omit(),
            starting_after=None,
        )

        stream._state = _make_state_with_snapshot("resp_abc")
        assert stream.response_id == "resp_abc"

    @pytest.mark.asyncio
    async def test_cancel_raises_when_no_response_id(self) -> None:
        raw_stream = MagicMock(spec=AsyncStream)
        raw_stream.response = MagicMock()

        stream = AsyncResponseStream(
            raw_stream=raw_stream,
            text_format=Omit(),
            input_tools=Omit(),
            starting_after=None,
            cancel_response=AsyncMock(),
        )

        with pytest.raises(ValueError, match="response ID not yet available"):
            await stream.cancel()

    @pytest.mark.asyncio
    async def test_cancel_calls_callback_and_closes(self) -> None:
        raw_stream = MagicMock(spec=AsyncStream)
        raw_stream.response = MagicMock()
        raw_stream.response.aclose = AsyncMock()

        mock_response = MagicMock(spec=Response)
        cancel_fn = AsyncMock(return_value=mock_response)

        stream = AsyncResponseStream(
            raw_stream=raw_stream,
            text_format=Omit(),
            input_tools=Omit(),
            starting_after=None,
            cancel_response=cancel_fn,
        )

        stream._state = _make_state_with_snapshot("resp_xyz")

        result = await stream.cancel()

        cancel_fn.assert_called_once_with("resp_xyz")
        raw_stream.response.aclose.assert_called_once()
        assert result is mock_response


class TestResponseStreamStateSnapshot:
    def test_current_snapshot_none_initially(self) -> None:
        state = ResponseStreamState(text_format=Omit(), input_tools=Omit())
        assert state.current_snapshot is None

    def test_current_snapshot_available_after_event(self) -> None:
        state = _make_state_with_snapshot("resp_test")
        assert state.current_snapshot is not None
        assert state.current_snapshot.id == "resp_test"
