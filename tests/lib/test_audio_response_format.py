from __future__ import annotations

import logging
from typing import Any, cast
from unittest.mock import Mock
from typing_extensions import Literal

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from tests.respx2 import MockRouter
from openai._types import Omit, omit, not_given
from openai.types.audio import (
    Translation,
    Transcription,
    TranslationVerbose,
    TranscriptionVerbose,
    TranscriptionDiarized,
    TranscriptionTextDeltaEvent,
)
from openai.resources.audio import translations, transcriptions
from openai.types.audio_response_format import AudioResponseFormat

AudioResource = Literal["transcriptions", "translations"]
ResponseMode = Literal["normal", "raw", "streaming"]
FORMAT_CASES = [
    pytest.param("transcriptions", omit, Transcription, id="transcription-default"),
    pytest.param("transcriptions", "json", Transcription, id="transcription-json"),
    pytest.param("transcriptions", "verbose_json", TranscriptionVerbose, id="transcription-verbose"),
    pytest.param("transcriptions", "diarized_json", TranscriptionDiarized, id="transcription-diarized"),
    pytest.param("transcriptions", "text", str, id="transcription-text"),
    pytest.param("transcriptions", "srt", str, id="transcription-srt"),
    pytest.param("transcriptions", "vtt", str, id="transcription-vtt"),
    pytest.param("translations", omit, Translation, id="translation-default"),
    pytest.param("translations", "json", Translation, id="translation-json"),
    pytest.param("translations", "verbose_json", TranslationVerbose, id="translation-verbose"),
    pytest.param("translations", "text", str, id="translation-text"),
    pytest.param("translations", "srt", str, id="translation-srt"),
    pytest.param("translations", "vtt", str, id="translation-vtt"),
]


def select_response_type(resource: AudioResource, response_format: object) -> type[object]:
    if resource == "transcriptions":
        return transcriptions._get_response_format_type(cast(Any, response_format))
    return translations._get_response_format_type(cast(Any, response_format))


@pytest.mark.parametrize("resource,response_format,expected_type", FORMAT_CASES)
def test_supported_formats_keep_exact_response_classes(
    resource: AudioResource, response_format: AudioResponseFormat | Omit, expected_type: type[object]
) -> None:
    assert select_response_type(resource, response_format) is expected_type


@pytest.mark.parametrize(
    "resource,expected_type",
    [("transcriptions", Transcription), ("translations", Translation)],
)
@pytest.mark.parametrize("response_format", [None, Omit()], ids=["none", "new-omit"])
def test_default_compatibility_values(
    resource: AudioResource, response_format: object, expected_type: type[object]
) -> None:
    assert select_response_type(resource, response_format) is expected_type


@pytest.mark.parametrize(
    "resource,response_format,expected_type",
    [
        ("transcriptions", "future-format", Transcription),
        ("transcriptions", not_given, Transcription),
        ("translations", "future-format", Translation),
        ("translations", not_given, Translation),
        ("translations", "diarized_json", Translation),
    ],
)
def test_fallback_keeps_resource_logger_and_method(
    resource: AudioResource, response_format: object, expected_type: type[object], monkeypatch: pytest.MonkeyPatch
) -> None:
    logger = Mock(spec=logging.Logger)
    module = transcriptions if resource == "transcriptions" else translations
    monkeypatch.setattr(module, "log", logger)

    assert select_response_type(resource, response_format) is expected_type

    if resource == "transcriptions":
        logger.warn.assert_called_once_with("Unexpected audio response format: %s", response_format)
        logger.warning.assert_not_called()
    else:
        logger.warning.assert_called_once_with("Unexpected audio response format: %s", response_format)
        logger.warn.assert_not_called()


def test_fallback_keeps_historical_logger_name_and_warning(caplog: pytest.LogCaptureFixture) -> None:
    logger = logging.getLogger("openai.audio.transcriptions")
    assert transcriptions.log is logger
    assert translations.log is logger

    with pytest.warns(DeprecationWarning, match="deprecated"):
        assert select_response_type("transcriptions", "future-format") is Transcription
    assert select_response_type("translations", "future-format") is Translation

    records = [record for record in caplog.records if record.name == logger.name]
    assert [(record.levelno, record.getMessage()) for record in records] == [
        (logging.WARNING, "Unexpected audio response format: future-format"),
        (logging.WARNING, "Unexpected audio response format: future-format"),
    ]


def make_response(expected_type: type[object]) -> httpx2.Response:
    if expected_type is str:
        return httpx2.Response(200, text="test transcript")
    return httpx2.Response(
        200,
        json={
            "text": "test transcript",
            "duration": 1.0,
            "language": "english",
            "segments": [],
            "task": "transcribe",
        },
    )


