from __future__ import annotations

import os
import json
from typing import Any, Callable
from typing_extensions import Literal, TypeVar

import httpx
import pytest
from respx import MockRouter
from pydantic import BaseModel
from inline_snapshot import snapshot

import openai
from openai import OpenAI, AsyncOpenAI
from openai._utils import assert_signatures_in_sync

from ._utils import print_obj
from ...conftest import base_url
from ..schema_types.query import Query

_T = TypeVar("_T")

# all the snapshots in this file are auto-generated from the live API
#
# you can update them with
#
# `OPENAI_LIVE=1 pytest --inline-snapshot=fix`


@pytest.mark.respx(base_url=base_url)
def test_parse_nothing(client: OpenAI, respx_mock: MockRouter, monkeypatch: pytest.MonkeyPatch) -> None:
    completion = _make_snapshot_request(
        lambda c: c.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "user",
                    "content": "What's the weather like in SF?",
                },
            ],
        ),
        content_snapshot=snapshot(
            '{"id": "chatcmpl-9tABLlmqdEOYnmmWATUI3dNKlfXa3", "object": "chat.completion", "created": 1722934207, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": "I\'m unable to provide real-time weather updates. For the current weather in San Francisco, I recommend checking a reliable weather website or app.", "refusal": null}, "logprobs": null, "finish_reason": "stop"}], "usage": {"prompt_tokens": 14, "completion_tokens": 27, "total_tokens": 41}, "system_fingerprint": "fp_e1a05a1dce"}'
        ),
        mock_client=client,
        respx_mock=respx_mock,
    )

    assert print_obj(completion, monkeypatch) == snapshot(
        """\
ParsedChatCompletion[NoneType](
    choices=[
        ParsedChoice[NoneType](
            finish_reason='stop',
            index=0,
            logprobs=None,
            message=ParsedChatCompletionMessage[NoneType](
                content="I'm unable to provide real-time weather updates. For the current weather in San Francisco, I 
recommend checking a reliable weather website or app.",
                function_call=None,
                parsed=None,
                refusal=None,
                role='assistant',
                tool_calls=[]
            )
        )
    ],
    created=1722934207,
    id='chatcmpl-9tABLlmqdEOYnmmWATUI3dNKlfXa3',
    model='gpt-4o-2024-08-06',
    object='chat.completion',
    service_tier=None,
    system_fingerprint='fp_e1a05a1dce',
    usage=CompletionUsage(completion_tokens=27, prompt_tokens=14, total_tokens=41)
)
"""
    )


@pytest.mark.respx(base_url=base_url)
def test_parse_pydantic_model(client: OpenAI, respx_mock: MockRouter, monkeypatch: pytest.MonkeyPatch) -> None:
    class Location(BaseModel):
        city: str
        temperature: float
        units: Literal["c", "f"]

    completion = _make_snapshot_request(
        lambda c: c.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "user",
                    "content": "What's the weather like in SF?",
                },
            ],
            response_format=Location,
        ),
        content_snapshot=snapshot(
            '{"id": "chatcmpl-9tABUwdw3Kbe3VPRnMofh9lJkFkLV", "object": "chat.completion", "created": 1722934216, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": "{\\"city\\":\\"San Francisco\\",\\"temperature\\":65,\\"units\\":\\"f\\"}", "refusal": null}, "logprobs": null, "finish_reason": "stop"}], "usage": {"prompt_tokens": 17, "completion_tokens": 14, "total_tokens": 31}, "system_fingerprint": "fp_e1a05a1dce"}'
        ),
        mock_client=client,
        respx_mock=respx_mock,
    )

    assert print_obj(completion, monkeypatch) == snapshot(
        """\
ParsedChatCompletion[Location](
    choices=[
        ParsedChoice[Location](
            finish_reason='stop',
            index=0,
            logprobs=None,
            message=ParsedChatCompletionMessage[Location](
                content='{"city":"San Francisco","temperature":65,"units":"f"}',
                function_call=None,
                parsed=Location(city='San Francisco', temperature=65.0, units='f'),
                refusal=None,
                role='assistant',
                tool_calls=[]
            )
        )
    ],
    created=1722934216,
    id='chatcmpl-9tABUwdw3Kbe3VPRnMofh9lJkFkLV',
    model='gpt-4o-2024-08-06',
    object='chat.completion',
    service_tier=None,
    system_fingerprint='fp_e1a05a1dce',
    usage=CompletionUsage(completion_tokens=14, prompt_tokens=17, total_tokens=31)
)
"""
    )


