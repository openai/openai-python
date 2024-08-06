from __future__ import annotations

import os
from typing import Any, Generic, Callable, Iterator, cast, overload
from typing_extensions import Literal, TypeVar

import rich
import httpx
import pytest
from respx import MockRouter
from pydantic import BaseModel
from inline_snapshot import external, snapshot, outsource

import openai
from openai import OpenAI, AsyncOpenAI
from openai._utils import assert_signatures_in_sync
from openai._compat import model_copy
from openai.lib.streaming.chat import (
    ContentDoneEvent,
    ChatCompletionStream,
    ChatCompletionStreamEvent,
    ChatCompletionStreamManager,
    ParsedChatCompletionSnapshot,
)
from openai.lib._parsing._completions import ResponseFormatT

from ._utils import print_obj
from ...conftest import base_url

_T = TypeVar("_T")

# all the snapshots in this file are auto-generated from the live API
#
# you can update them with
#
# `OPENAI_LIVE=1 pytest --inline-snapshot=fix`


@pytest.mark.respx(base_url=base_url)
def test_parse_nothing(client: OpenAI, respx_mock: MockRouter, monkeypatch: pytest.MonkeyPatch) -> None:
    listener = _make_stream_snapshot_request(
        lambda c: c.beta.chat.completions.stream(
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "user",
                    "content": "What's the weather like in SF?",
                },
            ],
        ),
        content_snapshot=snapshot(external("b9d6bee9f9b8*.bin")),
        mock_client=client,
        respx_mock=respx_mock,
    )

    assert print_obj(listener.stream.get_final_completion().choices, monkeypatch) == snapshot(
        """\
[
    ParsedChoice[NoneType](
        finish_reason='stop',
        index=0,
        logprobs=None,
        message=ParsedChatCompletionMessage[NoneType](
            content="I'm unable to provide real-time weather updates. To get the latest weather information for San 
Francisco, I recommend checking a reliable weather website or using a weather app.",
            function_call=None,
            parsed=None,
            refusal=None,
            role='assistant',
            tool_calls=[]
        )
    )
]
"""
    )
    assert print_obj(listener.get_event_by_type("content.done"), monkeypatch) == snapshot(
        """\
ContentDoneEvent[NoneType](
    content="I'm unable to provide real-time weather updates. To get the latest weather information for San Francisco, I
recommend checking a reliable weather website or using a weather app.",
    parsed=None,
    type='content.done'
)
"""
    )


@pytest.mark.respx(base_url=base_url)
def test_parse_pydantic_model(client: OpenAI, respx_mock: MockRouter, monkeypatch: pytest.MonkeyPatch) -> None:
    class Location(BaseModel):
        city: str
        temperature: float
        units: Literal["c", "f"]

    done_snapshots: list[ParsedChatCompletionSnapshot] = []

    def on_event(stream: ChatCompletionStream[Location], event: ChatCompletionStreamEvent[Location]) -> None:
        if event.type == "content.done":
            done_snapshots.append(model_copy(stream.current_completion_snapshot, deep=True))

    listener = _make_stream_snapshot_request(
        lambda c: c.beta.chat.completions.stream(
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "user",
                    "content": "What's the weather like in SF?",
                },
            ],
            response_format=Location,
        ),
        content_snapshot=snapshot(external("ea9a417d533b*.bin")),
        mock_client=client,
        respx_mock=respx_mock,
        on_event=on_event,
    )

    assert len(done_snapshots) == 1
    assert isinstance(done_snapshots[0].choices[0].message.parsed, Location)

    for event in reversed(listener.events):
        if event.type == "content.delta":
            data = cast(Any, event.parsed)
            assert isinstance(data["city"], str), data
            assert isinstance(data["temperature"], (int, float)), data
            assert isinstance(data["units"], str), data
            break
    else:
        rich.print(listener.events)
        raise AssertionError("Did not find a `content.delta` event")

    assert print_obj(listener.stream.get_final_completion(), monkeypatch) == snapshot(
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
    created=1722934250,
    id='chatcmpl-9tAC2Fr44W8e4GakwKuKSSsFPhISv',
    model='gpt-4o-so',
    object='chat.completion',
    service_tier=None,
    system_fingerprint='fp_e1a05a1dce',
    usage=CompletionUsage(completion_tokens=14, prompt_tokens=17, total_tokens=31)
)
"""
    )
    assert print_obj(listener.get_event_by_type("content.done"), monkeypatch) == snapshot(
        """\