def assert_request_and_response(
    request: httpx2.Request,
    response: object,
    response_format: AudioResponseFormat | Omit,
    expected_type: type[object],
) -> None:
    assert type(response) is expected_type
    assert request.headers["content-type"].startswith("multipart/form-data; boundary=")
    if isinstance(response_format, Omit):
        assert b'name="response_format"' not in request.content
    else:
        assert f'name="response_format"\r\n\r\n{response_format}\r\n'.encode() in request.content


@pytest.mark.respx2()
@pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])
@pytest.mark.parametrize("resource,response_format,expected_type", FORMAT_CASES)
@pytest.mark.parametrize("mode", ["normal", "raw", "streaming"])
def test_sync_create_uses_selected_response_class(
    client: OpenAI,
    respx2_mock: MockRouter,
    resource: AudioResource,
    response_format: AudioResponseFormat | Omit,
    expected_type: type[object],
    mode: ResponseMode,
) -> None:
    route = respx2_mock.post(f"{str(client.base_url).rstrip('/')}/audio/{resource}").mock(
        return_value=make_response(expected_type)
    )
    audio = cast(Any, client.audio.transcriptions if resource == "transcriptions" else client.audio.translations)
    kwargs: dict[str, Any] = {"file": b"fake audio", "model": "whisper-1", "response_format": response_format}

    if mode == "normal":
        response = audio.create(**kwargs)
    elif mode == "raw":
        response = audio.with_raw_response.create(**kwargs).parse()
    else:
        with audio.with_streaming_response.create(**kwargs) as raw_response:
            response = raw_response.parse()

    assert route.call_count == 1
    assert_request_and_response(route.calls.last.request, response, response_format, expected_type)


@pytest.mark.respx2()
@pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])
@pytest.mark.parametrize("resource,response_format,expected_type", FORMAT_CASES)
@pytest.mark.parametrize("mode", ["normal", "raw", "streaming"])
async def test_async_create_uses_selected_response_class(
    async_client: AsyncOpenAI,
    respx2_mock: MockRouter,
    resource: AudioResource,
    response_format: AudioResponseFormat | Omit,
    expected_type: type[object],
    mode: ResponseMode,
) -> None:
    route = respx2_mock.post(f"{str(async_client.base_url).rstrip('/')}/audio/{resource}").mock(
        return_value=make_response(expected_type)
    )
    audio = cast(
        Any, async_client.audio.transcriptions if resource == "transcriptions" else async_client.audio.translations
    )
    kwargs: dict[str, Any] = {"file": b"fake audio", "model": "whisper-1", "response_format": response_format}

    if mode == "normal":
        response = await audio.create(**kwargs)
    elif mode == "raw":
        response = (await audio.with_raw_response.create(**kwargs)).parse()
    else:
        async with audio.with_streaming_response.create(**kwargs) as raw_response:
            response = await raw_response.parse()

    assert route.call_count == 1
    assert_request_and_response(route.calls.last.request, response, response_format, expected_type)


STREAM_BODY = 'event: transcript.text.delta\ndata: {"type":"transcript.text.delta","delta":"hello"}\n\ndata: [DONE]\n\n'


@pytest.mark.respx2()
def test_sync_transcription_stream_still_yields_events(client: OpenAI, respx2_mock: MockRouter) -> None:
    respx2_mock.post(f"{str(client.base_url).rstrip('/')}/audio/transcriptions").mock(
        return_value=httpx2.Response(200, content=STREAM_BODY, headers={"content-type": "text/event-stream"})
    )

    with client.audio.transcriptions.create(
        file=b"fake audio", model="gpt-4o-transcribe", response_format="json", stream=True
    ) as stream:
        events = list(stream)

    assert len(events) == 1
    assert isinstance(events[0], TranscriptionTextDeltaEvent)
    assert events[0].delta == "hello"


@pytest.mark.respx2()
async def test_async_transcription_stream_still_yields_events(
    async_client: AsyncOpenAI, respx2_mock: MockRouter
) -> None:
    respx2_mock.post(f"{str(async_client.base_url).rstrip('/')}/audio/transcriptions").mock(
        return_value=httpx2.Response(200, content=STREAM_BODY, headers={"content-type": "text/event-stream"})
    )

    async with await async_client.audio.transcriptions.create(
        file=b"fake audio", model="gpt-4o-transcribe", response_format="json", stream=True
    ) as stream:
        events = [event async for event in stream]

    assert len(events) == 1
    assert isinstance(events[0], TranscriptionTextDeltaEvent)
    assert events[0].delta == "hello"