@pytest.mark.respx(base_url=base_url)
def test_parse_pydantic_model_multiple_choices(
    client: OpenAI, respx_mock: MockRouter, monkeypatch: pytest.MonkeyPatch
) -> None:
    class Location(BaseModel):
        city: str
        temperature: float
        units: Literal["c", "f"]

    completion = _make_snapshot_request(
        lambda c: c.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "user",
                    "content": "What's the weather like in SF?",
                },
            ],
            n=3,
            response_format=Location,
        ),
        content_snapshot=snapshot(
            '{"id": "chatcmpl-9tABVfBu4ZdyQFKe8RgsWsyL7UoIj", "object": "chat.completion", "created": 1722934217, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": "{\\"city\\":\\"San Francisco\\",\\"temperature\\":58.0,\\"units\\":\\"f\\"}", "refusal": null}, "logprobs": null, "finish_reason": "stop"}, {"index": 1, "message": {"role": "assistant", "content": "{\\"city\\":\\"San Francisco\\",\\"temperature\\":61,\\"units\\":\\"f\\"}", "refusal": null}, "logprobs": null, "finish_reason": "stop"}, {"index": 2, "message": {"role": "assistant", "content": "{\\"city\\":\\"San Francisco\\",\\"temperature\\":65,\\"units\\":\\"f\\"}", "refusal": null}, "logprobs": null, "finish_reason": "stop"}], "usage": {"prompt_tokens": 17, "completion_tokens": 44, "total_tokens": 61}, "system_fingerprint": "fp_e1a05a1dce"}'
        ),
        mock_client=client,
        respx_mock=respx_mock,
    )

    assert print_obj(completion.choices, monkeypatch) == snapshot(
        """\
[
    ParsedChoice[Location](
        finish_reason='stop',
        index=0,
        logprobs=None,
        message=ParsedChatCompletionMessage[Location](
            content='{"city":"San Francisco","temperature":58.0,"units":"f"}',
            function_call=None,
            parsed=Location(city='San Francisco', temperature=58.0, units='f'),
            refusal=None,
            role='assistant',
            tool_calls=[]
        )
    ),
    ParsedChoice[Location](
        finish_reason='stop',
        index=1,
        logprobs=None,
        message=ParsedChatCompletionMessage[Location](
            content='{"city":"San Francisco","temperature":61,"units":"f"}',
            function_call=None,
            parsed=Location(city='San Francisco', temperature=61.0, units='f'),
            refusal=None,
            role='assistant',
            tool_calls=[]
        )
    ),
    ParsedChoice[Location](
        finish_reason='stop',
        index=2,
        logprobs=None,
        message=ParsedChatCompletionMessage[Location](
            content='{"city":"San Francisco","temperature":65,"units":"f"}',
            function_call=None,
            parsed=Location(city='San Francisco', temperature=65.0, units='f'),
            refusal=None,
            role='assistant',
            tool_calls=[]
        )
    )
]
"""
    )