ContentDoneEvent[Location](
    content='{"city":"San Francisco","temperature":63,"units":"f"}',
    parsed=Location(city='San Francisco', temperature=63.0, units='f'),
    type='content.done'
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

    listener = _make_stream_snapshot_request(
        lambda c: c.beta.chat.completions.stream(
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
        content_snapshot=snapshot(external("1437bd06a9d5*.bin")),
        mock_client=client,
        respx_mock=respx_mock,
    )

    assert [e.type for e in listener.events] == snapshot(
        [
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.delta",
            "chunk",
            "content.done",
            "chunk",
            "content.done",
            "chunk",
            "content.done",
            "chunk",
        ]
    )
    assert print_obj(listener.stream.get_final_completion().choices, monkeypatch) == snapshot(
        """\
[
    ParsedChoice[Location](
        finish_reason='stop',
        index=0,
        logprobs=None,
        message=ParsedChatCompletionMessage[Location](
            content='{"city":"San Francisco","temperature":64,"units":"f"}',
            function_call=None,
            parsed=Location(city='San Francisco', temperature=64.0, units='f'),
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
            content='{"city":"San Francisco","temperature":64,"units":"f"}',
            function_call=None,
            parsed=Location(city='San Francisco', temperature=64.0, units='f'),
            refusal=None,
            role='assistant',
            tool_calls=[]
        )
    )
]
"""
    )


@pytest.mark.respx(base_url=base_url)
def test_parse_max_tokens_reached(client: OpenAI, respx_mock: MockRouter) -> None:
    class Location(BaseModel):
        city: str
        temperature: float
        units: Literal["c", "f"]

    with pytest.raises(openai.LengthFinishReasonError):
        _make_stream_snapshot_request(
            lambda c: c.beta.chat.completions.stream(
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
            content_snapshot=snapshot(external("7ae6c1a2631b*.bin")),
            mock_client=client,
            respx_mock=respx_mock,
        )


@pytest.mark.respx(base_url=base_url)
def test_parse_pydantic_model_refusal(client: OpenAI, respx_mock: MockRouter, monkeypatch: pytest.MonkeyPatch) -> None:
    class Location(BaseModel):
        city: str
        temperature: float
        units: Literal["c", "f"]

    listener = _make_stream_snapshot_request(
        lambda c: c.beta.chat.completions.stream(
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "user",
                    "content": "How do I make anthrax?",
                },
            ],
            response_format=Location,
        ),
        content_snapshot=snapshot(external("d79326933c15*.bin")),
        mock_client=client,
        respx_mock=respx_mock,
    )

    assert print_obj(listener.get_event_by_type("refusal.done"), monkeypatch) == snapshot("""\
RefusalDoneEvent(refusal="I'm very sorry, but I can't assist with that request.", type='refusal.done')
""")

    assert print_obj(listener.stream.get_final_completion().choices, monkeypatch) == snapshot(
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
def test_content_logprobs_events(client: OpenAI, respx_mock: MockRouter, monkeypatch: pytest.MonkeyPatch) -> None:
    listener = _make_stream_snapshot_request(
        lambda c: c.beta.chat.completions.stream(
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "user",
                    "content": "Say foo",
                },
            ],
            logprobs=True,
        ),
        content_snapshot=snapshot(external("70c7df71ce72*.bin")),
        mock_client=client,
        respx_mock=respx_mock,
    )

    assert print_obj([e for e in listener.events if e.type.startswith("logprobs")], monkeypatch) == snapshot("""\
[
    LogprobsContentDeltaEvent(
        content=[ChatCompletionTokenLogprob(bytes=[70, 111, 111], logprob=-0.006764991, token='Foo', top_logprobs=[])],
        snapshot=[
            ChatCompletionTokenLogprob(bytes=[70, 111, 111], logprob=-0.006764991, token='Foo', top_logprobs=[])
        ],
        type='logprobs.content.delta'
    ),
    LogprobsContentDeltaEvent(
        content=[ChatCompletionTokenLogprob(bytes=[33], logprob=-0.31380808, token='!', top_logprobs=[])],
        snapshot=[
            ChatCompletionTokenLogprob(bytes=[70, 111, 111], logprob=-0.006764991, token='Foo', top_logprobs=[]),
            ChatCompletionTokenLogprob(bytes=[33], logprob=-0.31380808, token='!', top_logprobs=[])
        ],
        type='logprobs.content.delta'
    ),
    LogprobsContentDoneEvent(
        content=[
            ChatCompletionTokenLogprob(bytes=[70, 111, 111], logprob=-0.006764991, token='Foo', top_logprobs=[]),
            ChatCompletionTokenLogprob(bytes=[33], logprob=-0.31380808, token='!', top_logprobs=[])
        ],
        type='logprobs.content.done'
    )
]
""")

    assert print_obj(listener.stream.get_final_completion().choices, monkeypatch) == snapshot("""\
[
    ParsedChoice[NoneType](
        finish_reason='stop',
        index=0,
        logprobs=ChoiceLogprobs(
            content=[
                ChatCompletionTokenLogprob(bytes=[70, 111, 111], logprob=-0.006764991, token='Foo', top_logprobs=[]),
                ChatCompletionTokenLogprob(bytes=[33], logprob=-0.31380808, token='!', top_logprobs=[])
            ],
            refusal=None
        ),
        message=ParsedChatCompletionMessage[NoneType](
            content='Foo!',
            function_call=None,
            parsed=None,
            refusal=None,
            role='assistant',
            tool_calls=[]
        )
    )
]
""")


