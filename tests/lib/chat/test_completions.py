from __future__ import annotations

import os
import json
from enum import Enum
from typing import Any, List, Callable, Optional
from typing_extensions import Literal, TypeVar

import httpx
import pytest
from respx import MockRouter
from pydantic import Field, BaseModel
from inline_snapshot import snapshot

import openai
from openai import OpenAI, AsyncOpenAI
from openai._utils import assert_signatures_in_sync
from openai._compat import PYDANTIC_V2

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
            '{"id": "chatcmpl-9tXjSozlYq8oGdlRH3vgLsiUNRg8c", "object": "chat.completion", "created": 1723024734, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": "I\'m unable to provide real-time weather updates. To find out the current weather in San Francisco, please check a reliable weather website or app.", "refusal": null}, "logprobs": null, "finish_reason": "stop"}], "usage": {"prompt_tokens": 14, "completion_tokens": 28, "total_tokens": 42}, "system_fingerprint": "fp_845eaabc1f"}'
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
                content="I'm unable to provide real-time weather updates. To find out the current weather in San 
Francisco, please check a reliable weather website or app.",
                function_call=None,
                parsed=None,
                refusal=None,
                role='assistant',
                tool_calls=[]
            )
        )
    ],
    created=1723024734,
    id='chatcmpl-9tXjSozlYq8oGdlRH3vgLsiUNRg8c',
    model='gpt-4o-2024-08-06',
    object='chat.completion',
    service_tier=None,
    system_fingerprint='fp_845eaabc1f',
    usage=CompletionUsage(completion_tokens=28, completion_tokens_details=None, prompt_tokens=14, total_tokens=42)
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
            '{"id": "chatcmpl-9tXjTNupyDe7nL1Z8eOO6BdSyrHAD", "object": "chat.completion", "created": 1723024735, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": "{\\"city\\":\\"San Francisco\\",\\"temperature\\":56,\\"units\\":\\"f\\"}", "refusal": null}, "logprobs": null, "finish_reason": "stop"}], "usage": {"prompt_tokens": 17, "completion_tokens": 14, "total_tokens": 31}, "system_fingerprint": "fp_2a322c9ffc"}'
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
                content='{"city":"San Francisco","temperature":56,"units":"f"}',
                function_call=None,
                parsed=Location(city='San Francisco', temperature=56.0, units='f'),
                refusal=None,
                role='assistant',
                tool_calls=[]
            )
        )
    ],
    created=1723024735,
    id='chatcmpl-9tXjTNupyDe7nL1Z8eOO6BdSyrHAD',
    model='gpt-4o-2024-08-06',
    object='chat.completion',
    service_tier=None,
    system_fingerprint='fp_2a322c9ffc',
    usage=CompletionUsage(completion_tokens=14, completion_tokens_details=None, prompt_tokens=17, total_tokens=31)
)
"""
    )


@pytest.mark.respx(base_url=base_url)
def test_parse_pydantic_model_optional_default(
    client: OpenAI, respx_mock: MockRouter, monkeypatch: pytest.MonkeyPatch
) -> None:
    class Location(BaseModel):
        city: str
        temperature: float
        units: Optional[Literal["c", "f"]] = None

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
            '{"id": "chatcmpl-9y39Q2jGzWmeEZlm5CoNVOuQzcxP4", "object": "chat.completion", "created": 1724098820, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": "{\\"city\\":\\"San Francisco\\",\\"temperature\\":62,\\"units\\":\\"f\\"}", "refusal": null}, "logprobs": null, "finish_reason": "stop"}], "usage": {"prompt_tokens": 17, "completion_tokens": 14, "total_tokens": 31}, "system_fingerprint": "fp_2a322c9ffc"}'
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
                content='{"city":"San Francisco","temperature":62,"units":"f"}',
                function_call=None,
                parsed=Location(city='San Francisco', temperature=62.0, units='f'),
                refusal=None,
                role='assistant',
                tool_calls=[]
            )
        )
    ],
    created=1724098820,
    id='chatcmpl-9y39Q2jGzWmeEZlm5CoNVOuQzcxP4',
    model='gpt-4o-2024-08-06',
    object='chat.completion',
    service_tier=None,
    system_fingerprint='fp_2a322c9ffc',
    usage=CompletionUsage(completion_tokens=14, completion_tokens_details=None, prompt_tokens=17, total_tokens=31)
)
"""
    )


