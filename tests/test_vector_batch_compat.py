from __future__ import annotations

import json
from typing import Any

import httpx2
import pytest
from pydantic import ValidationError

from openai import OpenAI, AsyncOpenAI, APIResponseValidationError
from openai._compat import parse_obj, model_dump
from openai.types.vector_stores import VectorStoreFileBatch


def batch_payload(object_value: Any = "vector_store.file_batch") -> dict[str, Any]:
    return {
        "id": "vsfb_test",
        "object": object_value,
        "created_at": 123,
        "file_counts": {"cancelled": 0, "completed": 1, "failed": 0, "in_progress": 0, "total": 1},
        "status": "completed",
        "vector_store_id": "vs_test",
        "future_field": {"preserved": True},
    }


def transport(payload: dict[str, Any]) -> httpx2.MockTransport:
    return httpx2.MockTransport(
        lambda _request: httpx2.Response(200, json=payload, headers={"x-request-id": "req_test"})
    )


def assert_preserved(result: VectorStoreFileBatch, payload: dict[str, Any]) -> None:
    assert model_dump(result) == payload
    assert json.loads(result.to_json()) == payload
    assert set(payload) - {"future_field"} <= result.model_fields_set
    assert result._request_id == "req_test"


@pytest.mark.parametrize("object_value", ["vector_store.file_batch", "vector_store.files_batch"])
@pytest.mark.parametrize("strict", [False, True])
@pytest.mark.parametrize("operation", ["create", "retrieve", "cancel", "poll"])
def test_sync_responses(object_value: str, strict: bool, operation: str) -> None:
    payload = batch_payload(object_value)
    with OpenAI(
        api_key="test-key",
        _strict_response_validation=strict,
        http_client=httpx2.Client(transport=transport(payload)),
    ) as client:
        batches = client.vector_stores.file_batches
        if operation == "create":
            result = batches.create(vector_store_id="vs_test", file_ids=["file_test"])
        elif operation == "cancel":
            result = batches.cancel("vsfb_test", vector_store_id="vs_test")
        elif operation == "poll":
            result = batches.poll("vsfb_test", vector_store_id="vs_test")
        else:
            result = batches.retrieve("vsfb_test", vector_store_id="vs_test")
        assert_preserved(result, payload)


@pytest.mark.parametrize("object_value", ["vector_store.file_batch", "vector_store.files_batch"])
@pytest.mark.parametrize("strict", [False, True])
@pytest.mark.parametrize("operation", ["create", "retrieve", "cancel", "poll"])
async def test_async_responses(object_value: str, strict: bool, operation: str) -> None:
    payload = batch_payload(object_value)
    async with AsyncOpenAI(
        api_key="test-key",
        _strict_response_validation=strict,
        http_client=httpx2.AsyncClient(transport=transport(payload)),
    ) as client:
        batches = client.vector_stores.file_batches
        if operation == "create":
            result = await batches.create(vector_store_id="vs_test", file_ids=["file_test"])
        elif operation == "cancel":
            result = await batches.cancel("vsfb_test", vector_store_id="vs_test")
        elif operation == "poll":
            result = await batches.poll("vsfb_test", vector_store_id="vs_test")
        else:
            result = await batches.retrieve("vsfb_test", vector_store_id="vs_test")
        assert_preserved(result, payload)


@pytest.mark.parametrize(
    "change",
    [
        {"object": "unknown"},
        {"object": None},
        {"object": 123},
        {"status": "unknown"},
        {"file_counts": {"total": "invalid"}},
        {"created_at": "invalid"},
    ],
)
def test_other_validation_errors_survive(change: dict[str, Any]) -> None:
    payload = {**batch_payload(), **change}
    with OpenAI(
        api_key="test-key",
        _strict_response_validation=True,
        http_client=httpx2.Client(transport=transport(payload)),
    ) as client:
        with pytest.raises(APIResponseValidationError) as error:
            client.vector_stores.file_batches.retrieve("vsfb_test", vector_store_id="vs_test")
        assert error.value.body == payload


async def test_async_other_fields_still_validate() -> None:
    payload = {**batch_payload(), "status": "unknown"}
    async with AsyncOpenAI(
        api_key="test-key",
        _strict_response_validation=True,
        http_client=httpx2.AsyncClient(transport=transport(payload)),
    ) as client:
        with pytest.raises(APIResponseValidationError) as error:
            await client.vector_stores.file_batches.retrieve("vsfb_test", vector_store_id="vs_test")
        assert error.value.body == payload


def test_missing_discriminator_still_fails() -> None:
    payload = batch_payload()
    del payload["object"]
    with OpenAI(
        api_key="test-key",
        _strict_response_validation=True,
        http_client=httpx2.Client(transport=transport(payload)),
    ) as client:
        with pytest.raises(APIResponseValidationError):
            client.vector_stores.file_batches.retrieve("vsfb_test", vector_store_id="vs_test")


def test_validation_copy_does_not_modify_input() -> None:
    payload = batch_payload()
    with OpenAI(
        api_key="test-key",
        _strict_response_validation=True,
        http_client=httpx2.Client(transport=transport(payload)),
    ) as client:
        result = client._process_response_data(
            data=payload, cast_to=VectorStoreFileBatch, response=httpx2.Response(200)
        )
    assert payload == batch_payload()
    assert model_dump(result) == payload
    assert (
        result.model_fields_set
        == parse_obj(VectorStoreFileBatch, batch_payload("vector_store.files_batch")).model_fields_set
    )


def test_direct_validation_and_other_models_are_unchanged() -> None:
    legacy = batch_payload("vector_store.files_batch")
    assert model_dump(parse_obj(VectorStoreFileBatch, legacy)) == legacy
    with pytest.raises(ValidationError):
        parse_obj(VectorStoreFileBatch, batch_payload())

    class OtherBatch(VectorStoreFileBatch):
        pass

    with OpenAI(
        api_key="test-key",
        _strict_response_validation=True,
        http_client=httpx2.Client(transport=transport(batch_payload())),
    ) as client:
        with pytest.raises(APIResponseValidationError):
            client._process_response_data(
                data=batch_payload(),
                cast_to=OtherBatch,
                response=httpx2.Response(200, request=httpx2.Request("GET", "https://example.test")),
            )


def test_unknown_value_remains_permissive_without_strict_validation() -> None:
    payload = batch_payload("unknown")
    with OpenAI(api_key="test-key", http_client=httpx2.Client(transport=transport(payload))) as client:
        result = client.vector_stores.file_batches.retrieve("vsfb_test", vector_store_id="vs_test")
        assert_preserved(result, payload)
