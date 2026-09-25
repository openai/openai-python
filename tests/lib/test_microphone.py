from __future__ import annotations

import io
import wave
from typing import Any, Generator
from contextlib import contextmanager
from unittest.mock import Mock

import numpy as np
import pytest
import numpy.typing as npt

from openai.helpers import microphone


@pytest.fixture
def samples(request: pytest.FixtureRequest) -> npt.NDArray[Any]:
    return np.array(request.param[1], dtype=request.param[0]).reshape(-1, 2)


@pytest.fixture
def recorder(monkeypatch: pytest.MonkeyPatch, samples: npt.NDArray[Any]) -> microphone.Microphone[Any]:
    class CallbackStop(Exception):
        pass

    @contextmanager
    def input_stream(**kwargs: Any) -> Generator[None, None, None]:
        assert kwargs["dtype"] == samples.dtype
        assert kwargs["channels"] == samples.shape[1]
        callback = kwargs["callback"]
        callback(samples, len(samples), None, None)
        with pytest.raises(CallbackStop):
            callback(samples, len(samples), None, None)
        yield

    monkeypatch.setattr(microphone, "sd", Mock(InputStream=input_stream, CallbackStop=CallbackStop))
    decisions = iter([True, False])
    return microphone.Microphone(
        channels=samples.shape[1], dtype=samples.dtype.type, should_record=lambda: next(decisions)
    )


@pytest.mark.parametrize(
    "samples,sample_width,expected",
    [
        ((np.float32, [-1, -0.5, 0, 0.25, 0.5, 1]), 2, [-32767, -16383, 0, 8191, 16383, 32767]),
        ((np.int8, [-128, -64, 0, 32, 64, 127]), 1, [0, 64, 128, 160, 192, 255]),
        ((np.uint8, [0, 64, 128, 160, 192, 255]), 1, [0, 64, 128, 160, 192, 255]),
        ((np.int16, [-32768, -16384, 0, 8192, 16384, 32767]), 2, [-32768, -16384, 0, 8192, 16384, 32767]),
        ((np.int32, [-2147483648, -1, 0, 1, 64, 2147483647]), 4, [-2147483648, -1, 0, 1, 64, 2147483647]),
    ],
    indirect=["samples"],
    ids=["float32", "int8", "uint8", "int16", "int32"],
)
@pytest.mark.parametrize("return_ndarray", [False, True], ids=["wav", "ndarray"])
async def test_record_sample_encoding(
    recorder: microphone.Microphone[Any],
    samples: npt.NDArray[Any],
    sample_width: int,
    expected: list[int],
    return_ndarray: bool,
) -> None:
    if return_ndarray:
        result = await recorder.record(return_ndarray=True)
        assert result.dtype == samples.dtype
        np.testing.assert_array_equal(result, samples)
        return

    file = await recorder.record()
    assert isinstance(file, tuple)
    assert len(file) == 3
    filename, content, media_type = file
    assert (filename, media_type) == ("audio.wav", "audio/wav")
    assert isinstance(content, io.BytesIO)
    with wave.open(content, "rb") as wav:
        assert wav.getnchannels() == samples.shape[1]
        assert wav.getframerate() == 24000
        assert wav.getnframes() == len(samples)
        assert wav.getsampwidth() == sample_width
        pcm = np.frombuffer(wav.readframes(len(samples)), dtype={1: "u1", 2: "<i2", 4: "<i4"}[sample_width])
        np.testing.assert_array_equal(pcm, expected)