@pytest.mark.respx(base_url=base_url)
def test_parse_pydantic_model_enum(client: OpenAI, respx_mock: MockRouter, monkeypatch: pytest.MonkeyPatch) -> None:
    class Color(Enum):
        """The detected color"""

        RED = "red"
        BLUE = "blue"
        GREEN = "green"

    class ColorDetection(BaseModel):
        color: Color
        hex_color_code: str = Field(description="The hex color code of the detected color")

    if not PYDANTIC_V2:
        ColorDetection.update_forward_refs(**locals())  # type: ignore

    completion = _make_snapshot_request(
        lambda c: c.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "user", "content": "What color is a Coke can?"},
            ],
            response_format=ColorDetection,
        ),
        content_snapshot=snapshot(
            '{"id": "chatcmpl-9vK4UZVr385F2UgZlP1ShwPn2nFxG", "object": "chat.completion", "created": 1723448878, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": "{\\"color\\":\\"red\\",\\"hex_color_code\\":\\"#FF0000\\"}", "refusal": null}, "logprobs": null, "finish_reason": "stop"}], "usage": {"prompt_tokens": 18, "completion_tokens": 14, "total_tokens": 32}, "system_fingerprint": "fp_845eaabc1f"}'
        ),
        mock_client=client,
        respx_mock=respx_mock,
    )

    assert print_obj(completion.choices[0], monkeypatch) == snapshot(
        """\
ParsedChoice[ColorDetection](
    finish_reason='stop',
    index=0,
    logprobs=None,
    message=ParsedChatCompletionMessage[ColorDetection](
        content='{"color":"red","hex_color_code":"#FF0000"}',
        function_call=None,
        parsed=ColorDetection(color=<Color.RED: 'red'>, hex_color_code='#FF0000'),
        refusal=None,
        role='assistant',
        tool_calls=[]
    )
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
            '{"id": "chatcmpl-9tXjUrNFyyjSB2FJ842TMDNRM6Gen", "object": "chat.completion", "created": 1723024736, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": "{\\"city\\":\\"San Francisco\\",\\"temperature\\":58,\\"units\\":\\"f\\"}", "refusal": null}, "logprobs": null, "finish_reason": "stop"}, {"index": 1, "message": {"role": "assistant", "content": "{\\"city\\":\\"San Francisco\\",\\"temperature\\":58,\\"units\\":\\"f\\"}", "refusal": null}, "logprobs": null, "finish_reason": "stop"}, {"index": 2, "message": {"role": "assistant", "content": "{\\"city\\":\\"San Francisco\\",\\"temperature\\":63,\\"units\\":\\"f\\"}", "refusal": null}, "logprobs": null, "finish_reason": "stop"}], "usage": {"prompt_tokens": 17, "completion_tokens": 42, "total_tokens": 59}, "system_fingerprint": "fp_845eaabc1f"}'
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
            content='{"city":"San Francisco","temperature":58,"units":"f"}',
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
            content='{"city":"San Francisco","temperature":58,"units":"f"}',
            function_call=None,
            parsed=Location(city='San Francisco', temperature=58.0, units='f'),
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
            content='{"city":"San Francisco","temperature":63,"units":"f"}',
            function_call=None,
            parsed=Location(city='San Francisco', temperature=63.0, units='f'),
            refusal=None,
            role='assistant',
            tool_calls=[]
        )
    )
]
"""
    )


