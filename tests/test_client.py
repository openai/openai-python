# File generated from our OpenAPI spec by Stainless.

from __future__ import annotations

import os
import json
import asyncio
import inspect
from typing import Any, Dict, Union, cast
from unittest import mock

import httpx
import pytest
from respx import MockRouter
from pydantic import ValidationError

from openai import OpenAI, AsyncOpenAI, APIResponseValidationError
from openai._client import OpenAI, AsyncOpenAI
from openai._models import BaseModel, FinalRequestOptions
from openai._streaming import Stream, AsyncStream
from openai._exceptions import APIResponseValidationError
from openai._base_client import (
    DEFAULT_TIMEOUT,
    HTTPX_DEFAULT_TIMEOUT,
    BaseClient,
    make_request_options,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")
api_key = "My API Key"


def _get_params(client: BaseClient[Any, Any]) -> dict[str, str]:
    request = client._build_request(FinalRequestOptions(method="get", url="/foo"))
    url = httpx.URL(request.url)
    return dict(url.params)


class TestOpenAI:
    client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)

    @pytest.mark.respx(base_url=base_url)
    def test_raw_response(self, respx_mock: MockRouter) -> None:
        respx_mock.post("/foo").mock(return_value=httpx.Response(200, json='{"foo": "bar"}'))

        response = self.client.post("/foo", cast_to=httpx.Response)
        assert response.status_code == 200
        assert isinstance(response, httpx.Response)
        assert response.json() == '{"foo": "bar"}'

    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_for_binary(self, respx_mock: MockRouter) -> None:
        respx_mock.post("/foo").mock(
            return_value=httpx.Response(200, headers={"Content-Type": "application/binary"}, content='{"foo": "bar"}')
        )

        response = self.client.post("/foo", cast_to=httpx.Response)
        assert response.status_code == 200
        assert isinstance(response, httpx.Response)
        assert response.json() == '{"foo": "bar"}'

    def test_copy(self) -> None:
        copied = self.client.copy()
        assert id(copied) != id(self.client)

        copied = self.client.copy(api_key="another My API Key")
        assert copied.api_key == "another My API Key"
        assert self.client.api_key == "My API Key"

    def test_copy_default_options(self) -> None:
        # options that have a default are overridden correctly
        copied = self.client.copy(max_retries=7)
        assert copied.max_retries == 7
        assert self.client.max_retries == 2

        copied2 = copied.copy(max_retries=6)
        assert copied2.max_retries == 6
        assert copied.max_retries == 7

        # timeout
        assert isinstance(self.client.timeout, httpx.Timeout)
        copied = self.client.copy(timeout=None)
        assert copied.timeout is None
        assert isinstance(self.client.timeout, httpx.Timeout)

    def test_copy_default_headers(self) -> None:
        client = OpenAI(
            base_url=base_url, api_key=api_key, _strict_response_validation=True, default_headers={"X-Foo": "bar"}
        )
        assert client.default_headers["X-Foo"] == "bar"

        # does not override the already given value when not specified
        copied = client.copy()
        assert copied.default_headers["X-Foo"] == "bar"

        # merges already given headers
        copied = client.copy(default_headers={"X-Bar": "stainless"})
        assert copied.default_headers["X-Foo"] == "bar"
        assert copied.default_headers["X-Bar"] == "stainless"

        # uses new values for any already given headers
        copied = client.copy(default_headers={"X-Foo": "stainless"})
        assert copied.default_headers["X-Foo"] == "stainless"

        # set_default_headers

        # completely overrides already set values
        copied = client.copy(set_default_headers={})
        assert copied.default_headers.get("X-Foo") is None

        copied = client.copy(set_default_headers={"X-Bar": "Robert"})
        assert copied.default_headers["X-Bar"] == "Robert"

        with pytest.raises(
            ValueError,
            match="`default_headers` and `set_default_headers` arguments are mutually exclusive",
        ):
            client.copy(set_default_headers={}, default_headers={"X-Foo": "Bar"})

    def test_copy_default_query(self) -> None:
        client = OpenAI(
            base_url=base_url, api_key=api_key, _strict_response_validation=True, default_query={"foo": "bar"}
        )
        assert _get_params(client)["foo"] == "bar"

        # does not override the already given value when not specified
        copied = client.copy()
        assert _get_params(copied)["foo"] == "bar"

        # merges already given params
        copied = client.copy(default_query={"bar": "stainless"})
        params = _get_params(copied)
        assert params["foo"] == "bar"
        assert params["bar"] == "stainless"

        # uses new values for any already given headers
        copied = client.copy(default_query={"foo": "stainless"})
        assert _get_params(copied)["foo"] == "stainless"

        # set_default_query

        # completely overrides already set values
        copied = client.copy(set_default_query={})
        assert _get_params(copied) == {}

        copied = client.copy(set_default_query={"bar": "Robert"})
        assert _get_params(copied)["bar"] == "Robert"

        with pytest.raises(
            ValueError,
            # TODO: update
            match="`default_query` and `set_default_query` arguments are mutually exclusive",
        ):
            client.copy(set_default_query={}, default_query={"foo": "Bar"})

    def test_copy_signature(self) -> None:
        # ensure the same parameters that can be passed to the client are defined in the `.copy()` method
        init_signature = inspect.signature(
            # mypy doesn't like that we access the `__init__` property.
            self.client.__init__,  # type: ignore[misc]
        )
        copy_signature = inspect.signature(self.client.copy)
        exclude_params = {"transport", "proxies", "_strict_response_validation"}

        for name in init_signature.parameters.keys():
            if name in exclude_params:
                continue

            copy_param = copy_signature.parameters.get(name)
            assert copy_param is not None, f"copy() signature is missing the {name} param"

    def test_request_timeout(self) -> None:
        request = self.client._build_request(FinalRequestOptions(method="get", url="/foo"))
        timeout = httpx.Timeout(**request.extensions["timeout"])  # type: ignore
        assert timeout == DEFAULT_TIMEOUT

        request = self.client._build_request(
            FinalRequestOptions(method="get", url="/foo", timeout=httpx.Timeout(100.0))
        )
        timeout = httpx.Timeout(**request.extensions["timeout"])  # type: ignore
        assert timeout == httpx.Timeout(100.0)

    def test_client_timeout_option(self) -> None:
        client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True, timeout=httpx.Timeout(0))

        request = client._build_request(FinalRequestOptions(method="get", url="/foo"))
        timeout = httpx.Timeout(**request.extensions["timeout"])  # type: ignore
        assert timeout == httpx.Timeout(0)

    def test_http_client_timeout_option(self) -> None:
        # custom timeout given to the httpx client should be used
        with httpx.Client(timeout=None) as http_client:
            client = OpenAI(
                base_url=base_url, api_key=api_key, _strict_response_validation=True, http_client=http_client
            )

            request = client._build_request(FinalRequestOptions(method="get", url="/foo"))
            timeout = httpx.Timeout(**request.extensions["timeout"])  # type: ignore
            assert timeout == httpx.Timeout(None)

        # no timeout given to the httpx client should not use the httpx default
        with httpx.Client() as http_client:
            client = OpenAI(
                base_url=base_url, api_key=api_key, _strict_response_validation=True, http_client=http_client
            )

            request = client._build_request(FinalRequestOptions(method="get", url="/foo"))
            timeout = httpx.Timeout(**request.extensions["timeout"])  # type: ignore
            assert timeout == DEFAULT_TIMEOUT

        # explicitly passing the default timeout currently results in it being ignored
        with httpx.Client(timeout=HTTPX_DEFAULT_TIMEOUT) as http_client:
            client = OpenAI(
                base_url=base_url, api_key=api_key, _strict_response_validation=True, http_client=http_client
            )

            request = client._build_request(FinalRequestOptions(method="get", url="/foo"))
            timeout = httpx.Timeout(**request.extensions["timeout"])  # type: ignore
            assert timeout == DEFAULT_TIMEOUT  # our default

    def test_default_headers_option(self) -> None:
        client = OpenAI(
            base_url=base_url, api_key=api_key, _strict_response_validation=True, default_headers={"X-Foo": "bar"}
        )
        request = client._build_request(FinalRequestOptions(method="get", url="/foo"))
        assert request.headers.get("x-foo") == "bar"
        assert request.headers.get("x-stainless-lang") == "python"

        client2 = OpenAI(
            base_url=base_url,
            api_key=api_key,
            _strict_response_validation=True,
            default_headers={
                "X-Foo": "stainless",
                "X-Stainless-Lang": "my-overriding-header",
            },
        )
        request = client2._build_request(FinalRequestOptions(method="get", url="/foo"))
        assert request.headers.get("x-foo") == "stainless"
        assert request.headers.get("x-stainless-lang") == "my-overriding-header"

    def test_validate_headers(self) -> None:
        client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
        request = client._build_request(FinalRequestOptions(method="get", url="/foo"))
        assert request.headers.get("Authorization") == f"Bearer {api_key}"

        with pytest.raises(Exception):
            client2 = OpenAI(base_url=base_url, api_key=None, _strict_response_validation=True)
            _ = client2

    def test_default_query_option(self) -> None:
        client = OpenAI(
            base_url=base_url, api_key=api_key, _strict_response_validation=True, default_query={"query_param": "bar"}
        )
        request = client._build_request(FinalRequestOptions(method="get", url="/foo"))
        url = httpx.URL(request.url)
        assert dict(url.params) == {"query_param": "bar"}

        request = client._build_request(
            FinalRequestOptions(
                method="get",
                url="/foo",
                params={"foo": "baz", "query_param": "overriden"},
            )
        )
        url = httpx.URL(request.url)
        assert dict(url.params) == {"foo": "baz", "query_param": "overriden"}

    def test_request_extra_json(self) -> None:
        request = self.client._build_request(
            FinalRequestOptions(
                method="post",
                url="/foo",
                json_data={"foo": "bar"},
                extra_json={"baz": False},
            ),
        )
        data = json.loads(request.content.decode("utf-8"))
        assert data == {"foo": "bar", "baz": False}

        request = self.client._build_request(
            FinalRequestOptions(
                method="post",
                url="/foo",
                extra_json={"baz": False},
            ),
        )
        data = json.loads(request.content.decode("utf-8"))
        assert data == {"baz": False}

        # `extra_json` takes priority over `json_data` when keys clash
        request = self.client._build_request(
            FinalRequestOptions(
                method="post",
                url="/foo",
                json_data={"foo": "bar", "baz": True},
                extra_json={"baz": None},
            ),
        )
        data = json.loads(request.content.decode("utf-8"))
        assert data == {"foo": "bar", "baz": None}

    def test_request_extra_headers(self) -> None:
        request = self.client._build_request(
            FinalRequestOptions(
                method="post",
                url="/foo",
                **make_request_options(extra_headers={"X-Foo": "Foo"}),
            ),
        )
        assert request.headers.get("X-Foo") == "Foo"

        # `extra_headers` takes priority over `default_headers` when keys clash
        request = self.client.with_options(default_headers={"X-Bar": "true"})._build_request(
            FinalRequestOptions(
                method="post",
                url="/foo",
                **make_request_options(
                    extra_headers={"X-Bar": "false"},
                ),
            ),
        )
        assert request.headers.get("X-Bar") == "false"

    def test_request_extra_query(self) -> None:
        request = self.client._build_request(
            FinalRequestOptions(
                method="post",
                url="/foo",
                **make_request_options(
                    extra_query={"my_query_param": "Foo"},
                ),
            ),
        )
        params = cast(Dict[str, str], dict(request.url.params))
        assert params == {"my_query_param": "Foo"}

        # if both `query` and `extra_query` are given, they are merged
        request = self.client._build_request(
            FinalRequestOptions(
                method="post",
                url="/foo",
                **make_request_options(
                    query={"bar": "1"},
                    extra_query={"foo": "2"},
                ),
            ),
        )
        params = cast(Dict[str, str], dict(request.url.params))
        assert params == {"bar": "1", "foo": "2"}

        # `extra_query` takes priority over `query` when keys clash
        request = self.client._build_request(
            FinalRequestOptions(
                method="post",
                url="/foo",
                **make_request_options(
                    query={"foo": "1"},
                    extra_query={"foo": "2"},
                ),
            ),
        )
        params = cast(Dict[str, str], dict(request.url.params))
        assert params == {"foo": "2"}

    @pytest.mark.respx(base_url=base_url)
    def test_basic_union_response(self, respx_mock: MockRouter) -> None:
        class Model1(BaseModel):
            name: str

        class Model2(BaseModel):
            foo: str

        respx_mock.get("/foo").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        response = self.client.get("/foo", cast_to=cast(Any, Union[Model1, Model2]))
        assert isinstance(response, Model2)
        assert response.foo == "bar"

    @pytest.mark.respx(base_url=base_url)
    def test_union_response_different_types(self, respx_mock: MockRouter) -> None:
        """Union of objects with the same field name using a different type"""

        class Model1(BaseModel):
            foo: int

        class Model2(BaseModel):
            foo: str

        respx_mock.get("/foo").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        response = self.client.get("/foo", cast_to=cast(Any, Union[Model1, Model2]))
        assert isinstance(response, Model2)
        assert response.foo == "bar"

        respx_mock.get("/foo").mock(return_value=httpx.Response(200, json={"foo": 1}))

        response = self.client.get("/foo", cast_to=cast(Any, Union[Model1, Model2]))
        assert isinstance(response, Model1)
        assert response.foo == 1

    @pytest.mark.parametrize(
        "client",
        [
            OpenAI(base_url="http://localhost:5000/custom/path/", api_key=api_key, _strict_response_validation=True),
            OpenAI(
                base_url="http://localhost:5000/custom/path/",
                api_key=api_key,
                _strict_response_validation=True,
                http_client=httpx.Client(),
            ),
        ],
        ids=["standard", "custom http client"],
    )
    def test_base_url_trailing_slash(self, client: OpenAI) -> None:
        request = client._build_request(
            FinalRequestOptions(
                method="post",
                url="/foo",
                json_data={"foo": "bar"},
            ),
        )
        assert request.url == "http://localhost:5000/custom/path/foo"

    @pytest.mark.parametrize(
        "client",
        [
            OpenAI(base_url="http://localhost:5000/custom/path/", api_key=api_key, _strict_response_validation=True),
            OpenAI(
                base_url="http://localhost:5000/custom/path/",
                api_key=api_key,
                _strict_response_validation=True,
                http_client=httpx.Client(),
            ),
        ],
        ids=["standard", "custom http client"],
    )
    def test_base_url_no_trailing_slash(self, client: OpenAI) -> None:
        request = client._build_request(
            FinalRequestOptions(
                method="post",
                url="/foo",
                json_data={"foo": "bar"},
            ),
        )
        assert request.url == "http://localhost:5000/custom/path/foo"

    @pytest.mark.parametrize(
        "client",
        [
            OpenAI(base_url="http://localhost:5000/custom/path/", api_key=api_key, _strict_response_validation=True),
            OpenAI(
                base_url="http://localhost:5000/custom/path/",
                api_key=api_key,
                _strict_response_validation=True,
                http_client=httpx.Client(),
            ),
        ],
        ids=["standard", "custom http client"],
    )
    def test_absolute_request_url(self, client: OpenAI) -> None:
        request = client._build_request(
            FinalRequestOptions(
                method="post",
                url="https://myapi.com/foo",
                json_data={"foo": "bar"},
            ),
        )
        assert request.url == "https://myapi.com/foo"

    def test_client_del(self) -> None:
        client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
        assert not client.is_closed()

        client.__del__()

        assert client.is_closed()

    def test_copied_client_does_not_close_http(self) -> None:
        client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
        assert not client.is_closed()

        copied = client.copy()
        assert copied is not client

        copied.__del__()

        assert not copied.is_closed()
        assert not client.is_closed()

    def test_client_context_manager(self) -> None:
        client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
        with client as c2:
            assert c2 is client
            assert not c2.is_closed()
            assert not client.is_closed()
        assert client.is_closed()

    @pytest.mark.respx(base_url=base_url)
    def test_client_response_validation_error(self, respx_mock: MockRouter) -> None:
        class Model(BaseModel):
            foo: str

        respx_mock.get("/foo").mock(return_value=httpx.Response(200, json={"foo": {"invalid": True}}))

        with pytest.raises(APIResponseValidationError) as exc:
            self.client.get("/foo", cast_to=Model)

        assert isinstance(exc.value.__cause__, ValidationError)

    @pytest.mark.respx(base_url=base_url)
    def test_default_stream_cls(self, respx_mock: MockRouter) -> None:
        class Model(BaseModel):
            name: str

        respx_mock.post("/foo").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        response = self.client.post("/foo", cast_to=Model, stream=True)
        assert isinstance(response, Stream)

    @pytest.mark.respx(base_url=base_url)
    def test_received_text_for_expected_json(self, respx_mock: MockRouter) -> None:
        class Model(BaseModel):
            name: str

        respx_mock.get("/foo").mock(return_value=httpx.Response(200, text="my-custom-format"))

        strict_client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)

        with pytest.raises(APIResponseValidationError):
            strict_client.get("/foo", cast_to=Model)

        client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)

        response = client.get("/foo", cast_to=Model)
        assert isinstance(response, str)  # type: ignore[unreachable]

    @pytest.mark.parametrize(
        "remaining_retries,retry_after,timeout",
        [
            [3, "20", 20],
            [3, "0", 0.5],
            [3, "-10", 0.5],
            [3, "60", 60],
            [3, "61", 0.5],
            [3, "Fri, 29 Sep 2023 16:26:57 GMT", 20],
            [3, "Fri, 29 Sep 2023 16:26:37 GMT", 0.5],
            [3, "Fri, 29 Sep 2023 16:26:27 GMT", 0.5],
            [3, "Fri, 29 Sep 2023 16:27:37 GMT", 60],
            [3, "Fri, 29 Sep 2023 16:27:38 GMT", 0.5],
            [3, "99999999999999999999999999999999999", 0.5],
            [3, "Zun, 29 Sep 2023 16:26:27 GMT", 0.5],
            [3, "", 0.5],
            [2, "", 0.5 * 2.0],
            [1, "", 0.5 * 4.0],
        ],
    )
    @mock.patch("time.time", mock.MagicMock(return_value=1696004797))
    def test_parse_retry_after_header(self, remaining_retries: int, retry_after: str, timeout: float) -> None:
        client = OpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)

        headers = httpx.Headers({"retry-after": retry_after})
        options = FinalRequestOptions(method="get", url="/foo", max_retries=3)
        calculated = client._calculate_retry_timeout(remaining_retries, options, headers)
        assert calculated == pytest.approx(timeout, 0.5 * 0.875)  # pyright: ignore[reportUnknownMemberType]


