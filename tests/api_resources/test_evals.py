# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openai import OpenAI, AsyncOpenAI
from tests.utils import assert_matches_type
from openai.types import (
    EvalListResponse,
    EvalCreateResponse,
    EvalDeleteResponse,
    EvalUpdateResponse,
    EvalRetrieveResponse,
)
from openai.pagination import SyncCursorPage, AsyncCursorPage

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEvals:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: OpenAI) -> None:
        eval = client.evals.create(
            data_source_config={
                "item_schema": {
                    "0": "bar",
                    "1": "bar",
                    "2": "bar",
                    "3": "bar",
                    "4": "bar",
                    "5": "bar",
                    "6": "bar",
                    "7": "bar",
                    "8": "bar",
                    "9": "bar",
                    "10": "bar",
                    "11": "bar",
                    "12": "bar",
                    "13": "bar",
                    "14": "bar",
                    "15": "bar",
                    "16": "bar",
                    "17": "bar",
                    "18": "bar",
                    "19": "bar",
                    "20": "bar",
                    "21": "bar",
                    "22": "bar",
                    "23": "bar",
                    "24": "bar",
                    "25": "bar",
                    "26": "bar",
                    "27": "bar",
                    "28": "bar",
                    "29": "bar",
                    "30": "bar",
                    "31": "bar",
                    "32": "bar",
                    "33": "bar",
                    "34": "bar",
                    "35": "bar",
                    "36": "bar",
                    "37": "bar",
                    "38": "bar",
                    "39": "bar",
                    "40": "bar",
                    "41": "bar",
                    "42": "bar",
                    "43": "bar",
                    "44": "bar",
                    "45": "bar",
                    "46": "bar",
                    "47": "bar",
                    "48": "bar",
                    "49": "bar",
                    "50": "bar",
                    "51": "bar",
                    "52": "bar",
                    "53": "bar",
                    "54": "bar",
                    "55": "bar",
                    "56": "bar",
                    "57": "bar",
                    "58": "bar",
                    "59": "bar",
                    "60": "bar",
                    "61": "bar",
                    "62": "bar",
                    "63": "bar",
                    "64": "bar",
                    "65": "bar",
                    "66": "bar",
                    "67": "bar",
                    "68": "bar",
                    "69": "bar",
                    "70": "bar",
                    "71": "bar",
                    "72": "bar",
                    "73": "bar",
                    "74": "bar",
                    "75": "bar",
                    "76": "bar",
                    "77": "bar",
                    "78": "bar",
                    "79": "bar",
                    "80": "bar",
                    "81": "bar",
                    "82": "bar",
                    "83": "bar",
                    "84": "bar",
                    "85": "bar",
                    "86": "bar",
                    "87": "bar",
                    "88": "bar",
                    "89": "bar",
                    "90": "bar",
                    "91": "bar",
                    "92": "bar",
                    "93": "bar",
                    "94": "bar",
                    "95": "bar",
                    "96": "bar",
                    "97": "bar",
                    "98": "bar",
                    "99": "bar",
                    "100": "bar",
                    "101": "bar",
                    "102": "bar",
                    "103": "bar",
                    "104": "bar",
                    "105": "bar",
                    "106": "bar",
                    "107": "bar",
                    "108": "bar",
                    "109": "bar",
                    "110": "bar",
                    "111": "bar",
                    "112": "bar",
                    "113": "bar",
                    "114": "bar",
                    "115": "bar",
                    "116": "bar",
                    "117": "bar",
                    "118": "bar",
                    "119": "bar",
                    "120": "bar",
                    "121": "bar",
                    "122": "bar",
                    "123": "bar",
                    "124": "bar",
                    "125": "bar",
                    "126": "bar",
                    "127": "bar",
                    "128": "bar",
                    "129": "bar",
                    "130": "bar",
                    "131": "bar",
                    "132": "bar",
                    "133": "bar",
                    "134": "bar",
                    "135": "bar",
                    "136": "bar",
                    "137": "bar",
                    "138": "bar",
                    "139": "bar",
                },
                "type": "custom",
            },
            testing_criteria=[
                {
                    "input": [
                        {
                            "content": "content",
                            "role": "role",
                        }
                    ],
                    "labels": ["string"],
                    "model": "model",
                    "name": "name",
                    "passing_labels": ["string"],
                    "type": "label_model",
                }
            ],
        )
        assert_matches_type(EvalCreateResponse, eval, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: OpenAI) -> None:
        eval = client.evals.create(
            data_source_config={
                "item_schema": {
                    "0": "bar",
                    "1": "bar",
                    "2": "bar",
                    "3": "bar",
                    "4": "bar",
                    "5": "bar",
                    "6": "bar",
                    "7": "bar",
                    "8": "bar",
                    "9": "bar",
                    "10": "bar",
                    "11": "bar",
                    "12": "bar",
                    "13": "bar",
                    "14": "bar",
                    "15": "bar",
                    "16": "bar",
                    "17": "bar",
                    "18": "bar",
                    "19": "bar",
                    "20": "bar",
                    "21": "bar",
                    "22": "bar",
                    "23": "bar",
                    "24": "bar",
                    "25": "bar",
                    "26": "bar",
                    "27": "bar",
                    "28": "bar",
                    "29": "bar",
                    "30": "bar",
                    "31": "bar",
                    "32": "bar",
                    "33": "bar",
                    "34": "bar",
                    "35": "bar",
                    "36": "bar",
                    "37": "bar",
                    "38": "bar",
                    "39": "bar",
                    "40": "bar",
                    "41": "bar",
                    "42": "bar",
                    "43": "bar",
                    "44": "bar",
                    "45": "bar",
                    "46": "bar",
                    "47": "bar",
                    "48": "bar",
                    "49": "bar",
                    "50": "bar",
                    "51": "bar",
                    "52": "bar",
                    "53": "bar",
                    "54": "bar",
                    "55": "bar",
                    "56": "bar",
                    "57": "bar",
                    "58": "bar",
                    "59": "bar",
                    "60": "bar",
                    "61": "bar",
                    "62": "bar",
                    "63": "bar",
                    "64": "bar",
                    "65": "bar",
                    "66": "bar",
                    "67": "bar",
                    "68": "bar",
                    "69": "bar",
                    "70": "bar",
                    "71": "bar",
                    "72": "bar",
                    "73": "bar",
                    "74": "bar",
                    "75": "bar",
                    "76": "bar",
                    "77": "bar",
                    "78": "bar",
                    "79": "bar",
                    "80": "bar",
                    "81": "bar",
                    "82": "bar",
                    "83": "bar",
                    "84": "bar",
                    "85": "bar",
                    "86": "bar",
                    "87": "bar",
                    "88": "bar",
                    "89": "bar",
                    "90": "bar",
                    "91": "bar",
                    "92": "bar",
                    "93": "bar",
                    "94": "bar",
                    "95": "bar",
                    "96": "bar",
                    "97": "bar",
                    "98": "bar",
                    "99": "bar",
                    "100": "bar",
                    "101": "bar",
                    "102": "bar",
                    "103": "bar",
                    "104": "bar",
                    "105": "bar",
                    "106": "bar",
                    "107": "bar",
                    "108": "bar",
                    "109": "bar",
                    "110": "bar",
                    "111": "bar",
                    "112": "bar",
                    "113": "bar",
                    "114": "bar",
                    "115": "bar",
                    "116": "bar",
                    "117": "bar",
                    "118": "bar",
                    "119": "bar",
                    "120": "bar",
                    "121": "bar",
                    "122": "bar",
                    "123": "bar",
                    "124": "bar",
                    "125": "bar",
                    "126": "bar",
                    "127": "bar",
                    "128": "bar",
                    "129": "bar",
                    "130": "bar",
                    "131": "bar",
                    "132": "bar",
                    "133": "bar",
                    "134": "bar",
                    "135": "bar",
                    "136": "bar",
                    "137": "bar",
                    "138": "bar",
                    "139": "bar",
                },
                "type": "custom",
                "include_sample_schema": True,
            },
            testing_criteria=[
                {
                    "input": [
                        {
                            "content": "content",
                            "role": "role",
                        }
                    ],
                    "labels": ["string"],
                    "model": "model",
                    "name": "name",
                    "passing_labels": ["string"],
                    "type": "label_model",
                }
            ],
            metadata={"foo": "string"},
            name="name",
            share_with_openai=True,
        )
        assert_matches_type(EvalCreateResponse, eval, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: OpenAI) -> None:
        response = client.evals.with_raw_response.create(
            data_source_config={
                "item_schema": {
                    "0": "bar",
                    "1": "bar",
                    "2": "bar",
                    "3": "bar",
                    "4": "bar",
                    "5": "bar",
                    "6": "bar",
                    "7": "bar",
                    "8": "bar",
                    "9": "bar",
                    "10": "bar",
                    "11": "bar",
                    "12": "bar",
                    "13": "bar",
                    "14": "bar",
                    "15": "bar",
                    "16": "bar",
                    "17": "bar",
                    "18": "bar",
                    "19": "bar",
                    "20": "bar",
                    "21": "bar",
                    "22": "bar",
                    "23": "bar",
                    "24": "bar",
                    "25": "bar",
                    "26": "bar",
                    "27": "bar",
                    "28": "bar",
                    "29": "bar",
                    "30": "bar",
                    "31": "bar",
                    "32": "bar",
                    "33": "bar",
                    "34": "bar",
                    "35": "bar",
                    "36": "bar",
                    "37": "bar",
                    "38": "bar",
                    "39": "bar",
                    "40": "bar",
                    "41": "bar",
                    "42": "bar",
                    "43": "bar",
                    "44": "bar",
                    "45": "bar",
                    "46": "bar",
                    "47": "bar",
                    "48": "bar",
                    "49": "bar",
                    "50": "bar",
                    "51": "bar",
                    "52": "bar",
                    "53": "bar",
                    "54": "bar",
                    "55": "bar",
                    "56": "bar",
                    "57": "bar",
                    "58": "bar",
                    "59": "bar",
                    "60": "bar",
                    "61": "bar",
                    "62": "bar",
                    "63": "bar",
                    "64": "bar",
                    "65": "bar",
                    "66": "bar",
                    "67": "bar",
                    "68": "bar",
                    "69": "bar",
                    "70": "bar",
                    "71": "bar",
                    "72": "bar",
                    "73": "bar",
                    "74": "bar",
                    "75": "bar",
                    "76": "bar",
                    "77": "bar",
                    "78": "bar",
                    "79": "bar",
                    "80": "bar",
                    "81": "bar",
                    "82": "bar",
                    "83": "bar",
                    "84": "bar",
                    "85": "bar",
                    "86": "bar",
                    "87": "bar",
                    "88": "bar",
                    "89": "bar",
                    "90": "bar",
                    "91": "bar",
                    "92": "bar",
                    "93": "bar",
                    "94": "bar",
                    "95": "bar",
                    "96": "bar",
                    "97": "bar",
                    "98": "bar",
                    "99": "bar",
                    "100": "bar",
                    "101": "bar",
                    "102": "bar",
                    "103": "bar",
                    "104": "bar",
                    "105": "bar",
                    "106": "bar",
                    "107": "bar",
                    "108": "bar",
                    "109": "bar",
                    "110": "bar",
                    "111": "bar",
                    "112": "bar",
                    "113": "bar",
                    "114": "bar",
                    "115": "bar",
                    "116": "bar",
                    "117": "bar",
                    "118": "bar",
                    "119": "bar",
                    "120": "bar",
                    "121": "bar",
                    "122": "bar",
                    "123": "bar",
                    "124": "bar",
                    "125": "bar",
                    "126": "bar",
                    "127": "bar",
                    "128": "bar",
                    "129": "bar",
                    "130": "bar",
                    "131": "bar",
                    "132": "bar",
                    "133": "bar",
                    "134": "bar",
                    "135": "bar",
                    "136": "bar",
                    "137": "bar",
                    "138": "bar",
                    "139": "bar",
                },
                "type": "custom",
            },
            testing_criteria=[
                {
                    "input": [
                        {
                            "content": "content",
                            "role": "role",
                        }
                    ],
                    "labels": ["string"],
                    "model": "model",
                    "name": "name",
                    "passing_labels": ["string"],
                    "type": "label_model",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        eval = response.parse()
        assert_matches_type(EvalCreateResponse, eval, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: OpenAI) -> None:
        with client.evals.with_streaming_response.create(
            data_source_config={
                "item_schema": {
                    "0": "bar",
                    "1": "bar",
                    "2": "bar",
                    "3": "bar",
                    "4": "bar",
                    "5": "bar",
                    "6": "bar",
                    "7": "bar",
                    "8": "bar",
                    "9": "bar",
                    "10": "bar",
                    "11": "bar",
                    "12": "bar",
                    "13": "bar",
                    "14": "bar",
                    "15": "bar",
                    "16": "bar",
                    "17": "bar",
                    "18": "bar",
                    "19": "bar",
                    "20": "bar",
                    "21": "bar",
                    "22": "bar",
                    "23": "bar",
                    "24": "bar",
                    "25": "bar",
                    "26": "bar",
                    "27": "bar",
                    "28": "bar",
                    "29": "bar",
                    "30": "bar",
                    "31": "bar",
                    "32": "bar",
                    "33": "bar",
                    "34": "bar",
                    "35": "bar",
                    "36": "bar",
                    "37": "bar",
                    "38": "bar",
                    "39": "bar",
                    "40": "bar",
                    "41": "bar",
                    "42": "bar",
                    "43": "bar",
                    "44": "bar",
                    "45": "bar",
                    "46": "bar",
                    "47": "bar",
                    "48": "bar",
                    "49": "bar",
                    "50": "bar",
                    "51": "bar",
                    "52": "bar",
                    "53": "bar",
                    "54": "bar",
                    "55": "bar",
                    "56": "bar",
                    "57": "bar",
                    "58": "bar",
                    "59": "bar",
                    "60": "bar",
                    "61": "bar",
                    "62": "bar",
                    "63": "bar",
                    "64": "bar",
                    "65": "bar",
                    "66": "bar",
                    "67": "bar",
                    "68": "bar",
                    "69": "bar",
                    "70": "bar",
                    "71": "bar",
                    "72": "bar",
                    "73": "bar",
                    "74": "bar",
                    "75": "bar",
                    "76": "bar",
                    "77": "bar",
                    "78": "bar",
                    "79": "bar",
                    "80": "bar",
                    "81": "bar",
                    "82": "bar",
                    "83": "bar",
                    "84": "bar",
                    "85": "bar",
                    "86": "bar",
                    "87": "bar",
                    "88": "bar",
                    "89": "bar",
                    "90": "bar",
                    "91": "bar",
                    "92": "bar",
                    "93": "bar",
                    "94": "bar",
                    "95": "bar",
                    "96": "bar",
                    "97": "bar",
                    "98": "bar",
                    "99": "bar",
                    "100": "bar",
                    "101": "bar",
                    "102": "bar",
                    "103": "bar",
                    "104": "bar",
                    "105": "bar",
                    "106": "bar",
                    "107": "bar",
                    "108": "bar",
                    "109": "bar",
                    "110": "bar",
                    "111": "bar",
                    "112": "bar",
                    "113": "bar",
                    "114": "bar",
                    "115": "bar",
                    "116": "bar",
                    "117": "bar",
                    "118": "bar",
                    "119": "bar",
                    "120": "bar",
                    "121": "bar",
                    "122": "bar",
                    "123": "bar",
                    "124": "bar",
                    "125": "bar",
                    "126": "bar",
                    "127": "bar",
                    "128": "bar",
                    "129": "bar",
                    "130": "bar",
                    "131": "bar",
                    "132": "bar",
                    "133": "bar",
                    "134": "bar",
                    "135": "bar",
                    "136": "bar",
                    "137": "bar",
                    "138": "bar",
                    "139": "bar",
                },
                "type": "custom",
            },
            testing_criteria=[
                {
                    "input": [
                        {
                            "content": "content",
                            "role": "role",
                        }
                    ],
                    "labels": ["string"],
                    "model": "model",
                    "name": "name",
                    "passing_labels": ["string"],
                    "type": "label_model",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            eval = response.parse()
            assert_matches_type(EvalCreateResponse, eval, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_retrieve(self, client: OpenAI) -> None:
        eval = client.evals.retrieve(
            "eval_id",
        )
        assert_matches_type(EvalRetrieveResponse, eval, path=["response"])

    @parametrize
    def test_raw_response_retrieve(self, client: OpenAI) -> None:
        response = client.evals.with_raw_response.retrieve(
            "eval_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        eval = response.parse()
        assert_matches_type(EvalRetrieveResponse, eval, path=["response"])

    @parametrize
    def test_streaming_response_retrieve(self, client: OpenAI) -> None:
        with client.evals.with_streaming_response.retrieve(
            "eval_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            eval = response.parse()
            assert_matches_type(EvalRetrieveResponse, eval, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_retrieve(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `eval_id` but received ''"):
            client.evals.with_raw_response.retrieve(
                "",
            )

    @parametrize
    def test_method_update(self, client: OpenAI) -> None:
        eval = client.evals.update(
            eval_id="eval_id",
        )
        assert_matches_type(EvalUpdateResponse, eval, path=["response"])

    @parametrize
    def test_method_update_with_all_params(self, client: OpenAI) -> None:
        eval = client.evals.update(
            eval_id="eval_id",
            metadata={"foo": "string"},
            name="name",
        )
        assert_matches_type(EvalUpdateResponse, eval, path=["response"])

    @parametrize
    def test_raw_response_update(self, client: OpenAI) -> None:
        response = client.evals.with_raw_response.update(
            eval_id="eval_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        eval = response.parse()
        assert_matches_type(EvalUpdateResponse, eval, path=["response"])

    @parametrize
    def test_streaming_response_update(self, client: OpenAI) -> None:
        with client.evals.with_streaming_response.update(
            eval_id="eval_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            eval = response.parse()
            assert_matches_type(EvalUpdateResponse, eval, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_update(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `eval_id` but received ''"):
            client.evals.with_raw_response.update(
                eval_id="",
            )

    @parametrize
    def test_method_list(self, client: OpenAI) -> None:
        eval = client.evals.list()
        assert_matches_type(SyncCursorPage[EvalListResponse], eval, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: OpenAI) -> None:
        eval = client.evals.list(
            after="after",
            limit=0,
            order="asc",
            order_by="created_at",
        )
        assert_matches_type(SyncCursorPage[EvalListResponse], eval, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: OpenAI) -> None:
        response = client.evals.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        eval = response.parse()
        assert_matches_type(SyncCursorPage[EvalListResponse], eval, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: OpenAI) -> None:
        with client.evals.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            eval = response.parse()
            assert_matches_type(SyncCursorPage[EvalListResponse], eval, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: OpenAI) -> None:
        eval = client.evals.delete(
            "eval_id",
        )
        assert_matches_type(EvalDeleteResponse, eval, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: OpenAI) -> None:
        response = client.evals.with_raw_response.delete(
            "eval_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        eval = response.parse()
        assert_matches_type(EvalDeleteResponse, eval, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: OpenAI) -> None:
        with client.evals.with_streaming_response.delete(
            "eval_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            eval = response.parse()
            assert_matches_type(EvalDeleteResponse, eval, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_delete(self, client: OpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `eval_id` but received ''"):
            client.evals.with_raw_response.delete(
                "",
            )


class TestAsyncEvals:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncOpenAI) -> None:
        eval = await async_client.evals.create(
            data_source_config={
                "item_schema": {
                    "0": "bar",
                    "1": "bar",
                    "2": "bar",
                    "3": "bar",
                    "4": "bar",
                    "5": "bar",
                    "6": "bar",
                    "7": "bar",
                    "8": "bar",
                    "9": "bar",
                    "10": "bar",
                    "11": "bar",
                    "12": "bar",
                    "13": "bar",
                    "14": "bar",
                    "15": "bar",
                    "16": "bar",
                    "17": "bar",
                    "18": "bar",
                    "19": "bar",
                    "20": "bar",
                    "21": "bar",
                    "22": "bar",
                    "23": "bar",
                    "24": "bar",
                    "25": "bar",
                    "26": "bar",
                    "27": "bar",
                    "28": "bar",
                    "29": "bar",
                    "30": "bar",
                    "31": "bar",
                    "32": "bar",
                    "33": "bar",
                    "34": "bar",
                    "35": "bar",
                    "36": "bar",
                    "37": "bar",
                    "38": "bar",
                    "39": "bar",
                    "40": "bar",
                    "41": "bar",
                    "42": "bar",
                    "43": "bar",
                    "44": "bar",
                    "45": "bar",
                    "46": "bar",
                    "47": "bar",
                    "48": "bar",
                    "49": "bar",
                    "50": "bar",
                    "51": "bar",
                    "52": "bar",
                    "53": "bar",
                    "54": "bar",
                    "55": "bar",
                    "56": "bar",
                    "57": "bar",
                    "58": "bar",
                    "59": "bar",
                    "60": "bar",
                    "61": "bar",
                    "62": "bar",
                    "63": "bar",
                    "64": "bar",
                    "65": "bar",
                    "66": "bar",
                    "67": "bar",
                    "68": "bar",
                    "69": "bar",
                    "70": "bar",
                    "71": "bar",
                    "72": "bar",
                    "73": "bar",
                    "74": "bar",
                    "75": "bar",
                    "76": "bar",
                    "77": "bar",
                    "78": "bar",
                    "79": "bar",
                    "80": "bar",
                    "81": "bar",
                    "82": "bar",
                    "83": "bar",
                    "84": "bar",
                    "85": "bar",
                    "86": "bar",
                    "87": "bar",
                    "88": "bar",
                    "89": "bar",
                    "90": "bar",
                    "91": "bar",
                    "92": "bar",
                    "93": "bar",
                    "94": "bar",
                    "95": "bar",
                    "96": "bar",
                    "97": "bar",
                    "98": "bar",
                    "99": "bar",
                    "100": "bar",
                    "101": "bar",
                    "102": "bar",
                    "103": "bar",
                    "104": "bar",
                    "105": "bar",
                    "106": "bar",
                    "107": "bar",
                    "108": "bar",
                    "109": "bar",
                    "110": "bar",
                    "111": "bar",
                    "112": "bar",
                    "113": "bar",
                    "114": "bar",
                    "115": "bar",
                    "116": "bar",
                    "117": "bar",
                    "118": "bar",
                    "119": "bar",
                    "120": "bar",
                    "121": "bar",
                    "122": "bar",
                    "123": "bar",
                    "124": "bar",
                    "125": "bar",
                    "126": "bar",
                    "127": "bar",
                    "128": "bar",
                    "129": "bar",
                    "130": "bar",
                    "131": "bar",
                    "132": "bar",
                    "133": "bar",
                    "134": "bar",
                    "135": "bar",
                    "136": "bar",
                    "137": "bar",
                    "138": "bar",
                    "139": "bar",
                },
                "type": "custom",
            },
            testing_criteria=[
                {
                    "input": [
                        {
                            "content": "content",
                            "role": "role",
                        }
                    ],
                    "labels": ["string"],
                    "model": "model",
                    "name": "name",
                    "passing_labels": ["string"],
                    "type": "label_model",
                }
            ],
        )
        assert_matches_type(EvalCreateResponse, eval, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncOpenAI) -> None:
        eval = await async_client.evals.create(
            data_source_config={
                "item_schema": {
                    "0": "bar",
                    "1": "bar",
                    "2": "bar",
                    "3": "bar",
                    "4": "bar",
                    "5": "bar",
                    "6": "bar",
                    "7": "bar",
                    "8": "bar",
                    "9": "bar",
                    "10": "bar",
                    "11": "bar",
                    "12": "bar",
                    "13": "bar",
                    "14": "bar",
                    "15": "bar",
                    "16": "bar",
                    "17": "bar",
                    "18": "bar",
                    "19": "bar",
                    "20": "bar",
                    "21": "bar",
                    "22": "bar",
                    "23": "bar",
                    "24": "bar",
                    "25": "bar",
                    "26": "bar",
                    "27": "bar",
                    "28": "bar",
                    "29": "bar",
                    "30": "bar",
                    "31": "bar",
                    "32": "bar",
                    "33": "bar",
                    "34": "bar",
                    "35": "bar",
                    "36": "bar",
                    "37": "bar",
                    "38": "bar",
                    "39": "bar",
                    "40": "bar",
                    "41": "bar",
                    "42": "bar",
                    "43": "bar",
                    "44": "bar",
                    "45": "bar",
                    "46": "bar",
                    "47": "bar",
                    "48": "bar",
                    "49": "bar",
                    "50": "bar",
                    "51": "bar",
                    "52": "bar",
                    "53": "bar",
                    "54": "bar",
                    "55": "bar",
                    "56": "bar",
                    "57": "bar",
                    "58": "bar",
                    "59": "bar",
                    "60": "bar",
                    "61": "bar",
                    "62": "bar",
                    "63": "bar",
                    "64": "bar",
                    "65": "bar",
                    "66": "bar",
                    "67": "bar",
                    "68": "bar",
                    "69": "bar",
                    "70": "bar",
                    "71": "bar",
                    "72": "bar",
                    "73": "bar",
                    "74": "bar",
                    "75": "bar",
                    "76": "bar",
                    "77": "bar",
                    "78": "bar",
                    "79": "bar",
                    "80": "bar",
                    "81": "bar",
                    "82": "bar",
                    "83": "bar",
                    "84": "bar",
                    "85": "bar",
                    "86": "bar",
                    "87": "bar",
                    "88": "bar",
                    "89": "bar",
                    "90": "bar",
                    "91": "bar",
                    "92": "bar",
                    "93": "bar",
                    "94": "bar",
                    "95": "bar",
                    "96": "bar",
                    "97": "bar",
                    "98": "bar",
                    "99": "bar",
                    "100": "bar",
                    "101": "bar",
                    "102": "bar",
                    "103": "bar",
                    "104": "bar",
                    "105": "bar",
                    "106": "bar",
                    "107": "bar",
                    "108": "bar",
                    "109": "bar",
                    "110": "bar",
                    "111": "bar",
                    "112": "bar",
                    "113": "bar",
                    "114": "bar",
                    "115": "bar",
                    "116": "bar",
                    "117": "bar",
                    "118": "bar",
                    "119": "bar",
                    "120": "bar",
                    "121": "bar",
                    "122": "bar",
                    "123": "bar",
                    "124": "bar",
                    "125": "bar",
                    "126": "bar",
                    "127": "bar",
                    "128": "bar",
                    "129": "bar",
                    "130": "bar",
                    "131": "bar",
                    "132": "bar",
                    "133": "bar",
                    "134": "bar",
                    "135": "bar",
                    "136": "bar",
                    "137": "bar",
                    "138": "bar",
                    "139": "bar",
                },
                "type": "custom",
                "include_sample_schema": True,
            },
            testing_criteria=[
                {
                    "input": [
                        {
                            "content": "content",
                            "role": "role",
                        }
                    ],
                    "labels": ["string"],
                    "model": "model",
                    "name": "name",
                    "passing_labels": ["string"],
                    "type": "label_model",
                }
            ],
            metadata={"foo": "string"},
            name="name",
            share_with_openai=True,
        )
        assert_matches_type(EvalCreateResponse, eval, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.evals.with_raw_response.create(
            data_source_config={
                "item_schema": {
                    "0": "bar",
                    "1": "bar",
                    "2": "bar",
                    "3": "bar",
                    "4": "bar",
                    "5": "bar",
                    "6": "bar",
                    "7": "bar",
                    "8": "bar",
                    "9": "bar",
                    "10": "bar",
                    "11": "bar",
                    "12": "bar",
                    "13": "bar",
                    "14": "bar",
                    "15": "bar",
                    "16": "bar",
                    "17": "bar",
                    "18": "bar",
                    "19": "bar",
                    "20": "bar",
                    "21": "bar",
                    "22": "bar",
                    "23": "bar",
                    "24": "bar",
                    "25": "bar",
                    "26": "bar",
                    "27": "bar",
                    "28": "bar",
                    "29": "bar",
                    "30": "bar",
                    "31": "bar",
                    "32": "bar",
                    "33": "bar",
                    "34": "bar",
                    "35": "bar",
                    "36": "bar",
                    "37": "bar",
                    "38": "bar",
                    "39": "bar",
                    "40": "bar",
                    "41": "bar",
                    "42": "bar",
                    "43": "bar",
                    "44": "bar",
                    "45": "bar",
                    "46": "bar",
                    "47": "bar",
                    "48": "bar",
                    "49": "bar",
                    "50": "bar",
                    "51": "bar",
                    "52": "bar",
                    "53": "bar",
                    "54": "bar",
                    "55": "bar",
                    "56": "bar",
                    "57": "bar",
                    "58": "bar",
                    "59": "bar",
                    "60": "bar",
                    "61": "bar",
                    "62": "bar",
                    "63": "bar",
                    "64": "bar",
                    "65": "bar",
                    "66": "bar",
                    "67": "bar",
                    "68": "bar",
                    "69": "bar",
                    "70": "bar",
                    "71": "bar",
                    "72": "bar",
                    "73": "bar",
                    "74": "bar",
                    "75": "bar",
                    "76": "bar",
                    "77": "bar",
                    "78": "bar",
                    "79": "bar",
                    "80": "bar",
                    "81": "bar",
                    "82": "bar",
                    "83": "bar",
                    "84": "bar",
                    "85": "bar",
                    "86": "bar",
                    "87": "bar",
                    "88": "bar",
                    "89": "bar",
                    "90": "bar",
                    "91": "bar",
                    "92": "bar",
                    "93": "bar",
                    "94": "bar",
                    "95": "bar",
                    "96": "bar",
                    "97": "bar",
                    "98": "bar",
                    "99": "bar",
                    "100": "bar",
                    "101": "bar",
                    "102": "bar",
                    "103": "bar",
                    "104": "bar",
                    "105": "bar",
                    "106": "bar",
                    "107": "bar",
                    "108": "bar",
                    "109": "bar",
                    "110": "bar",
                    "111": "bar",
                    "112": "bar",
                    "113": "bar",
                    "114": "bar",
                    "115": "bar",
                    "116": "bar",
                    "117": "bar",
                    "118": "bar",
                    "119": "bar",
                    "120": "bar",
                    "121": "bar",
                    "122": "bar",
                    "123": "bar",
                    "124": "bar",
                    "125": "bar",
                    "126": "bar",
                    "127": "bar",
                    "128": "bar",
                    "129": "bar",
                    "130": "bar",
                    "131": "bar",
                    "132": "bar",
                    "133": "bar",
                    "134": "bar",
                    "135": "bar",
                    "136": "bar",
                    "137": "bar",
                    "138": "bar",
                    "139": "bar",
                },
                "type": "custom",
            },
            testing_criteria=[
                {
                    "input": [
                        {
                            "content": "content",
                            "role": "role",
                        }
                    ],
                    "labels": ["string"],
                    "model": "model",
                    "name": "name",
                    "passing_labels": ["string"],
                    "type": "label_model",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        eval = response.parse()
        assert_matches_type(EvalCreateResponse, eval, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncOpenAI) -> None:
        async with async_client.evals.with_streaming_response.create(
            data_source_config={
                "item_schema": {
                    "0": "bar",
                    "1": "bar",
                    "2": "bar",
                    "3": "bar",
                    "4": "bar",
                    "5": "bar",
                    "6": "bar",
                    "7": "bar",
                    "8": "bar",
                    "9": "bar",
                    "10": "bar",
                    "11": "bar",
                    "12": "bar",
                    "13": "bar",
                    "14": "bar",
                    "15": "bar",
                    "16": "bar",
                    "17": "bar",
                    "18": "bar",
                    "19": "bar",
                    "20": "bar",
                    "21": "bar",
                    "22": "bar",
                    "23": "bar",
                    "24": "bar",
                    "25": "bar",
                    "26": "bar",
                    "27": "bar",
                    "28": "bar",
                    "29": "bar",
                    "30": "bar",
                    "31": "bar",
                    "32": "bar",
                    "33": "bar",
                    "34": "bar",
                    "35": "bar",
                    "36": "bar",
                    "37": "bar",
                    "38": "bar",
                    "39": "bar",
                    "40": "bar",
                    "41": "bar",
                    "42": "bar",
                    "43": "bar",
                    "44": "bar",
                    "45": "bar",
                    "46": "bar",
                    "47": "bar",
                    "48": "bar",
                    "49": "bar",
                    "50": "bar",
                    "51": "bar",
                    "52": "bar",
                    "53": "bar",
                    "54": "bar",
                    "55": "bar",
                    "56": "bar",
                    "57": "bar",
                    "58": "bar",
                    "59": "bar",
                    "60": "bar",
                    "61": "bar",
                    "62": "bar",
                    "63": "bar",
                    "64": "bar",
                    "65": "bar",
                    "66": "bar",
                    "67": "bar",
                    "68": "bar",
                    "69": "bar",
                    "70": "bar",
                    "71": "bar",
                    "72": "bar",
                    "73": "bar",
                    "74": "bar",
                    "75": "bar",
                    "76": "bar",
                    "77": "bar",
                    "78": "bar",
                    "79": "bar",
                    "80": "bar",
                    "81": "bar",
                    "82": "bar",
                    "83": "bar",
                    "84": "bar",
                    "85": "bar",
                    "86": "bar",
                    "87": "bar",
                    "88": "bar",
                    "89": "bar",
                    "90": "bar",
                    "91": "bar",
                    "92": "bar",
                    "93": "bar",
                    "94": "bar",
                    "95": "bar",
                    "96": "bar",
                    "97": "bar",
                    "98": "bar",
                    "99": "bar",
                    "100": "bar",
                    "101": "bar",
                    "102": "bar",
                    "103": "bar",
                    "104": "bar",
                    "105": "bar",
                    "106": "bar",
                    "107": "bar",
                    "108": "bar",
                    "109": "bar",
                    "110": "bar",
                    "111": "bar",
                    "112": "bar",
                    "113": "bar",
                    "114": "bar",
                    "115": "bar",
                    "116": "bar",
                    "117": "bar",
                    "118": "bar",
                    "119": "bar",
                    "120": "bar",
                    "121": "bar",
                    "122": "bar",
                    "123": "bar",
                    "124": "bar",
                    "125": "bar",
                    "126": "bar",
                    "127": "bar",
                    "128": "bar",
                    "129": "bar",
                    "130": "bar",
                    "131": "bar",
                    "132": "bar",
                    "133": "bar",
                    "134": "bar",
                    "135": "bar",
                    "136": "bar",
                    "137": "bar",
                    "138": "bar",
                    "139": "bar",
                },
                "type": "custom",
            },
            testing_criteria=[
                {
                    "input": [
                        {
                            "content": "content",
                            "role": "role",
                        }
                    ],
                    "labels": ["string"],
                    "model": "model",
                    "name": "name",
                    "passing_labels": ["string"],
                    "type": "label_model",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            eval = await response.parse()
            assert_matches_type(EvalCreateResponse, eval, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_retrieve(self, async_client: AsyncOpenAI) -> None:
        eval = await async_client.evals.retrieve(
            "eval_id",
        )
        assert_matches_type(EvalRetrieveResponse, eval, path=["response"])

    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.evals.with_raw_response.retrieve(
            "eval_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        eval = response.parse()
        assert_matches_type(EvalRetrieveResponse, eval, path=["response"])

    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncOpenAI) -> None:
        async with async_client.evals.with_streaming_response.retrieve(
            "eval_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            eval = await response.parse()
            assert_matches_type(EvalRetrieveResponse, eval, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `eval_id` but received ''"):
            await async_client.evals.with_raw_response.retrieve(
                "",
            )

    @parametrize
    async def test_method_update(self, async_client: AsyncOpenAI) -> None:
        eval = await async_client.evals.update(
            eval_id="eval_id",
        )
        assert_matches_type(EvalUpdateResponse, eval, path=["response"])

    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncOpenAI) -> None:
        eval = await async_client.evals.update(
            eval_id="eval_id",
            metadata={"foo": "string"},
            name="name",
        )
        assert_matches_type(EvalUpdateResponse, eval, path=["response"])

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.evals.with_raw_response.update(
            eval_id="eval_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        eval = response.parse()
        assert_matches_type(EvalUpdateResponse, eval, path=["response"])

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncOpenAI) -> None:
        async with async_client.evals.with_streaming_response.update(
            eval_id="eval_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            eval = await response.parse()
            assert_matches_type(EvalUpdateResponse, eval, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_update(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `eval_id` but received ''"):
            await async_client.evals.with_raw_response.update(
                eval_id="",
            )

    @parametrize
    async def test_method_list(self, async_client: AsyncOpenAI) -> None:
        eval = await async_client.evals.list()
        assert_matches_type(AsyncCursorPage[EvalListResponse], eval, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncOpenAI) -> None:
        eval = await async_client.evals.list(
            after="after",
            limit=0,
            order="asc",
            order_by="created_at",
        )
        assert_matches_type(AsyncCursorPage[EvalListResponse], eval, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.evals.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        eval = response.parse()
        assert_matches_type(AsyncCursorPage[EvalListResponse], eval, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncOpenAI) -> None:
        async with async_client.evals.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            eval = await response.parse()
            assert_matches_type(AsyncCursorPage[EvalListResponse], eval, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, async_client: AsyncOpenAI) -> None:
        eval = await async_client.evals.delete(
            "eval_id",
        )
        assert_matches_type(EvalDeleteResponse, eval, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncOpenAI) -> None:
        response = await async_client.evals.with_raw_response.delete(
            "eval_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        eval = response.parse()
        assert_matches_type(EvalDeleteResponse, eval, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncOpenAI) -> None:
        async with async_client.evals.with_streaming_response.delete(
            "eval_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            eval = await response.parse()
            assert_matches_type(EvalDeleteResponse, eval, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_delete(self, async_client: AsyncOpenAI) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `eval_id` but received ''"):
            await async_client.evals.with_raw_response.delete(
                "",
            )