@pytest.mark.respx(base_url=base_url)
def test_refusal_logprobs_events(client: OpenAI, respx_mock: MockRouter, monkeypatch: pytest.MonkeyPatch) -> None:
    class Location(BaseModel):
        city: str
        temperature: float
        units: Literal["c", "f"]

    listener = _make_stream_snapshot_request(
        lambda c: c.beta.chat.completions.stream(
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "user",
                    "content": "How do I make anthrax?",
                },
            ],
            logprobs=True,
            response_format=Location,
        ),
        content_snapshot=snapshot(external("cb77dc69b6c8*.bin")),
        mock_client=client,
        respx_mock=respx_mock,
    )

    assert print_obj([e.type for e in listener.events if e.type.startswith("logprobs")], monkeypatch) == snapshot("""\
[
    'logprobs.refusal.delta',
    'logprobs.refusal.delta',
    'logprobs.refusal.delta',
    'logprobs.refusal.delta',
    'logprobs.refusal.delta',
    'logprobs.refusal.delta',
    'logprobs.refusal.delta',
    'logprobs.refusal.delta',
    'logprobs.refusal.delta',
    'logprobs.refusal.delta',
    'logprobs.refusal.delta',
    'logprobs.refusal.done'
]
""")

    assert print_obj(listener.stream.get_final_completion().choices, monkeypatch) == snapshot("""\
[
    ParsedChoice[Location](
        finish_reason='stop',
        index=0,
        logprobs=ChoiceLogprobs(
            content=None,
            refusal=[
                ChatCompletionTokenLogprob(bytes=[73, 39, 109], logprob=-0.0010472201, token="I'm", top_logprobs=[]),
                ChatCompletionTokenLogprob(
                    bytes=[32, 118, 101, 114, 121],
                    logprob=-0.7292482,
                    token=' very',
                    top_logprobs=[]
                ),
                ChatCompletionTokenLogprob(
                    bytes=[32, 115, 111, 114, 114, 121],
                    logprob=-5.080963e-06,
                    token=' sorry',
                    top_logprobs=[]
                ),
                ChatCompletionTokenLogprob(bytes=[44], logprob=-4.048445e-05, token=',', top_logprobs=[]),
                ChatCompletionTokenLogprob(
                    bytes=[32, 98, 117, 116],
                    logprob=-0.038046427,
                    token=' but',
                    top_logprobs=[]
                ),
                ChatCompletionTokenLogprob(bytes=[32, 73], logprob=-0.0019351852, token=' I', top_logprobs=[]),
                ChatCompletionTokenLogprob(
                    bytes=[32, 99, 97, 110, 39, 116],
                    logprob=-0.008995773,
                    token=" can't",
                    top_logprobs=[]
                ),
                ChatCompletionTokenLogprob(
                    bytes=[32, 97, 115, 115, 105, 115, 116],
                    logprob=-0.0033510819,
                    token=' assist',
                    top_logprobs=[]
                ),
                ChatCompletionTokenLogprob(
                    bytes=[32, 119, 105, 116, 104],
                    logprob=-0.0036033941,
                    token=' with',
                    top_logprobs=[]
                ),
                ChatCompletionTokenLogprob(
                    bytes=[32, 116, 104, 97, 116],
                    logprob=-0.0015974608,
                    token=' that',
                    top_logprobs=[]
                ),
                ChatCompletionTokenLogprob(bytes=[46], logprob=-0.6339823, token='.', top_logprobs=[])
            ]
        ),
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
""")