@pytest.mark.respx(base_url=base_url)
def test_pydantic_tool_model_all_types(client: OpenAI, respx_mock: MockRouter, monkeypatch: pytest.MonkeyPatch) -> None:
    completion = _make_snapshot_request(
        lambda c: c.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "user",
                    "content": "look up all my orders in may of last year that were fulfilled but not delivered on time",
                },
            ],
            tools=[openai.pydantic_function_tool(Query)],
            response_format=Query,
        ),
        content_snapshot=snapshot(
            '{"id": "chatcmpl-9tABVRLORZbby5zZjZhyrUdDU1XhB", "object": "chat.completion", "created": 1722934217, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": null, "tool_calls": [{"id": "call_VcgQcA1C047fQnXDG0PQXG7O", "type": "function", "function": {"name": "Query", "arguments": "{\\"table_name\\":\\"orders\\",\\"columns\\":[\\"id\\",\\"status\\",\\"expected_delivery_date\\",\\"delivered_at\\"],\\"conditions\\":[{\\"column\\":\\"ordered_at\\",\\"operator\\":\\"=\\",\\"value\\":\\"2022-05\\"},{\\"column\\":\\"status\\",\\"operator\\":\\"=\\",\\"value\\":\\"fulfilled\\"},{\\"column\\":\\"delivered_at\\",\\"operator\\":\\">\\",\\"value\\":{\\"column_name\\":\\"expected_delivery_date\\"}}],\\"order_by\\":\\"asc\\"}"}}], "refusal": null}, "logprobs": null, "finish_reason": "tool_calls"}], "usage": {"prompt_tokens": 195, "completion_tokens": 85, "total_tokens": 280}, "system_fingerprint": "fp_e1a05a1dce"}'
        ),
        mock_client=client,
        respx_mock=respx_mock,
    )

    assert print_obj(completion.choices[0], monkeypatch) == snapshot(
        """\
ParsedChoice[Query](
    finish_reason='tool_calls',
    index=0,
    logprobs=None,
    message=ParsedChatCompletionMessage[Query](
        content=None,
        function_call=None,
        parsed=None,
        refusal=None,
        role='assistant',
        tool_calls=[
            ParsedFunctionToolCall(
                function=ParsedFunction(
                    arguments='{"table_name":"orders","columns":["id","status","expected_delivery_date","delivered_at"],
"conditions":[{"column":"ordered_at","operator":"=","value":"2022-05"},{"column":"status","operator":"=","value":"fulfil
led"},{"column":"delivered_at","operator":">","value":{"column_name":"expected_delivery_date"}}],"order_by":"asc"}',
                    name='Query',
                    parsed_arguments=Query(
                        columns=[
                            <Column.id: 'id'>,
                            <Column.status: 'status'>,
                            <Column.expected_delivery_date: 'expected_delivery_date'>,
                            <Column.delivered_at: 'delivered_at'>
                        ],
                        conditions=[
                            Condition(column='ordered_at', operator=<Operator.eq: '='>, value='2022-05'),
                            Condition(column='status', operator=<Operator.eq: '='>, value='fulfilled'),
                            Condition(
                                column='delivered_at',
                                operator=<Operator.gt: '>'>,
                                value=DynamicValue(column_name='expected_delivery_date')
                            )
                        ],
                        order_by=<OrderBy.asc: 'asc'>,
                        table_name=<Table.orders: 'orders'>
                    )
                ),
                id='call_VcgQcA1C047fQnXDG0PQXG7O',
                type='function'
            )
        ]
    )
)
"""
    )


@pytest.mark.respx(base_url=base_url)
def test_parse_max_tokens_reached(client: OpenAI, respx_mock: MockRouter) -> None:
    class Location(BaseModel):
        city: str
        temperature: float
        units: Literal["c", "f"]

    with pytest.raises(openai.LengthFinishReasonError):
        _make_snapshot_request(
            lambda c: c.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=[
                    {
                        "role": "user",
                        "content": "What's the weather like in SF?",
                    },
                ],
                max_tokens=1,
                response_format=Location,
            ),
            content_snapshot=snapshot(
                '{"id": "chatcmpl-9tABXbi3qast6oJvdaqQcK9C7k9fn", "object": "chat.completion", "created": 1722934219, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": "{\\"", "refusal": null}, "logprobs": null, "finish_reason": "length"}], "usage": {"prompt_tokens": 17, "completion_tokens": 1, "total_tokens": 18}, "system_fingerprint": "fp_e1a05a1dce"}'
            ),
            mock_client=client,
            respx_mock=respx_mock,
        )


@pytest.mark.respx(base_url=base_url)
def test_parse_pydantic_model_refusal(client: OpenAI, respx_mock: MockRouter, monkeypatch: pytest.MonkeyPatch) -> None:
    class Location(BaseModel):
        city: str
        temperature: float
        units: Literal["c", "f"]

    completion = _make_snapshot_request(
        lambda c: c.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "user",
                    "content": "How do I make anthrax?",
                },
            ],
            response_format=Location,
        ),
        content_snapshot=snapshot(
            '{"id": "chatcmpl-9tABXJEffhEWxp24MeLxkDJCMtWmx", "object": "chat.completion", "created": 1722934219, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": null, "refusal": "I\'m very sorry, but I can\'t assist with that."}, "logprobs": null, "finish_reason": "stop"}], "usage": {"prompt_tokens": 17, "completion_tokens": 12, "total_tokens": 29}, "system_fingerprint": "fp_e1a05a1dce"}'
        ),
        mock_client=client,
        respx_mock=respx_mock,
    )

    assert print_obj(completion.choices, monkeypatch) == snapshot(
        """\
[
    ParsedChoice[Location](
        finish_reason='stop',
        index=0,
        logprobs=None,
        message=ParsedChatCompletionMessage[Location](
            content=None,
            function_call=None,
            parsed=None,
            refusal="I'm very sorry, but I can't assist with that.",
            role='assistant',
            tool_calls=[]
        )
    )
]
"""
    )


