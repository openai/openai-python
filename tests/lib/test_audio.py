from __future__ import annotations

import sys
import inspect
import typing_extensions
from typing import get_args

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import evaluate_forwardref
from openai._utils import assert_signatures_in_sync
from openai._compat import is_literal_type
from openai._utils._typing import is_union_type
from openai.types.audio_response_format import AudioResponseFormat


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_translation_create_overloads_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    fn = checking_client.audio.translations.create
    overload_response_formats: set[str] = set()

    for i, overload in enumerate(typing_extensions.get_overloads(fn)):
        assert_signatures_in_sync(
            fn,
            overload,
            exclude_params={"response_format", "stream"},
            description=f" for overload {i}",
        )

        sig = inspect.signature(overload)
        typ = evaluate_forwardref(
            sig.parameters["response_format"].annotation,
            globalns=sys.modules[fn.__module__].__dict__,
        )
        if is_union_type(typ):
            for arg in get_args(typ):
                if not is_literal_type(arg):
                    continue

                overload_response_formats.update(get_args(arg))
        elif is_literal_type(typ):
            overload_response_formats.update(get_args(typ))

    src_response_formats: set[str] = set(get_args(AudioResponseFormat))
    diff = src_response_formats.difference(overload_response_formats)
    assert len(diff) == 0, f"some response format options don't have overloads"


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_transcription_create_overloads_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    fn = checking_client.audio.transcriptions.create
    overload_response_formats: set[str] = set()

    for i, overload in enumerate(typing_extensions.get_overloads(fn)):
        assert_signatures_in_sync(
            fn,
            overload,
            exclude_params={"response_format", "stream"},
            description=f" for overload {i}",
        )

        sig = inspect.signature(overload)
        typ = evaluate_forwardref(
            sig.parameters["response_format"].annotation,
            globalns=sys.modules[fn.__module__].__dict__,
        )
        if is_union_type(typ):
            for arg in get_args(typ):
                if not is_literal_type(arg):
                    continue

                overload_response_formats.update(get_args(arg))
        elif is_literal_type(typ):
            overload_response_formats.update(get_args(typ))

    src_response_formats: set[str] = set(get_args(AudioResponseFormat))
    diff = src_response_formats.difference(overload_response_formats)
    assert len(diff) == 0, f"some response format options don't have overloads"