@pytest.mark.respx(base_url=base_url)
def test_parse_pydantic_tool(client: OpenAI, respx_mock: MockRouter, monkeypatch: pytest.MonkeyPatch) -> None:
    class GetWeatherArgs(BaseModel):
        city: str
        country: str
        units: Literal["c", "f"] = "c"

    listener = _make_stream_snapshot_request(
        lambda c: c.beta.chat.completions.stream(
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
        content_snapshot=snapshot(external("ae070a447e1d*.bin")),
        mock_client=client,
        respx_mock=respx_mock,
    )

    assert print_obj(listener.stream.current_completion_snapshot.choices, monkeypatch) == snapshot(
        """\
[
    ParsedChoice[object](
        finish_reason='tool_calls',
        index=0,
        logprobs=None,
        message=ParsedChatCompletionMessage[object](
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
                    id='call_Vz6ZXciy6Y0PYfT4d9W7fYB4',
                    index=0,
                    type='function'
                )
            ]
        )
    )
]
"""
    )

    assert print_obj(listener.stream.get_final_completion().choices, monkeypatch) == snapshot(
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
                    id='call_Vz6ZXciy6Y0PYfT4d9W7fYB4',
                    index=0,
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

    listener = _make_stream_snapshot_request(
        lambda c: c.beta.chat.completions.stream(
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
        content_snapshot=snapshot(external("a346213bec7a*.bin")),
        mock_client=client,
        respx_mock=respx_mock,
    )

    assert print_obj(listener.stream.current_completion_snapshot.choices, monkeypatch) == snapshot(
        """\
[
    ParsedChoice[object](
        finish_reason='tool_calls',
        index=0,
        logprobs=None,
        message=ParsedChatCompletionMessage[object](
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
                    id='call_g4Q1vRbE0CaHGOs5if8mHsBq',
                    index=0,
                    type='function'
                ),
                ParsedFunctionToolCall(
                    function=ParsedFunction(
                        arguments='{"ticker": "AAPL", "exchange": "NASDAQ"}',
                        name='get_stock_price',
                        parsed_arguments=GetStockPrice(exchange='NASDAQ', ticker='AAPL')
                    ),
                    id='call_gWj3HQxZEHnFvyJLEHIiJKBV',
                    index=1,
                    type='function'
                )
            ]
        )
    )
]
"""
    )
    completion = listener.stream.get_final_completion()
    assert print_obj(completion.choices[0].message.tool_calls, monkeypatch) == snapshot(
        """\
[
    ParsedFunctionToolCall(
        function=ParsedFunction(
            arguments='{"city": "Edinburgh", "country": "UK", "units": "c"}',
            name='GetWeatherArgs',
            parsed_arguments=GetWeatherArgs(city='Edinburgh', country='UK', units='c')
        ),
        id='call_g4Q1vRbE0CaHGOs5if8mHsBq',
        index=0,
        type='function'
    ),
    ParsedFunctionToolCall(
        function=ParsedFunction(
            arguments='{"ticker": "AAPL", "exchange": "NASDAQ"}',
            name='get_stock_price',
            parsed_arguments=GetStockPrice(exchange='NASDAQ', ticker='AAPL')
        ),
        id='call_gWj3HQxZEHnFvyJLEHIiJKBV',
        index=1,
        type='function'
    )
]
"""
    )


@pytest.mark.respx(base_url=base_url)
def test_parse_strict_tools(client: OpenAI, respx_mock: MockRouter, monkeypatch: pytest.MonkeyPatch) -> None:
    listener = _make_stream_snapshot_request(
        lambda c: c.beta.chat.completions.stream(
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
        content_snapshot=snapshot(external("a7097cae6a1f*.bin")),
        mock_client=client,
        respx_mock=respx_mock,
    )

    assert print_obj(listener.stream.current_completion_snapshot.choices, monkeypatch) == snapshot(
        """\
[
    ParsedChoice[object](
        finish_reason='tool_calls',
        index=0,
        logprobs=None,
        message=ParsedChatCompletionMessage[object](
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
                    id='call_rQe3kzGnTr2epjx8HREg3F2a',
                    index=0,
                    type='function'
                )
            ]
        )
    )
]
"""
    )


@pytest.mark.respx(base_url=base_url)
def test_non_pydantic_response_format(client: OpenAI, respx_mock: MockRouter, monkeypatch: pytest.MonkeyPatch) -> None:
    listener = _make_stream_snapshot_request(
        lambda c: c.beta.chat.completions.stream(
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "user",
                    "content": "What's the weather like in SF? Give me any JSON back",
                },
            ],
            response_format={"type": "json_object"},
        ),
        content_snapshot=snapshot(external("3e0df46f250d*.bin")),
        mock_client=client,
        respx_mock=respx_mock,
    )

    assert print_obj(listener.stream.get_final_completion().choices, monkeypatch) == snapshot(
        """\
[
    ParsedChoice[NoneType](
        finish_reason='stop',
        index=0,
        logprobs=None,
        message=ParsedChatCompletionMessage[NoneType](
            content='{\\n  "location": "San Francisco, CA",\\n  "temperature": "N/A",\\n  "conditions": "N/A",\\n  
"humidity": "N/A",\\n  "wind_speed": "N/A",\\n  "timestamp": "N/A",\\n  "note": "Real-time weather data is not available. 
Please check a reliable weather service for the most up-to-date information on San Francisco\\'s weather conditions."}',
            function_call=None,
            parsed=None,
            refusal=None,
            role='assistant',
            tool_calls=[]
        )
    )
]
"""
    )


@pytest.mark.respx(base_url=base_url)
def test_allows_non_strict_tools_but_no_parsing(
    client: OpenAI, respx_mock: MockRouter, monkeypatch: pytest.MonkeyPatch
) -> None:
    listener = _make_stream_snapshot_request(
        lambda c: c.beta.chat.completions.stream(
            model="gpt-4o-2024-08-06",
            messages=[{"role": "user", "content": "what's the weather in NYC?"}],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "parameters": {"type": "object", "properties": {"city": {"type": "string"}}},
                    },
                }
            ],
        ),
        content_snapshot=snapshot(external("fb75060ede89*.bin")),
        mock_client=client,
        respx_mock=respx_mock,
    )

    assert print_obj(listener.get_event_by_type("tool_calls.function.arguments.done"), monkeypatch) == snapshot("""\
FunctionToolCallArgumentsDoneEvent(
    arguments='{"city":"New York City"}',
    index=0,
    name='get_weather',
    parsed_arguments=None,
    type='tool_calls.function.arguments.done'
)
""")

    assert print_obj(listener.stream.get_final_completion().choices, monkeypatch) == snapshot(
        """\
[
    ParsedChoice[NoneType](
        finish_reason='stop',
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
                        arguments='{"city":"New York City"}',
                        name='get_weather',
                        parsed_arguments=None
                    ),
                    id='call_9rqjEc1DQRADTYGVV45LbZwL',
                    index=0,
                    type='function'
                )
            ]
        )
    )
]
"""
    )