@pytest.mark.respx(base_url=base_url)
@pytest.mark.skipif(not PYDANTIC_V2, reason="dataclasses only supported in v2")
def test_parse_pydantic_dataclass(client: OpenAI, respx_mock: MockRouter, monkeypatch: pytest.MonkeyPatch) -> None:
    from pydantic.dataclasses import dataclass

    @dataclass
    class CalendarEvent:
        name: str
        date: str
        participants: List[str]

    completion = _make_snapshot_request(
        lambda c: c.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "Extract the event information."},
                {"role": "user", "content": "Alice and Bob are going to a science fair on Friday."},
            ],
            response_format=CalendarEvent,
        ),
        content_snapshot=snapshot(
            '{"id": "chatcmpl-9wdGqXkJJARAz7rOrLH5u5FBwLjF3", "object": "chat.completion", "created": 1723761008, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": "{\\"name\\":\\"Science Fair\\",\\"date\\":\\"Friday\\",\\"participants\\":[\\"Alice\\",\\"Bob\\"]}", "refusal": null}, "logprobs": null, "finish_reason": "stop"}], "usage": {"prompt_tokens": 32, "completion_tokens": 17, "total_tokens": 49}, "system_fingerprint": "fp_2a322c9ffc"}'
        ),
        mock_client=client,
        respx_mock=respx_mock,
    )

    assert print_obj(completion, monkeypatch) == snapshot(
        """\
ParsedChatCompletion[CalendarEvent](
    choices=[
        ParsedChoice[CalendarEvent](
            finish_reason='stop',
            index=0,
            logprobs=None,
            message=ParsedChatCompletionMessage[CalendarEvent](
                content='{"name":"Science Fair","date":"Friday","participants":["Alice","Bob"]}',
                function_call=None,
                parsed=CalendarEvent(name='Science Fair', date='Friday', participants=['Alice', 'Bob']),
                refusal=None,
                role='assistant',
                tool_calls=[]
            )
        )
    ],
    created=1723761008,
    id='chatcmpl-9wdGqXkJJARAz7rOrLH5u5FBwLjF3',
    model='gpt-4o-2024-08-06',
    object='chat.completion',
    service_tier=None,
    system_fingerprint='fp_2a322c9ffc',
    usage=CompletionUsage(completion_tokens=17, completion_tokens_details=None, prompt_tokens=32, total_tokens=49)
)
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
            '{"id": "chatcmpl-9tXjVJVCLTn7CWFhpjETixvvApCk3", "object": "chat.completion", "created": 1723024737, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": null, "tool_calls": [{"id": "call_Un4g0IXeQGOyqKBS3zhqNCox", "type": "function", "function": {"name": "Query", "arguments": "{\\"table_name\\":\\"orders\\",\\"columns\\":[\\"id\\",\\"status\\",\\"expected_delivery_date\\",\\"delivered_at\\",\\"shipped_at\\",\\"ordered_at\\"],\\"conditions\\":[{\\"column\\":\\"ordered_at\\",\\"operator\\":\\">=\\",\\"value\\":\\"2022-05-01\\"},{\\"column\\":\\"ordered_at\\",\\"operator\\":\\"<=\\",\\"value\\":\\"2022-05-31\\"},{\\"column\\":\\"status\\",\\"operator\\":\\"=\\",\\"value\\":\\"fulfilled\\"},{\\"column\\":\\"delivered_at\\",\\"operator\\":\\">\\",\\"value\\":{\\"column_name\\":\\"expected_delivery_date\\"}}],\\"order_by\\":\\"asc\\"}"}}], "refusal": null}, "logprobs": null, "finish_reason": "tool_calls"}], "usage": {"prompt_tokens": 195, "completion_tokens": 114, "total_tokens": 309}, "system_fingerprint": "fp_845eaabc1f"}'
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
                    arguments='{"table_name":"orders","columns":["id","status","expected_delivery_date","delivered_at","
shipped_at","ordered_at"],"conditions":[{"column":"ordered_at","operator":">=","value":"2022-05-01"},{"column":"ordered_
at","operator":"<=","value":"2022-05-31"},{"column":"status","operator":"=","value":"fulfilled"},{"column":"delivered_at
","operator":">","value":{"column_name":"expected_delivery_date"}}],"order_by":"asc"}',
                    name='Query',
                    parsed_arguments=Query(
                        columns=[
                            <Column.id: 'id'>,
                            <Column.status: 'status'>,
                            <Column.expected_delivery_date: 'expected_delivery_date'>,
                            <Column.delivered_at: 'delivered_at'>,
                            <Column.shipped_at: 'shipped_at'>,
                            <Column.ordered_at: 'ordered_at'>
                        ],
                        conditions=[
                            Condition(column='ordered_at', operator=<Operator.ge: '>='>, value='2022-05-01'),
                            Condition(column='ordered_at', operator=<Operator.le: '<='>, value='2022-05-31'),
                            Condition(column='status', operator=<Operator.eq: '='>, value='fulfilled'),
                            Condition(
                                column='delivered_at',
                                operator=<Operator.gt: '>'>,
                                value=DynamicValue(column_name='expected_delivery_date')
                            )
                        ],
                        name=None,
                        order_by=<OrderBy.asc: 'asc'>,
                        table_name=<Table.orders: 'orders'>
                    )
                ),
                id='call_Un4g0IXeQGOyqKBS3zhqNCox',
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
                '{"id": "chatcmpl-9tXjYACgVKixKdMv2nVQqDVELkdSF", "object": "chat.completion", "created": 1723024740, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": "{\\"", "refusal": null}, "logprobs": null, "finish_reason": "length"}], "usage": {"prompt_tokens": 17, "completion_tokens": 1, "total_tokens": 18}, "system_fingerprint": "fp_2a322c9ffc"}'
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
            '{"id": "chatcmpl-9tXm7FnIj3hSot5xM4c954MIePle0", "object": "chat.completion", "created": 1723024899, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": null, "refusal": "I\'m very sorry, but I can\'t assist with that request."}, "logprobs": null, "finish_reason": "stop"}], "usage": {"prompt_tokens": 17, "completion_tokens": 13, "total_tokens": 30}, "system_fingerprint": "fp_845eaabc1f"}'
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
            refusal="I'm very sorry, but I can't assist with that request.",
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
            '{"id": "chatcmpl-9tXjbQ9V0l5XPlynOJHKvrWsJQymO", "object": "chat.completion", "created": 1723024743, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": null, "tool_calls": [{"id": "call_EEaIYq8aTdiDWro8jILNl3XK", "type": "function", "function": {"name": "GetWeatherArgs", "arguments": "{\\"city\\":\\"Edinburgh\\",\\"country\\":\\"GB\\",\\"units\\":\\"c\\"}"}}], "refusal": null}, "logprobs": null, "finish_reason": "tool_calls"}], "usage": {"prompt_tokens": 76, "completion_tokens": 24, "total_tokens": 100}, "system_fingerprint": "fp_2a322c9ffc"}'
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
                        arguments='{"city":"Edinburgh","country":"GB","units":"c"}',
                        name='GetWeatherArgs',
                        parsed_arguments=GetWeatherArgs(city='Edinburgh', country='GB', units='c')
                    ),
                    id='call_EEaIYq8aTdiDWro8jILNl3XK',
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
            '{"id": "chatcmpl-9tXjcnIvzZDXRfLfbVTPNL5963GWw", "object": "chat.completion", "created": 1723024744, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": null, "tool_calls": [{"id": "call_ECSuZ8gcNPPwgt24me91jHsJ", "type": "function", "function": {"name": "GetWeatherArgs", "arguments": "{\\"city\\": \\"Edinburgh\\", \\"country\\": \\"UK\\", \\"units\\": \\"c\\"}"}}, {"id": "call_Z3fM2sNBBGILhMtimk5Y3RQk", "type": "function", "function": {"name": "get_stock_price", "arguments": "{\\"ticker\\": \\"AAPL\\", \\"exchange\\": \\"NASDAQ\\"}"}}], "refusal": null}, "logprobs": null, "finish_reason": "tool_calls"}], "usage": {"prompt_tokens": 149, "completion_tokens": 60, "total_tokens": 209}, "system_fingerprint": "fp_845eaabc1f"}'
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
                        arguments='{"city": "Edinburgh", "country": "UK", "units": "c"}',
                        name='GetWeatherArgs',
                        parsed_arguments=GetWeatherArgs(city='Edinburgh', country='UK', units='c')
                    ),
                    id='call_ECSuZ8gcNPPwgt24me91jHsJ',
                    type='function'
                ),
                ParsedFunctionToolCall(
                    function=ParsedFunction(
                        arguments='{"ticker": "AAPL", "exchange": "NASDAQ"}',
                        name='get_stock_price',
                        parsed_arguments=GetStockPrice(exchange='NASDAQ', ticker='AAPL')
                    ),
                    id='call_Z3fM2sNBBGILhMtimk5Y3RQk',
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
            '{"id": "chatcmpl-9tXjfjETDIqeYvDjsuGACbwdY0xsr", "object": "chat.completion", "created": 1723024747, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": null, "tool_calls": [{"id": "call_7ZZPctBXQWexQlIHSrIHMVUq", "type": "function", "function": {"name": "get_weather", "arguments": "{\\"city\\":\\"San Francisco\\",\\"state\\":\\"CA\\"}"}}], "refusal": null}, "logprobs": null, "finish_reason": "tool_calls"}], "usage": {"prompt_tokens": 48, "completion_tokens": 19, "total_tokens": 67}, "system_fingerprint": "fp_2a322c9ffc"}'
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
                    id='call_7ZZPctBXQWexQlIHSrIHMVUq',
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