@pytest.mark.respx(base_url=base_url)
def test_parse_pydantic_tool(client: OpenAI, respx_mock: MockRouter, monkeypatch: pytest.MonkeyPatch) -> None:
    class GetWeatherArgs(BaseModel):
        city: str
        country: str
        units: Literal["c", "f"] = "c"

    completion = _make_snapshot_request(
        lambda c: c.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "user",
                    "content": "What's the weather like in Edinburgh?",
                },
            ],
            tools=[
                openai.pydantic_function_tool(GetWeatherArgs),
            ],
        ),
        content_snapshot=snapshot(
            '{"id": "chatcmpl-9tABgtKnF7Gbri4CmpOocmhg0UgBF", "object": "chat.completion", "created": 1722934228, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": null, "tool_calls": [{"id": "call_9rqjEc1DQRADTYGVV45LbZwL", "type": "function", "function": {"name": "GetWeatherArgs", "arguments": "{\\"city\\":\\"Edinburgh\\",\\"country\\":\\"UK\\",\\"units\\":\\"c\\"}"}}], "refusal": null}, "logprobs": null, "finish_reason": "tool_calls"}], "usage": {"prompt_tokens": 76, "completion_tokens": 24, "total_tokens": 100}, "system_fingerprint": "fp_e1a05a1dce"}'
        ),
        mock_client=client,
        respx_mock=respx_mock,
    )

    assert print_obj(completion.choices, monkeypatch) == snapshot(
        """\
[
    ParsedChoice[NoneType](
        finish_reason='tool_calls',
        index=0,
        logprobs=None,
        message=ParsedChatCompletionMessage[NoneType](
            content=None,
            function_call=None,
            parsed=None,
            refusal=None,
            role='assistant',
            tool_calls=[
                ParsedFunctionToolCall(
                    function=ParsedFunction(
                        arguments='{"city":"Edinburgh","country":"UK","units":"c"}',
                        name='GetWeatherArgs',
                        parsed_arguments=GetWeatherArgs(city='Edinburgh', country='UK', units='c')
                    ),
                    id='call_9rqjEc1DQRADTYGVV45LbZwL',
                    type='function'
                )
            ]
        )
    )
]
"""
    )


@pytest.mark.respx(base_url=base_url)
def test_parse_multiple_pydantic_tools(client: OpenAI, respx_mock: MockRouter, monkeypatch: pytest.MonkeyPatch) -> None:
    class GetWeatherArgs(BaseModel):
        """Get the temperature for the given country/city combo"""

        city: str
        country: str
        units: Literal["c", "f"] = "c"

    class GetStockPrice(BaseModel):
        ticker: str
        exchange: str

    completion = _make_snapshot_request(
        lambda c: c.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "user",
                    "content": "What's the weather like in Edinburgh?",
                },
                {
                    "role": "user",
                    "content": "What's the price of AAPL?",
                },
            ],
            tools=[
                openai.pydantic_function_tool(GetWeatherArgs),
                openai.pydantic_function_tool(
                    GetStockPrice, name="get_stock_price", description="Fetch the latest price for a given ticker"
                ),
            ],
        ),
        content_snapshot=snapshot(
            '{"id": "chatcmpl-9tABqDpvDTi0Cg8PHtKdNSFoh4UJv", "object": "chat.completion", "created": 1722934238, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": null, "tool_calls": [{"id": "call_Yeg67XmQbMcohm3NGj0g12ty", "type": "function", "function": {"name": "GetWeatherArgs", "arguments": "{\\"city\\": \\"Edinburgh\\", \\"country\\": \\"GB\\", \\"units\\": \\"c\\"}"}}, {"id": "call_OGg3UZC2ksjAg7yrLXy8t1MO", "type": "function", "function": {"name": "get_stock_price", "arguments": "{\\"ticker\\": \\"AAPL\\", \\"exchange\\": \\"NASDAQ\\"}"}}], "refusal": null}, "logprobs": null, "finish_reason": "tool_calls"}], "usage": {"prompt_tokens": 149, "completion_tokens": 60, "total_tokens": 209}, "system_fingerprint": "fp_e1a05a1dce"}'
        ),
        mock_client=client,
        respx_mock=respx_mock,
    )

    assert print_obj(completion.choices, monkeypatch) == snapshot(
        """\
[
    ParsedChoice[NoneType](
        finish_reason='tool_calls',
        index=0,
        logprobs=None,
        message=ParsedChatCompletionMessage[NoneType](
            content=None,
            function_call=None,
            parsed=None,
            refusal=None,
            role='assistant',
            tool_calls=[
                ParsedFunctionToolCall(
                    function=ParsedFunction(
                        arguments='{"city": "Edinburgh", "country": "GB", "units": "c"}',
                        name='GetWeatherArgs',
                        parsed_arguments=GetWeatherArgs(city='Edinburgh', country='GB', units='c')
                    ),
                    id='call_Yeg67XmQbMcohm3NGj0g12ty',
                    type='function'
                ),
                ParsedFunctionToolCall(
                    function=ParsedFunction(
                        arguments='{"ticker": "AAPL", "exchange": "NASDAQ"}',
                        name='get_stock_price',
                        parsed_arguments=GetStockPrice(exchange='NASDAQ', ticker='AAPL')
                    ),
                    id='call_OGg3UZC2ksjAg7yrLXy8t1MO',
                    type='function'
                )
            ]
        )
    )
]
"""
    )