@pytest.mark.parametrize("sync", [True, False], ids=["sync", "async"])
def test_stream_method_in_sync(sync: bool, client: OpenAI, async_client: AsyncOpenAI) -> None:
    checking_client: OpenAI | AsyncOpenAI = client if sync else async_client

    assert_signatures_in_sync(
        checking_client.chat.completions.create,
        checking_client.beta.chat.completions.stream,
        exclude_params={"response_format", "stream"},
    )


class StreamListener(Generic[ResponseFormatT]):
    def __init__(self, stream: ChatCompletionStream[ResponseFormatT]) -> None:
        self.stream = stream
        self.events: list[ChatCompletionStreamEvent[ResponseFormatT]] = []

    def __iter__(self) -> Iterator[ChatCompletionStreamEvent[ResponseFormatT]]:
        for event in self.stream:
            self.events.append(event)
            yield event

    @overload
    def get_event_by_type(self, event_type: Literal["content.done"]) -> ContentDoneEvent[ResponseFormatT] | None: ...

    @overload
    def get_event_by_type(self, event_type: str) -> ChatCompletionStreamEvent[ResponseFormatT] | None: ...

    def get_event_by_type(self, event_type: str) -> ChatCompletionStreamEvent[ResponseFormatT] | None:
        return next((e for e in self.events if e.type == event_type), None)


def _make_stream_snapshot_request(
    func: Callable[[OpenAI], ChatCompletionStreamManager[ResponseFormatT]],
    *,
    content_snapshot: Any,
    respx_mock: MockRouter,
    mock_client: OpenAI,
    on_event: Callable[[ChatCompletionStream[ResponseFormatT], ChatCompletionStreamEvent[ResponseFormatT]], Any]
    | None = None,
) -> StreamListener[ResponseFormatT]:
    live = os.environ.get("OPENAI_LIVE") == "1"
    if live:

        def _on_response(response: httpx.Response) -> None:
            # update the content snapshot
            assert outsource(response.read()) == content_snapshot

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
                content=content_snapshot._old_value._load_value(),
                headers={"content-type": "text/event-stream"},
            )
        )

        client = mock_client

    with func(client) as stream:
        listener = StreamListener(stream)

        for event in listener:
            if on_event:
                on_event(stream, event)

    if live:
        client.close()

    return listener
