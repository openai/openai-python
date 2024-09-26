from __future__ import annotations

import os
import json
from enum import Enum
from typing import Any, List, Callable, Optional, Awaitable
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
            '{"id": "chatcmpl-ABgIZhG0R51R94epwHjt5bgb83rz4", "object": "chat.completion", "created": 1727347567, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": "I\'m sorry, but I can\'t provide real-time weather updates. To find out the current weather in San Francisco, I recommend checking a reliable weather website or app.", "refusal": null}, "logprobs": null, "finish_reason": "stop"}], "usage": {"prompt_tokens": 14, "completion_tokens": 32, "total_tokens": 46, "completion_tokens_details": {"reasoning_tokens": 0}}, "system_fingerprint": "fp_7568d46099"}'
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
                content="I'm sorry, but I can't provide real-time weather updates. To find out the current weather in 
San Francisco, I recommend checking a reliable weather website or app.",
                function_call=None,
                parsed=None,
                refusal=None,
                role='assistant',
                tool_calls=[]
            )
        )
    ],
    created=1727347567,
    id='chatcmpl-ABgIZhG0R51R94epwHjt5bgb83rz4',
    model='gpt-4o-2024-08-06',
    object='chat.completion',
    service_tier=None,
    system_fingerprint='fp_7568d46099',
    usage=CompletionUsage(
        completion_tokens=32,
        completion_tokens_details=CompletionTokensDetails(reasoning_tokens=0),
        prompt_tokens=14,
        total_tokens=46
    )
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
            '{"id": "chatcmpl-ABgIaJhdAmzfDy7q3HCmK8jLHpja9", "object": "chat.completion", "created": 1727347568, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": "{\\"city\\":\\"San Francisco\\",\\"temperature\\":68,\\"units\\":\\"f\\"}", "refusal": null}, "logprobs": null, "finish_reason": "stop"}], "usage": {"prompt_tokens": 79, "completion_tokens": 14, "total_tokens": 93, "completion_tokens_details": {"reasoning_tokens": 0}}, "system_fingerprint": "fp_7568d46099"}'
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
                content='{"city":"San Francisco","temperature":68,"units":"f"}',
                function_call=None,
                parsed=Location(city='San Francisco', temperature=68.0, units='f'),
                refusal=None,
                role='assistant',
                tool_calls=[]
            )
        )
    ],
    created=1727347568,
    id='chatcmpl-ABgIaJhdAmzfDy7q3HCmK8jLHpja9',
    model='gpt-4o-2024-08-06',
    object='chat.completion',
    service_tier=None,
    system_fingerprint='fp_7568d46099',
    usage=CompletionUsage(
        completion_tokens=14,
        completion_tokens_details=CompletionTokensDetails(reasoning_tokens=0),
        prompt_tokens=79,
        total_tokens=93
    )
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
            '{"id": "chatcmpl-ABgIg6AynR6shXkfPUb2F0PQFA7f8", "object": "chat.completion", "created": 1727347574, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": "{\\"city\\":\\"San Francisco\\",\\"temperature\\":68,\\"units\\":\\"f\\"}", "refusal": null}, "logprobs": null, "finish_reason": "stop"}], "usage": {"prompt_tokens": 88, "completion_tokens": 14, "total_tokens": 102, "completion_tokens_details": {"reasoning_tokens": 0}}, "system_fingerprint": "fp_b40fb1c6fb"}'
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
                content='{"city":"San Francisco","temperature":68,"units":"f"}',
                function_call=None,
                parsed=Location(city='San Francisco', temperature=68.0, units='f'),
                refusal=None,
                role='assistant',
                tool_calls=[]
            )
        )
    ],
    created=1727347574,
    id='chatcmpl-ABgIg6AynR6shXkfPUb2F0PQFA7f8',
    model='gpt-4o-2024-08-06',
    object='chat.completion',
    service_tier=None,
    system_fingerprint='fp_b40fb1c6fb',
    usage=CompletionUsage(
        completion_tokens=14,
        completion_tokens_details=CompletionTokensDetails(reasoning_tokens=0),
        prompt_tokens=88,
        total_tokens=102
    )
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
            '{"id": "chatcmpl-ABgIhcpfJ6iawoLkZbJ7JDuTunZiy", "object": "chat.completion", "created": 1727347575, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": "{\\"color\\":\\"red\\",\\"hex_color_code\\":\\"#FF0000\\"}", "refusal": null}, "logprobs": null, "finish_reason": "stop"}], "usage": {"prompt_tokens": 109, "completion_tokens": 14, "total_tokens": 123, "completion_tokens_details": {"reasoning_tokens": 0}}, "system_fingerprint": "fp_5050236cbd"}'
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
            '{"id": "chatcmpl-ABgIht4RFnH9kv9s0zCqfRfVr2wjX", "object": "chat.completion", "created": 1727347575, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": "{\\"city\\":\\"San Francisco\\",\\"temperature\\":59,\\"units\\":\\"f\\"}", "refusal": null}, "logprobs": null, "finish_reason": "stop"}, {"index": 1, "message": {"role": "assistant", "content": "{\\"city\\":\\"San Francisco\\",\\"temperature\\":68,\\"units\\":\\"f\\"}", "refusal": null}, "logprobs": null, "finish_reason": "stop"}, {"index": 2, "message": {"role": "assistant", "content": "{\\"city\\":\\"San Francisco\\",\\"temperature\\":67,\\"units\\":\\"f\\"}", "refusal": null}, "logprobs": null, "finish_reason": "stop"}], "usage": {"prompt_tokens": 79, "completion_tokens": 42, "total_tokens": 121, "completion_tokens_details": {"reasoning_tokens": 0}}, "system_fingerprint": "fp_5050236cbd"}'
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
            content='{"city":"San Francisco","temperature":59,"units":"f"}',
            function_call=None,
            parsed=Location(city='San Francisco', temperature=59.0, units='f'),
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
            content='{"city":"San Francisco","temperature":68,"units":"f"}',
            function_call=None,
            parsed=Location(city='San Francisco', temperature=68.0, units='f'),
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
            content='{"city":"San Francisco","temperature":67,"units":"f"}',
            function_call=None,
            parsed=Location(city='San Francisco', temperature=67.0, units='f'),
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
            '{"id": "chatcmpl-ABgIiIO7LjsAsuZIzMtIdqzlCzSB4", "object": "chat.completion", "created": 1727347576, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": "{\\"name\\":\\"Science Fair\\",\\"date\\":\\"Friday\\",\\"participants\\":[\\"Alice\\",\\"Bob\\"]}", "refusal": null}, "logprobs": null, "finish_reason": "stop"}], "usage": {"prompt_tokens": 92, "completion_tokens": 17, "total_tokens": 109, "completion_tokens_details": {"reasoning_tokens": 0}}, "system_fingerprint": "fp_b40fb1c6fb"}'
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
    created=1727347576,
    id='chatcmpl-ABgIiIO7LjsAsuZIzMtIdqzlCzSB4',
    model='gpt-4o-2024-08-06',
    object='chat.completion',
    service_tier=None,
    system_fingerprint='fp_b40fb1c6fb',
    usage=CompletionUsage(
        completion_tokens=17,
        completion_tokens_details=CompletionTokensDetails(reasoning_tokens=0),
        prompt_tokens=92,
        total_tokens=109
    )
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
            '{"id": "chatcmpl-ABgIkOf7oA8OBGlO7YohLZHiKHJmJ", "object": "chat.completion", "created": 1727347578, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": null, "tool_calls": [{"id": "call_c8rJvUlGYId0FlVyVNvrWI3q", "type": "function", "function": {"name": "Query", "arguments": "{\\"name\\":\\"FulfilledButLateOrders\\",\\"table_name\\":\\"orders\\",\\"columns\\":[\\"id\\",\\"status\\",\\"expected_delivery_date\\",\\"delivered_at\\",\\"shipped_at\\",\\"ordered_at\\"],\\"conditions\\":[{\\"column\\":\\"ordered_at\\",\\"operator\\":\\">=\\",\\"value\\":\\"2022-05-01\\"},{\\"column\\":\\"ordered_at\\",\\"operator\\":\\"<\\",\\"value\\":\\"2022-06-01\\"},{\\"column\\":\\"status\\",\\"operator\\":\\"=\\",\\"value\\":\\"fulfilled\\"},{\\"column\\":\\"delivered_at\\",\\"operator\\":\\">\\",\\"value\\":{\\"column_name\\":\\"expected_delivery_date\\"}}],\\"order_by\\":\\"asc\\"}"}}], "refusal": null}, "logprobs": null, "finish_reason": "tool_calls"}], "usage": {"prompt_tokens": 512, "completion_tokens": 121, "total_tokens": 633, "completion_tokens_details": {"reasoning_tokens": 0}}, "system_fingerprint": "fp_143bb8492c"}'
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
                    arguments='{"name":"FulfilledButLateOrders","table_name":"orders","columns":["id","status","expected