@pytest.mark.respx(base_url=base_url)
def test_parse_strict_tools(client: OpenAI, respx_mock: MockRouter, monkeypatch: pytest.MonkeyPatch) -> None:
    completion = _make_snapshot_request(
        lambda c: c.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "user",
                    "content": "What's the weather like in SF?",
                },
            ],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "city": {"type": "string"},
                                "state": {"type": "string"},
                            },
                            "required": [
                                "city",
                                "state",
                            ],
                            "additionalProperties": False,
                        },
                        "strict": True,
                    },
                }
            ],
        ),
        content_snapshot=snapshot(
            '{"id": "chatcmpl-9tAC0vDx3MfupXmsduSZavLVaLcrA", "object": "chat.completion", "created": 1722934248, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": null, "tool_calls": [{"id": "call_iNznvWR4R81mizFFHjgh7o4i", "type": "function", "function": {"name": "get_weather", "arguments": "{\\"city\\":\\"San Francisco\\",\\"state\\":\\"CA\\"}"}}], "refusal": null}, "logprobs": null, "finish_reason": "tool_calls"}], "usage": {"prompt_tokens": 48, "completion_tokens": 19, "total_tokens": 67}, "system_fingerprint": "fp_e1a05a1dce"}'
        ),
        mock_client=client,
        respx_mock=respx_mock,
    )

    assert print_obj(completion.choices, monkeypatch) == snapshot(
        """\
[
    ParsedChoice[NoneType](
        finish_reason='tool_calls',
        index=0,
        logprobs=None,
        message=ParsedChatCompletionMessage[NoneType](
            content=None,
            function_call=None,
            parsed=None,
            refusal=None,
            role='assistant',
            tool_calls=[
                ParsedFunctionToolCall(
                    function=ParsedFunction(
                        arguments='{"city":"San Francisco","state":"CA"}',
                        name='get_weather',
                        parsed_arguments={'city': 'San Francisco', 'state': 'CA'}
                    ),
                    id='call_iNznvWR4R81mizFFHjgh7o4i',
                    type='function'
                )
            ]
        )
    )
]
"""
    )


def test_parse_non_strict_tools(client: OpenAI) -> None:
    with pytest.raises(
        ValueError, match="`get_weather` is not strict. Only `strict` function tools can be auto-parsed"
    ):
        client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "parameters": {},
                    },
                }
            ],
        )


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_parse_method_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    assert_signatures_in_sync(
        checking_client.chat.completions.create,
        checking_client.beta.chat.completions.parse,
        exclude_params={"response_format", "stream"},
    )


def _make_snapshot_request(
    func: Callable[[OpenAI], _T],
    *,
    content_snapshot: Any,
    respx_mock: MockRouter,
    mock_client: OpenAI,
) -> _T:
    live = os.environ.get("OPENAI_LIVE") == "1"
    if live:

        def _on_response(response: httpx.Response) -> None:
            # update the content snapshot
            assert json.dumps(json.loads(response.read())) == content_snapshot

        respx_mock.stop()

        client = OpenAI(
            http_client=httpx.Client(
                event_hooks={
                    "response": [_on_response],
                }
            )
        )
    else:
        respx_mock.post("/chat/completions").mock(
            return_value=httpx.Response(
                200,
                content=content_snapshot._old_value,
                headers={"content-type": "application/json"},
            )
        )

        client = mock_client

    result = func(client)

    if live:
        client.close()

    return result
