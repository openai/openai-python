"""Public type-checker witnesses; these functions do not open live connections."""

from typing_extensions import assert_type

from openai import OpenAI, AsyncOpenAI
from openai.types.responses import Response
from openai.lib.responses_websocket import (
    ResponsesWebSocketLane,
    ResponsesWebSocketLimits,
    ResponsesWebSocketSession,
    AsyncResponsesWebSocketLane,
    ResponsesWebSocketAccumulator,
    AsyncResponsesWebSocketSession,
)
from openai.types.beta.beta_response import BetaResponse
from openai.resources.responses.responses import ResponsesConnection, AsyncResponsesConnection
from openai.resources.beta.responses.responses import (
    ResponsesConnection as BetaResponsesConnection,
    AsyncResponsesConnection as AsyncBetaResponsesConnection,
)
from openai.types.beta.beta_responses_client_event import ResponseCreate as BetaResponseCreate
from openai.types.beta.beta_responses_server_event import BetaResponsesServerEvent
from openai.types.responses.responses_server_event import ResponsesServerEvent


def stable_sync(client: OpenAI, limits: ResponsesWebSocketLimits) -> None:
    with client.responses.connect() as connection:
        with ResponsesWebSocketSession(connection, limits=limits) as session:
            lane = session.lane("stable")
            assert_type(session, ResponsesWebSocketSession[ResponsesConnection])
            assert_type(lane, ResponsesWebSocketLane[ResponsesConnection])
            lane.send({"type": "response.create"})
            assert_type(lane.recv(), ResponsesServerEvent)
            assert_type(lane.get_final_response(), Response)
            accumulator = ResponsesWebSocketAccumulator()
            accumulator.add_event(lane.recv())
            assert_type(accumulator.get_final_response(), Response)


def beta_sync(client: OpenAI, limits: ResponsesWebSocketLimits) -> None:
    with client.beta.responses.connect() as connection:
        with ResponsesWebSocketSession(connection, limits=limits) as session:
            assert_type(session, ResponsesWebSocketSession[BetaResponsesConnection])
            assert_type(session.default, ResponsesWebSocketLane[BetaResponsesConnection])
            lane = session.lane("beta")
            assert_type(lane, ResponsesWebSocketLane[BetaResponsesConnection])
            explicit_lane: ResponsesWebSocketLane[BetaResponsesConnection] = lane
            assert_type(explicit_lane, ResponsesWebSocketLane[BetaResponsesConnection])
            lane.send(BetaResponseCreate(type="response.create"))
            lane.send({"type": "response.create"})
            assert_type(lane.recv(), BetaResponsesServerEvent)
            assert_type(lane.get_final_response(), BetaResponse)
            accumulator = ResponsesWebSocketAccumulator(response_type=BetaResponse)
            accumulator.add_event(lane.recv())
            assert_type(accumulator.get_final_response(), BetaResponse)
            explicit: ResponsesWebSocketAccumulator[BetaResponse] = ResponsesWebSocketAccumulator(
                response_type=BetaResponse
            )
            explicit.add_event(lane.recv())
            assert_type(explicit.get_final_response(), BetaResponse)


async def stable_async(client: AsyncOpenAI, limits: ResponsesWebSocketLimits) -> None:
    async with client.responses.connect() as connection:
        async with AsyncResponsesWebSocketSession(connection, limits=limits) as session:
            assert_type(session, AsyncResponsesWebSocketSession[AsyncResponsesConnection])
            lane = session.lane("stable")
            assert_type(lane, AsyncResponsesWebSocketLane[AsyncResponsesConnection])
            await lane.send({"type": "response.create"})
            assert_type(await lane.recv(), ResponsesServerEvent)
            assert_type(await lane.get_final_response(), Response)
            accumulator = ResponsesWebSocketAccumulator()
            accumulator.add_event(await lane.recv())
            assert_type(accumulator.get_final_response(), Response)


async def beta_async(client: AsyncOpenAI, limits: ResponsesWebSocketLimits) -> None:
    async with client.beta.responses.connect() as connection:
        async with AsyncResponsesWebSocketSession(connection, limits=limits) as session:
            assert_type(session, AsyncResponsesWebSocketSession[AsyncBetaResponsesConnection])
            assert_type(session.default, AsyncResponsesWebSocketLane[AsyncBetaResponsesConnection])
            lane = session.lane("beta")
            assert_type(lane, AsyncResponsesWebSocketLane[AsyncBetaResponsesConnection])
            explicit_lane: AsyncResponsesWebSocketLane[AsyncBetaResponsesConnection] = lane
            assert_type(explicit_lane, AsyncResponsesWebSocketLane[AsyncBetaResponsesConnection])
            await lane.send(BetaResponseCreate(type="response.create"))
            assert_type(await lane.recv(), BetaResponsesServerEvent)
            assert_type(await lane.get_final_response(), BetaResponse)
            accumulator = ResponsesWebSocketAccumulator(response_type=BetaResponse)
            accumulator.add_event(await lane.recv())
            assert_type(accumulator.get_final_response(), BetaResponse)


def caller_fed_stable(connection: ResponsesConnection) -> None:
    accumulator = ResponsesWebSocketAccumulator()
    accumulator.add_event(connection.recv())
    assert_type(accumulator.get_final_response(), Response)


def caller_fed_beta(connection: BetaResponsesConnection) -> None:
    accumulator = ResponsesWebSocketAccumulator(response_type=BetaResponse)
    accumulator.add_event(connection.recv())
    assert_type(accumulator.get_final_response(), BetaResponse)


async def caller_fed_async_stable(connection: AsyncResponsesConnection) -> None:
    accumulator = ResponsesWebSocketAccumulator()
    accumulator.add_event(await connection.recv())
    assert_type(accumulator.get_final_response(), Response)


async def caller_fed_async_beta(connection: AsyncBetaResponsesConnection) -> None:
    accumulator = ResponsesWebSocketAccumulator(response_type=BetaResponse)
    accumulator.add_event(await connection.recv())
    assert_type(accumulator.get_final_response(), BetaResponse)