class TestAsyncOpenAI:
    client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)

    @pytest.mark.respx(base_url=base_url)
    @pytest.mark.asyncio
    async def test_raw_response(self, respx_mock: MockRouter) -> None:
        respx_mock.post("/foo").mock(return_value=httpx.Response(200, json='{"foo": "bar"}'))

        response = await self.client.post("/foo", cast_to=httpx.Response)
        assert response.status_code == 200
        assert isinstance(response, httpx.Response)
        assert response.json() == '{"foo": "bar"}'

    @pytest.mark.respx(base_url=base_url)
    @pytest.mark.asyncio
    async def test_raw_response_for_binary(self, respx_mock: MockRouter) -> None:
        respx_mock.post("/foo").mock(
            return_value=httpx.Response(200, headers={"Content-Type": "application/binary"}, content='{"foo": "bar"}')
        )

        response = await self.client.post("/foo", cast_to=httpx.Response)
        assert response.status_code == 200
        assert isinstance(response, httpx.Response)
        assert response.json() == '{"foo": "bar"}'

    def test_copy(self) -> None:
        copied = self.client.copy()
        assert id(copied) != id(self.client)

        copied = self.client.copy(api_key="another My API Key")
        assert copied.api_key == "another My API Key"
        assert self.client.api_key == "My API Key"

    def test_copy_default_options(self) -> None:
        # options that have a default are overridden correctly
        copied = self.client.copy(max_retries=7)
        assert copied.max_retries == 7
        assert self.client.max_retries == 2

        copied2 = copied.copy(max_retries=6)
        assert copied2.max_retries == 6
        assert copied.max_retries == 7

        # timeout
        assert isinstance(self.client.timeout, httpx.Timeout)
        copied = self.client.copy(timeout=None)
        assert copied.timeout is None
        assert isinstance(self.client.timeout, httpx.Timeout)

    def test_copy_default_headers(self) -> None:
        client = AsyncOpenAI(
            base_url=base_url, api_key=api_key, _strict_response_validation=True, default_headers={"X-Foo": "bar"}
        )
        assert client.default_headers["X-Foo"] == "bar"

        # does not override the already given value when not specified
        copied = client.copy()
        assert copied.default_headers["X-Foo"] == "bar"

        # merges already given headers
        copied = client.copy(default_headers={"X-Bar": "stainless"})
        assert copied.default_headers["X-Foo"] == "bar"
        assert copied.default_headers["X-Bar"] == "stainless"

        # uses new values for any already given headers
        copied = client.copy(default_headers={"X-Foo": "stainless"})
        assert copied.default_headers["X-Foo"] == "stainless"

        # set_default_headers

        # completely overrides already set values
        copied = client.copy(set_default_headers={})
        assert copied.default_headers.get("X-Foo") is None

        copied = client.copy(set_default_headers={"X-Bar": "Robert"})
        assert copied.default_headers["X-Bar"] == "Robert"

        with pytest.raises(
            ValueError,
            match="`default_headers` and `set_default_headers` arguments are mutually exclusive",
        ):
            client.copy(set_default_headers={}, default_headers={"X-Foo": "Bar"})

    def test_copy_default_query(self) -> None:
        client = AsyncOpenAI(
            base_url=base_url, api_key=api_key, _strict_response_validation=True, default_query={"foo": "bar"}
        )
        assert _get_params(client)["foo"] == "bar"

        # does not override the already given value when not specified
        copied = client.copy()
        assert _get_params(copied)["foo"] == "bar"

        # merges already given params
        copied = client.copy(default_query={"bar": "stainless"})
        params = _get_params(copied)
        assert params["foo"] == "bar"
        assert params["bar"] == "stainless"

        # uses new values for any already given headers
        copied = client.copy(default_query={"foo": "stainless"})
        assert _get_params(copied)["foo"] == "stainless"

        # set_default_query

        # completely overrides already set values
        copied = client.copy(set_default_query={})
        assert _get_params(copied) == {}

        copied = client.copy(set_default_query={"bar": "Robert"})
        assert _get_params(copied)["bar"] == "Robert"

        with pytest.raises(
            ValueError,
            # TODO: update
            match="`default_query` and `set_default_query` arguments are mutually exclusive",
        ):
            client.copy(set_default_query={}, default_query={"foo": "Bar"})

    def test_copy_signature(self) -> None:
        # ensure the same parameters that can be passed to the client are defined in the `.copy()` method
        init_signature = inspect.signature(
            # mypy doesn't like that we access the `__init__` property.
            self.client.__init__,  # type: ignore[misc]
        )
        copy_signature = inspect.signature(self.client.copy)
        exclude_params = {"transport", "proxies", "_strict_response_validation"}

        for name in init_signature.parameters.keys():
            if name in exclude_params:
                continue

            copy_param = copy_signature.parameters.get(name)
            assert copy_param is not None, f"copy() signature is missing the {name} param"

    async def test_request_timeout(self) -> None:
        request = self.client._build_request(FinalRequestOptions(method="get", url="/foo"))
        timeout = httpx.Timeout(**request.extensions["timeout"])  # type: ignore
        assert timeout == DEFAULT_TIMEOUT

        request = self.client._build_request(
            FinalRequestOptions(method="get", url="/foo", timeout=httpx.Timeout(100.0))
        )
        timeout = httpx.Timeout(**request.extensions["timeout"])  # type: ignore
        assert timeout == httpx.Timeout(100.0)

    async def test_client_timeout_option(self) -> None:
        client = AsyncOpenAI(
            base_url=base_url, api_key=api_key, _strict_response_validation=True, timeout=httpx.Timeout(0)
        )

        request = client._build_request(FinalRequestOptions(method="get", url="/foo"))
        timeout = httpx.Timeout(**request.extensions["timeout"])  # type: ignore
        assert timeout == httpx.Timeout(0)

    async def test_http_client_timeout_option(self) -> None:
        # custom timeout given to the httpx client should be used
        async with httpx.AsyncClient(timeout=None) as http_client:
            client = AsyncOpenAI(
                base_url=base_url, api_key=api_key, _strict_response_validation=True, http_client=http_client
            )

            request = client._build_request(FinalRequestOptions(method="get", url="/foo"))
            timeout = httpx.Timeout(**request.extensions["timeout"])  # type: ignore
            assert timeout == httpx.Timeout(None)

        # no timeout given to the httpx client should not use the httpx default
        async with httpx.AsyncClient() as http_client:
            client = AsyncOpenAI(
                base_url=base_url, api_key=api_key, _strict_response_validation=True, http_client=http_client
            )

            request = client._build_request(FinalRequestOptions(method="get", url="/foo"))
            timeout = httpx.Timeout(**request.extensions["timeout"])  # type: ignore
            assert timeout == DEFAULT_TIMEOUT

        # explicitly passing the default timeout currently results in it being ignored
        async with httpx.AsyncClient(timeout=HTTPX_DEFAULT_TIMEOUT) as http_client:
            client = AsyncOpenAI(
                base_url=base_url, api_key=api_key, _strict_response_validation=True, http_client=http_client
            )

            request = client._build_request(FinalRequestOptions(method="get", url="/foo"))
            timeout = httpx.Timeout(**request.extensions["timeout"])  # type: ignore
            assert timeout == DEFAULT_TIMEOUT  # our default

    def test_default_headers_option(self) -> None:
        client = AsyncOpenAI(
            base_url=base_url, api_key=api_key, _strict_response_validation=True, default_headers={"X-Foo": "bar"}
        )
        request = client._build_request(FinalRequestOptions(method="get", url="/foo"))
        assert request.headers.get("x-foo") == "bar"
        assert request.headers.get("x-stainless-lang") == "python"

        client2 = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
            _strict_response_validation=True,
            default_headers={
                "X-Foo": "stainless",
                "X-Stainless-Lang": "my-overriding-header",
            },
        )
        request = client2._build_request(FinalRequestOptions(method="get", url="/foo"))
        assert request.headers.get("x-foo") == "stainless"
        assert request.headers.get("x-stainless-lang") == "my-overriding-header"

    def test_validate_headers(self) -> None:
        client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
        request = client._build_request(FinalRequestOptions(method="get", url="/foo"))
        assert request.headers.get("Authorization") == f"Bearer {api_key}"

        with pytest.raises(Exception):
            client2 = AsyncOpenAI(base_url=base_url, api_key=None, _strict_response_validation=True)
            _ = client2

    def test_default_query_option(self) -> None:
        client = AsyncOpenAI(
            base_url=base_url, api_key=api_key, _strict_response_validation=True, default_query={"query_param": "bar"}
        )
        request = client._build_request(FinalRequestOptions(method="get", url="/foo"))
        url = httpx.URL(request.url)
        assert dict(url.params) == {"query_param": "bar"}

        request = client._build_request(
            FinalRequestOptions(
                method="get",
                url="/foo",
                params={"foo": "baz", "query_param": "overriden"},
            )
        )
        url = httpx.URL(request.url)
        assert dict(url.params) == {"foo": "baz", "query_param": "overriden"}

    def test_request_extra_json(self) -> None:
        request = self.client._build_request(
            FinalRequestOptions(
                method="post",
                url="/foo",
                json_data={"foo": "bar"},
                extra_json={"baz": False},
            ),
        )
        data = json.loads(request.content.decode("utf-8"))
        assert data == {"foo": "bar", "baz": False}

        request = self.client._build_request(
            FinalRequestOptions(
                method="post",
                url="/foo",
                extra_json={"baz": False},
            ),
        )
        data = json.loads(request.content.decode("utf-8"))
        assert data == {"baz": False}

        # `extra_json` takes priority over `json_data` when keys clash
        request = self.client._build_request(
            FinalRequestOptions(
                method="post",
                url="/foo",
                json_data={"foo": "bar", "baz": True},
                extra_json={"baz": None},
            ),
        )
        data = json.loads(request.content.decode("utf-8"))
        assert data == {"foo": "bar", "baz": None}

    def test_request_extra_headers(self) -> None:
        request = self.client._build_request(
            FinalRequestOptions(
                method="post",
                url="/foo",
                **make_request_options(extra_headers={"X-Foo": "Foo"}),
            ),
        )
        assert request.headers.get("X-Foo") == "Foo"

        # `extra_headers` takes priority over `default_headers` when keys clash
        request = self.client.with_options(default_headers={"X-Bar": "true"})._build_request(
            FinalRequestOptions(
                method="post",
                url="/foo",
                **make_request_options(
                    extra_headers={"X-Bar": "false"},
                ),
            ),
        )
        assert request.headers.get("X-Bar") == "false"

    def test_request_extra_query(self) -> None:
        request = self.client._build_request(
            FinalRequestOptions(
                method="post",
                url="/foo",
                **make_request_options(
                    extra_query={"my_query_param": "Foo"},
                ),
            ),
        )
        params = cast(Dict[str, str], dict(request.url.params))
        assert params == {"my_query_param": "Foo"}

        # if both `query` and `extra_query` are given, they are merged
        request = self.client._build_request(
            FinalRequestOptions(
                method="post",
                url="/foo",
                **make_request_options(
                    query={"bar": "1"},
                    extra_query={"foo": "2"},
                ),
            ),
        )
        params = cast(Dict[str, str], dict(request.url.params))
        assert params == {"bar": "1", "foo": "2"}

        # `extra_query` takes priority over `query` when keys clash
        request = self.client._build_request(
            FinalRequestOptions(
                method="post",
                url="/foo",
                **make_request_options(
                    query={"foo": "1"},
                    extra_query={"foo": "2"},
                ),
            ),
        )
        params = cast(Dict[str, str], dict(request.url.params))
        assert params == {"foo": "2"}

    @pytest.mark.respx(base_url=base_url)
    async def test_basic_union_response(self, respx_mock: MockRouter) -> None:
        class Model1(BaseModel):
            name: str

        class Model2(BaseModel):
            foo: str

        respx_mock.get("/foo").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        response = await self.client.get("/foo", cast_to=cast(Any, Union[Model1, Model2]))
        assert isinstance(response, Model2)
        assert response.foo == "bar"

    @pytest.mark.respx(base_url=base_url)
    async def test_union_response_different_types(self, respx_mock: MockRouter) -> None:
        """Union of objects with the same field name using a different type"""

        class Model1(BaseModel):
            foo: int

        class Model2(BaseModel):
            foo: str

        respx_mock.get("/foo").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        response = await self.client.get("/foo", cast_to=cast(Any, Union[Model1, Model2]))
        assert isinstance(response, Model2)
        assert response.foo == "bar"

        respx_mock.get("/foo").mock(return_value=httpx.Response(200, json={"foo": 1}))

        response = await self.client.get("/foo", cast_to=cast(Any, Union[Model1, Model2]))
        assert isinstance(response, Model1)
        assert response.foo == 1

    @pytest.mark.parametrize(
        "client",
        [
            AsyncOpenAI(
                base_url="http://localhost:5000/custom/path/", api_key=api_key, _strict_response_validation=True
            ),
            AsyncOpenAI(
                base_url="http://localhost:5000/custom/path/",
                api_key=api_key,
                _strict_response_validation=True,
                http_client=httpx.AsyncClient(),
            ),
        ],
        ids=["standard", "custom http client"],
    )
    def test_base_url_trailing_slash(self, client: AsyncOpenAI) -> None:
        request = client._build_request(
            FinalRequestOptions(
                method="post",
                url="/foo",
                json_data={"foo": "bar"},
            ),
        )
        assert request.url == "http://localhost:5000/custom/path/foo"

    @pytest.mark.parametrize(
        "client",
        [
            AsyncOpenAI(
                base_url="http://localhost:5000/custom/path/", api_key=api_key, _strict_response_validation=True
            ),
            AsyncOpenAI(
                base_url="http://localhost:5000/custom/path/",
                api_key=api_key,
                _strict_response_validation=True,
                http_client=httpx.AsyncClient(),
            ),
        ],
        ids=["standard", "custom http client"],
    )
    def test_base_url_no_trailing_slash(self, client: AsyncOpenAI) -> None:
        request = client._build_request(
            FinalRequestOptions(
                method="post",
                url="/foo",
                json_data={"foo": "bar"},
            ),
        )
        assert request.url == "http://localhost:5000/custom/path/foo"

    @pytest.mark.parametrize(
        "client",
        [
            AsyncOpenAI(
                base_url="http://localhost:5000/custom/path/", api_key=api_key, _strict_response_validation=True
            ),
            AsyncOpenAI(
                base_url="http://localhost:5000/custom/path/",
                api_key=api_key,
                _strict_response_validation=True,
                http_client=httpx.AsyncClient(),
            ),
        ],
        ids=["standard", "custom http client"],
    )
    def test_absolute_request_url(self, client: AsyncOpenAI) -> None:
        request = client._build_request(
            FinalRequestOptions(
                method="post",
                url="https://myapi.com/foo",
                json_data={"foo": "bar"},
            ),
        )
        assert request.url == "https://myapi.com/foo"

    async def test_client_del(self) -> None:
        client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
        assert not client.is_closed()

        client.__del__()

        await asyncio.sleep(0.2)
        assert client.is_closed()

    async def test_copied_client_does_not_close_http(self) -> None:
        client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
        assert not client.is_closed()

        copied = client.copy()
        assert copied is not client

        copied.__del__()

        await asyncio.sleep(0.2)
        assert not copied.is_closed()
        assert not client.is_closed()

    async def test_client_context_manager(self) -> None:
        client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)
        async with client as c2:
            assert c2 is client
            assert not c2.is_closed()
            assert not client.is_closed()
        assert client.is_closed()

    @pytest.mark.respx(base_url=base_url)
    @pytest.mark.asyncio
    async def test_client_response_validation_error(self, respx_mock: MockRouter) -> None:
        class Model(BaseModel):
            foo: str

        respx_mock.get("/foo").mock(return_value=httpx.Response(200, json={"foo": {"invalid": True}}))

        with pytest.raises(APIResponseValidationError) as exc:
            await self.client.get("/foo", cast_to=Model)

        assert isinstance(exc.value.__cause__, ValidationError)

    @pytest.mark.respx(base_url=base_url)
    @pytest.mark.asyncio
    async def test_default_stream_cls(self, respx_mock: MockRouter) -> None:
        class Model(BaseModel):
            name: str

        respx_mock.post("/foo").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        response = await self.client.post("/foo", cast_to=Model, stream=True)
        assert isinstance(response, AsyncStream)

    @pytest.mark.respx(base_url=base_url)
    @pytest.mark.asyncio
    async def test_received_text_for_expected_json(self, respx_mock: MockRouter) -> None:
        class Model(BaseModel):
            name: str

        respx_mock.get("/foo").mock(return_value=httpx.Response(200, text="my-custom-format"))

        strict_client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)

        with pytest.raises(APIResponseValidationError):
            await strict_client.get("/foo", cast_to=Model)

        client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=False)

        response = await client.get("/foo", cast_to=Model)
        assert isinstance(response, str)  # type: ignore[unreachable]

    @pytest.mark.parametrize(
        "remaining_retries,retry_after,timeout",
        [
            [3, "20", 20],
            [3, "0", 0.5],
            [3, "-10", 0.5],
            [3, "60", 60],
            [3, "61", 0.5],
            [3, "Fri, 29 Sep 2023 16:26:57 GMT", 20],
            [3, "Fri, 29 Sep 2023 16:26:37 GMT", 0.5],
            [3, "Fri, 29 Sep 2023 16:26:27 GMT", 0.5],
            [3, "Fri, 29 Sep 2023 16:27:37 GMT", 60],
            [3, "Fri, 29 Sep 2023 16:27:38 GMT", 0.5],
            [3, "99999999999999999999999999999999999", 0.5],
            [3, "Zun, 29 Sep 2023 16:26:27 GMT", 0.5],
            [3, "", 0.5],
            [2, "", 0.5 * 2.0],
            [1, "", 0.5 * 4.0],
        ],
    )
    @mock.patch("time.time", mock.MagicMock(return_value=1696004797))
    @pytest.mark.asyncio
    async def test_parse_retry_after_header(self, remaining_retries: int, retry_after: str, timeout: float) -> None:
        client = AsyncOpenAI(base_url=base_url, api_key=api_key, _strict_response_validation=True)

        headers = httpx.Headers({"retry-after": retry_after})
        options = FinalRequestOptions(method="get", url="/foo", max_retries=3)
        calculated = client._calculate_retry_timeout(remaining_retries, options, headers)
        assert calculated == pytest.approx(timeout, 0.5 * 0.875)  # pyright: ignore[reportUnknownMemberType]