_delivery_date","delivered_at","shipped_at","ordered_at"],"conditions":[{"column":"ordered_at","operator":">=","value":"
2022-05-01"},{"column":"ordered_at","operator":"<","value":"2022-06-01"},{"column":"status","operator":"=","value":"fulf
illed"},{"column":"delivered_at","operator":">","value":{"column_name":"expected_delivery_date"}}],"order_by":"asc"}',
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
                            Condition(column='ordered_at', operator=<Operator.lt: '<'>, value='2022-06-01'),
                            Condition(column='status', operator=<Operator.eq: '='>, value='fulfilled'),
                            Condition(
                                column='delivered_at',
                                operator=<Operator.gt: '>'>,
                                value=DynamicValue(column_name='expected_delivery_date')
                            )
                        ],
                        name='FulfilledButLateOrders',
                        order_by=<OrderBy.asc: 'asc'>,
                        table_name=<Table.orders: 'orders'>
                    )
                ),
                id='call_c8rJvUlGYId0FlVyVNvrWI3q',
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
                '{"id": "chatcmpl-ABgIqaylwQNDVZAHe5lDKk0Ax7YS7", "object": "chat.completion", "created": 1727347584, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": "{\\"", "refusal": null}, "logprobs": null, "finish_reason": "length"}], "usage": {"prompt_tokens": 79, "completion_tokens": 1, "total_tokens": 80, "completion_tokens_details": {"reasoning_tokens": 0}}, "system_fingerprint": "fp_7568d46099"}'
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
            '{"id": "chatcmpl-ABgIq8R3DWxhOWoorrE8RgxJTPkYS", "object": "chat.completion", "created": 1727347584, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": null, "refusal": "I\'m sorry, but I can\'t assist with that request."}, "logprobs": null, "finish_reason": "stop"}], "usage": {"prompt_tokens": 79, "completion_tokens": 12, "total_tokens": 91, "completion_tokens_details": {"reasoning_tokens": 0}}, "system_fingerprint": "fp_5050236cbd"}'
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
            refusal="I'm sorry, but I can't assist with that request.",
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
            '{"id": "chatcmpl-ABgIrdZCy0ozC9KtEz7S1ZnTOSCjg", "object": "chat.completion", "created": 1727347585, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": null, "tool_calls": [{"id": "call_XTnBuYWrgBj4X6EAx18u2DMx", "type": "function", "function": {"name": "GetWeatherArgs", "arguments": "{\\"city\\":\\"Edinburgh\\",\\"country\\":\\"United Kingdom\\",\\"units\\":\\"c\\"}"}}], "refusal": null}, "logprobs": null, "finish_reason": "tool_calls"}], "usage": {"prompt_tokens": 76, "completion_tokens": 25, "total_tokens": 101, "completion_tokens_details": {"reasoning_tokens": 0}}, "system_fingerprint": "fp_b40fb1c6fb"}'
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
                        arguments='{"city":"Edinburgh","country":"United Kingdom","units":"c"}',
                        name='GetWeatherArgs',
                        parsed_arguments=GetWeatherArgs(city='Edinburgh', country='United Kingdom', units='c')
                    ),
                    id='call_XTnBuYWrgBj4X6EAx18u2DMx',
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
            '{"id": "chatcmpl-ABgIyhXFTmHutycKlMLZwNDlB9R8B", "object": "chat.completion", "created": 1727347592, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": null, "tool_calls": [{"id": "call_XcVkrO33vBQCOhx224TKi4NW", "type": "function", "function": {"name": "GetWeatherArgs", "arguments": "{\\"city\\": \\"Edinburgh\\", \\"country\\": \\"UK\\", \\"units\\": \\"c\\"}"}}, {"id": "call_bf4aX8l8QAARQPdaE6HOpzG0", "type": "function", "function": {"name": "get_stock_price", "arguments": "{\\"ticker\\": \\"AAPL\\", \\"exchange\\": \\"NASDAQ\\"}"}}], "refusal": null}, "logprobs": null, "finish_reason": "tool_calls"}], "usage": {"prompt_tokens": 149, "completion_tokens": 60, "total_tokens": 209, "completion_tokens_details": {"reasoning_tokens": 0}}, "system_fingerprint": "fp_5050236cbd"}'
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
                    id='call_XcVkrO33vBQCOhx224TKi4NW',
                    type='function'
                ),
                ParsedFunctionToolCall(
                    function=ParsedFunction(
                        arguments='{"ticker": "AAPL", "exchange": "NASDAQ"}',
                        name='get_stock_price',
                        parsed_arguments=GetStockPrice(exchange='NASDAQ', ticker='AAPL')
                    ),
                    id='call_bf4aX8l8QAARQPdaE6HOpzG0',
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
            '{"id": "chatcmpl-ABgIzSBJWifrpLSLto62LgecRNEVy", "object": "chat.completion", "created": 1727347593, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": null, "tool_calls": [{"id": "call_KDRFFW5ivLsEC3mxFJH8jpfA", "type": "function", "function": {"name": "get_weather", "arguments": "{\\"city\\":\\"San Francisco\\",\\"state\\":\\"CA\\"}"}}], "refusal": null}, "logprobs": null, "finish_reason": "tool_calls"}], "usage": {"prompt_tokens": 48, "completion_tokens": 19, "total_tokens": 67, "completion_tokens_details": {"reasoning_tokens": 0}}, "system_fingerprint": "fp_5050236cbd"}'
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
                    id='call_KDRFFW5ivLsEC3mxFJH8jpfA',
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


@pytest.mark.respx(base_url=base_url)
def test_parse_pydantic_raw_response(client: OpenAI, respx_mock: MockRouter, monkeypatch: pytest.MonkeyPatch) -> None:
    class Location(BaseModel):
        city: str
        temperature: float
        units: Literal["c", "f"]

    response = _make_snapshot_request(
        lambda c: c.beta.chat.completions.with_raw_response.parse(
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
            '{"id": "chatcmpl-ABgJ0eZEWD1qADq9WVMnR9UbKDWya", "object": "chat.completion", "created": 1727347594, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": "{\\"city\\":\\"San Francisco\\",\\"temperature\\":63,\\"units\\":\\"f\\"}", "refusal": null}, "logprobs": null, "finish_reason": "stop"}], "usage": {"prompt_tokens": 79, "completion_tokens": 14, "total_tokens": 93, "completion_tokens_details": {"reasoning_tokens": 0}}, "system_fingerprint": "fp_7568d46099"}'
        ),
        mock_client=client,
        respx_mock=respx_mock,
    )
    assert response.http_request.headers.get("x-stainless-helper-method") == "beta.chat.completions.parse"

    completion = response.parse()
    message = completion.choices[0].message
    assert message.parsed is not None
    assert isinstance(message.parsed.city, str)
    assert print_obj(completion, monkeypatch) == snapshot(
        """\
ParsedChatCompletion[Location](
    choices=[
        ParsedChoice[Location](
            finish_reason='stop',
            index=0,
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
    ],
    created=1727347594,
    id='chatcmpl-ABgJ0eZEWD1qADq9WVMnR9UbKDWya',
    model='gpt-4o-2024-08-06',
    object='chat.completion',
    service_tier=None,
    system_fingerprint='fp_7568d46099',
    usage=CompletionUsage(
        completion_tokens=14,
        completion_tokens_details=CompletionTokensDetails(reasoning_tokens=0),
        prompt_tokens=79,
        total_tokens=93
    )
)
"""
    )


@pytest.mark.respx(base_url=base_url)
@pytest.mark.asyncio
async def test_async_parse_pydantic_raw_response(
    async_client: AsyncOpenAI, respx_mock: MockRouter, monkeypatch: pytest.MonkeyPatch
) -> None:
    class Location(BaseModel):
        city: str
        temperature: float
        units: Literal["c", "f"]

    response = await _make_async_snapshot_request(
        lambda c: c.beta.chat.completions.with_raw_response.parse(
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
            '{"id": "chatcmpl-ABgJ3taZMsRGuUqeKOrm9k6Koja9q", "object": "chat.completion", "created": 1727347597, "model": "gpt-4o-2024-08-06", "choices": [{"index": 0, "message": {"role": "assistant", "content": "{\\"city\\":\\"San Francisco\\",\\"temperature\\":14,\\"units\\":\\"c\\"}", "refusal": null}, "logprobs": null, "finish_reason": "stop"}], "usage": {"prompt_tokens": 79, "completion_tokens": 14, "total_tokens": 93, "completion_tokens_details": {"reasoning_tokens": 0}}, "system_fingerprint": "fp_5050236cbd"}'
        ),
        mock_client=async_client,
        respx_mock=respx_mock,
    )
    assert response.http_request.headers.get("x-stainless-helper-method") == "beta.chat.completions.parse"

    completion = response.parse()
    message = completion.choices[0].message
    assert message.parsed is not None
    assert isinstance(message.parsed.city, str)
    assert print_obj(completion, monkeypatch) == snapshot(
        """\
ParsedChatCompletion[Location](
    choices=[
        ParsedChoice[Location](
            finish_reason='stop',
            index=0,
            logprobs=None,
            message=ParsedChatCompletionMessage[Location](
                content='{"city":"San Francisco","temperature":14,"units":"c"}',
                function_call=None,
                parsed=Location(city='San Francisco', temperature=14.0, units='c'),
                refusal=None,
                role='assistant',
                tool_calls=[]
            )
        )
    ],
    created=1727347597,
    id='chatcmpl-ABgJ3taZMsRGuUqeKOrm9k6Koja9q',
    model='gpt-4o-2024-08-06',
    object='chat.completion',
    service_tier=None,
    system_fingerprint='fp_5050236cbd',
    usage=CompletionUsage(
        completion_tokens=14,
        completion_tokens_details=CompletionTokensDetails(reasoning_tokens=0),
        prompt_tokens=79,
        total_tokens=93
    )
)
"""
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


async def _make_async_snapshot_request(
    func: Callable[[AsyncOpenAI], Awaitable[_T]],
    *,
    content_snapshot: Any,
    respx_mock: MockRouter,
    mock_client: AsyncOpenAI,
) -> _T:
    live = os.environ.get("OPENAI_LIVE") == "1"
    if live:

        async def _on_response(response: httpx.Response) -> None:
            # update the content snapshot
            assert json.dumps(json.loads(await response.aread())) == content_snapshot

        respx_mock.stop()

        client = AsyncOpenAI(
            http_client=httpx.AsyncClient(
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

    result = await func(client)

    if live:
        await client.close()

    return result
