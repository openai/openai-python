from __future__ import annotations

import json
import array
import base64
import binascii
from typing import Any, cast
from typing_extensions import Literal

import httpx2
import pytest

from openai import OpenAI, AsyncOpenAI
from tests.respx2 import MockRouter
from openai._types import Omit, NotGiven, omit, not_given
from openai._models import construct_type_unchecked
from openai.lib._parsing import _embeddings as embeddings_parser
from openai.types.create_embedding_response import CreateEmbeddingResponse

VALUES = [0.125, -2.5, 3.75]
ENCODED = base64.b64encode(array.array("f", VALUES).tobytes()).decode("ascii")
EncodingFormat = Literal["float", "base64"] | Omit
ResponseMode = Literal["normal", "raw", "streaming"]


def response_body(*vectors: object) -> dict[str, object]:
    return {
        "data": [{"embedding": vector, "index": index, "object": "embedding"} for index, vector in enumerate(vectors)],
        "model": "text-embedding-3-small",
        "object": "list",
        "usage": {"prompt_tokens": 1, "total_tokens": 1},
    }


def make_response(*vectors: object) -> CreateEmbeddingResponse:
    return construct_type_unchecked(type_=CreateEmbeddingResponse, value=response_body(*vectors))


@pytest.fixture(params=[False, True], ids=["stdlib", "numpy"])
def decoder(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    use_numpy = cast(bool, request.param)
    if use_numpy:
        pytest.importorskip("numpy")
    monkeypatch.setattr(embeddings_parser, "has_numpy", lambda: use_numpy)


@pytest.mark.usefixtures("decoder")
@pytest.mark.parametrize("encoding_format", [omit, not_given], ids=["omit", "not-given"])
def test_decode_preserves_response_and_non_string_vectors(encoding_format: Omit | NotGiven) -> None:
    response = make_response(ENCODED, [4.0, 5.0], ENCODED)
    data = response.data
    unchanged_vector = data[1].embedding
    usage = response.usage

    parsed = embeddings_parser.parse_embedding_response(response, encoding_format=encoding_format)

    assert parsed is response
    assert parsed.data is data
    assert parsed.data[0].embedding == VALUES
    assert parsed.data[1].embedding is unchanged_vector
    assert parsed.data[2].embedding == VALUES
    assert parsed.usage is usage
    assert parsed.model == "text-embedding-3-small"


def test_decode_checks_numpy_once_per_response(monkeypatch: pytest.MonkeyPatch) -> None:
    checks = 0

    def has_numpy() -> bool:
        nonlocal checks
        checks += 1
        return False

    monkeypatch.setattr(embeddings_parser, "has_numpy", has_numpy)
    response = make_response(ENCODED, ENCODED, ENCODED)

    embeddings_parser.parse_embedding_response(response, encoding_format=omit)

    assert checks == 1


def test_decode_does_not_check_numpy_without_encoded_vectors(monkeypatch: pytest.MonkeyPatch) -> None:
    def unexpected_decoder() -> bool:
        raise AssertionError("a response without encoded vectors must not inspect the decoder")

    monkeypatch.setattr(embeddings_parser, "has_numpy", unexpected_decoder)
    response = make_response([1.0, 2.0], [3.0, 4.0])

    assert embeddings_parser.parse_embedding_response(response, encoding_format=omit) is response


@pytest.mark.parametrize("encoding_format", ["float", "base64", None])
@pytest.mark.parametrize("vectors", [(ENCODED,), ("abc",), ()], ids=["encoded", "invalid", "empty"])
def test_explicit_format_is_untouched(
    encoding_format: object, vectors: tuple[object, ...], monkeypatch: pytest.MonkeyPatch
) -> None:
    def unexpected_decoder() -> bool:
        raise AssertionError("an explicit format must not inspect the decoder")

    monkeypatch.setattr(embeddings_parser, "has_numpy", unexpected_decoder)
    response = make_response(*vectors)
    data = response.data
    original = [cast(object, item.embedding) for item in data]

    assert embeddings_parser.parse_embedding_response(response, encoding_format=cast(Any, encoding_format)) is response
    assert response.data is data
    assert [cast(object, item.embedding) for item in data] == original


@pytest.mark.parametrize("encoding_format", [omit, not_given], ids=["omit", "not-given"])
@pytest.mark.parametrize("data", [[], None], ids=["empty", "null"])
def test_missing_data_keeps_existing_error(encoding_format: Omit | NotGiven, data: object) -> None:
    body = response_body()
    body["data"] = data
    response = construct_type_unchecked(type_=CreateEmbeddingResponse, value=body)

    with pytest.raises(ValueError, match=r"^No embedding data received$"):
        embeddings_parser.parse_embedding_response(response, encoding_format=encoding_format)


@pytest.mark.usefixtures("decoder")
@pytest.mark.parametrize(
    "encoded,error",
    [("abc", binascii.Error), (base64.b64encode(b"abc").decode("ascii"), ValueError)],
    ids=["invalid-base64", "invalid-float-buffer"],
)
def test_invalid_data_preserves_decoder_errors(encoded: str, error: type[Exception]) -> None:
    response = make_response(encoded)

    with pytest.raises(error):
        embeddings_parser.parse_embedding_response(response, encoding_format=omit)


def assert_request_and_response(
    request: httpx2.Request, response: CreateEmbeddingResponse, encoding_format: EncodingFormat
) -> None:
    expected_format = encoding_format if isinstance(encoding_format, str) else "base64"
    body = json.loads(request.content)
    assert body == {
        "input": "test input",
        "model": "text-embedding-3-small",
        "user": "fake-user",
        "dimensions": 3,
        "encoding_format": expected_format,
    }
    expected_vector = ENCODED if encoding_format == "base64" else VALUES
    assert cast(object, response.data[0].embedding) == expected_vector


@pytest.mark.respx2()
@pytest.mark.usefixtures("decoder")
@pytest.mark.parametrize("client", [False], indirect=True)
@pytest.mark.parametrize("encoding_format", [omit, "float", "base64"], ids=["default", "float", "base64"])
@pytest.mark.parametrize("mode", ["normal", "raw", "streaming"])
def test_sync_create_uses_decoder(
    client: OpenAI, respx2_mock: MockRouter, encoding_format: EncodingFormat, mode: ResponseMode
) -> None:
    vector = VALUES if encoding_format == "float" else ENCODED
    route = respx2_mock.post(f"{str(client.base_url).rstrip('/')}/embeddings").mock(
        return_value=httpx2.Response(200, json=response_body(vector))
    )
    kwargs: dict[str, Any] = {
        "input": "test input",
        "model": "text-embedding-3-small",
        "user": "fake-user",
        "dimensions": 3,
        "encoding_format": encoding_format,
    }

    if mode == "normal":
        response = client.embeddings.create(**kwargs)
    elif mode == "raw":
        response = client.embeddings.with_raw_response.create(**kwargs).parse()
    else:
        with client.embeddings.with_streaming_response.create(**kwargs) as raw_response:
            response = raw_response.parse()

    assert route.call_count == 1
    assert_request_and_response(route.calls.last.request, response, encoding_format)


@pytest.mark.respx2()
@pytest.mark.usefixtures("decoder")
@pytest.mark.parametrize("async_client", [False], indirect=True)
@pytest.mark.parametrize("encoding_format", [omit, "float", "base64"], ids=["default", "float", "base64"])
@pytest.mark.parametrize("mode", ["normal", "raw", "streaming"])
async def test_async_create_uses_decoder(
    async_client: AsyncOpenAI, respx2_mock: MockRouter, encoding_format: EncodingFormat, mode: ResponseMode
) -> None:
    vector = VALUES if encoding_format == "float" else ENCODED
    route = respx2_mock.post(f"{str(async_client.base_url).rstrip('/')}/embeddings").mock(
        return_value=httpx2.Response(200, json=response_body(vector))
    )
    kwargs: dict[str, Any] = {
        "input": "test input",
        "model": "text-embedding-3-small",
        "user": "fake-user",
        "dimensions": 3,
        "encoding_format": encoding_format,
    }

    if mode == "normal":
        response = await async_client.embeddings.create(**kwargs)
    elif mode == "raw":
        response = (await async_client.embeddings.with_raw_response.create(**kwargs)).parse()
    else:
        async with async_client.embeddings.with_streaming_response.create(**kwargs) as raw_response:
            response = await raw_response.parse()

    assert route.call_count == 1
    assert_request_and_response(route.calls.last.request, response, encoding_format)
