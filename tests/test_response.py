from typing import List

import httpx
import pytest

from openai._response import (
    APIResponse,
    BaseAPIResponse,
    AsyncAPIResponse,
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    extract_response_type,
)


class ConcreteBaseAPIResponse(APIResponse[bytes]):
    ...


class ConcreteAPIResponse(APIResponse[List[str]]):
    ...


class ConcreteAsyncAPIResponse(APIResponse[httpx.Response]):
    ...


def test_extract_response_type_direct_classes() -> None:
    assert extract_response_type(BaseAPIResponse[str]) == str
    assert extract_response_type(APIResponse[str]) == str
    assert extract_response_type(AsyncAPIResponse[str]) == str


def test_extract_response_type_direct_class_missing_type_arg() -> None:
    with pytest.raises(
        RuntimeError,
        match="Expected type <class 'openai._response.AsyncAPIResponse'> to have a type argument at index 0 but it did not",
    ):
        extract_response_type(AsyncAPIResponse)


def test_extract_response_type_concrete_subclasses() -> None:
    assert extract_response_type(ConcreteBaseAPIResponse) == bytes
    assert extract_response_type(ConcreteAPIResponse) == List[str]
    assert extract_response_type(ConcreteAsyncAPIResponse) == httpx.Response


def test_extract_response_type_binary_response() -> None:
    assert extract_response_type(BinaryAPIResponse) == bytes
    assert extract_response_type(AsyncBinaryAPIResponse) == bytes
