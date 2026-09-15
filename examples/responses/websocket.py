from __future__ import annotations

import json
import argparse
from typing import TYPE_CHECKING, Dict, Union, Literal, Optional, TypedDict, NamedTuple, cast

from openai import OpenAI
from openai.types.responses import (
    FunctionToolParam,
    ToolChoiceOptions,
    ResponseInputParam,
    ResponseFailedEvent,
    ResponseCompletedEvent,
    ResponseInputItemParam,
    ResponseIncompleteEvent,
    ToolChoiceFunctionParam,
)

if TYPE_CHECKING:
    from openai.resources.responses.responses import ResponsesConnection

ToolName = Literal["get_sku_inventory", "get_supplier_eta", "get_quality_alerts"]
ToolChoice = Union[ToolChoiceOptions, ToolChoiceFunctionParam]


class DemoTurn(TypedDict):
    tool_name: ToolName
    prompt: str


class SKUArguments(TypedDict):
    sku: str


class SKUInventoryOutput(TypedDict):
    sku: str
    warehouse: str
    on_hand_units: int
    reserved_units: int
    reorder_point: int
    safety_stock: int


class SupplierShipment(TypedDict):
    shipment_id: str
    eta_date: str
    quantity: int
    risk: str


class SupplierETAOutput(TypedDict):
    sku: str
    supplier_shipments: list[SupplierShipment]


class QualityAlert(TypedDict):
    alert_id: str
    status: str
    severity: str
    summary: str


class QualityAlertsOutput(TypedDict):
    sku: str
    alerts: list[QualityAlert]


class FunctionCallOutputItem(TypedDict):
    type: Literal["function_call_output"]
    call_id: str
    output: str


class FunctionCallRequest(NamedTuple):
    name: str
    arguments_json: str
    call_id: str


class RunResponseResult(NamedTuple):
    text: str
    response_id: str
    function_calls: list[FunctionCallRequest]


class RunTurnResult(NamedTuple):
    assistant_text: str
    response_id: str


ToolOutput = Union[SKUInventoryOutput, SupplierETAOutput, QualityAlertsOutput]

TOOLS: list[FunctionToolParam] = [
    {
        "type": "function",
        "name": "get_sku_inventory",
        "description": "Return froge pond inventory details for a SKU.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "sku": {
                    "type": "string",
                    "description": "Stock-keeping unit identifier, such as sku-froge-lily-pad-deluxe.",
                }
            },
            "required": ["sku"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_supplier_eta",
        "description": "Return tadpole supplier restock ETA data for a SKU.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "sku": {
                    "type": "string",
                    "description": "Stock-keeping unit identifier, such as sku-froge-lily-pad-deluxe.",
                }
            },
            "required": ["sku"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_quality_alerts",
        "description": "Return recent froge quality alerts for a SKU.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "sku": {
                    "type": "string",
                    "description": "Stock-keeping unit identifier, such as sku-froge-lily-pad-deluxe.",
                }
            },
            "required": ["sku"],
            "additionalProperties": False,
        },
    },
]

DEMO_TURNS: list[DemoTurn] = [
    {
        "tool_name": "get_sku_inventory",
        "prompt": "Use get_sku_inventory for sku='sku-froge-lily-pad-deluxe' and summarize current pond stock health in one sentence.",
    },
    {
        "tool_name": "get_supplier_eta",
        "prompt": "Now use get_supplier_eta for the same SKU and summarize restock ETA and tadpole shipment risk.",
    },
    {
        "tool_name": "get_quality_alerts",
        "prompt": "Finally use get_quality_alerts for the same SKU and summarize unresolved froge quality concerns in one short paragraph.",
    },
]

BETA_HEADER_VALUE = "responses_websockets=2026-02-06"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=("Run a 3-turn Responses WebSocket demo with function calling and chained previous_response_id.")
    )
    parser.add_argument("--model", default="gpt-5.2", help="Model used in the `response.create` payload.")
    parser.add_argument(
        "--use-beta-header",
        action="store_true",
        help=f"Include `OpenAI-Beta: {BETA_HEADER_VALUE}` for beta websocket behavior.",
    )
    parser.add_argument(
        "--show-events",
        action="store_true",
        help="Print non-text event types while streaming.",
    )
    parser.add_argument(
        "--show-tool-io",
        action="store_true",
        help="Print each tool call and tool output payload.",
    )
    return parser.parse_args()


def parse_tool_name(name: str) -> ToolName:
    if name not in {"get_sku_inventory", "get_supplier_eta", "get_quality_alerts"}:
        raise ValueError(f"Unsupported tool requested: {name}")
    return cast(ToolName, name)


def parse_sku_arguments(raw_arguments: str) -> SKUArguments:
    parsed_raw = json.loads(raw_arguments)
    if not isinstance(parsed_raw, dict):
        raise ValueError(f"Tool arguments must be a JSON object: {raw_arguments}")

    parsed = cast(Dict[str, object], parsed_raw)
    sku_value = parsed.get("sku")
    if not isinstance(sku_value, str):
        raise ValueError(f"Tool arguments must include a string `sku`: {raw_arguments}")

    return {"sku": sku_value}


def call_tool(name: ToolName, arguments: SKUArguments) -> ToolOutput:
    sku = arguments["sku"]

    if name == "get_sku_inventory":
        return {
            "sku": sku,
            "warehouse": "pond-west-1",
            "on_hand_units": 84,
            "reserved_units": 26,
            "reorder_point": 60,
            "safety_stock": 40,
        }

    if name == "get_supplier_eta":
        return {
            "sku": sku,
            "supplier_shipments": [
                {
                    "shipment_id": "frog_ship_2201",
                    "eta_date": "2026-02-24",
                    "quantity": 180,
                    "risk": "low",
                },
                {
                    "shipment_id": "frog_ship_2205",
                    "eta_date": "2026-03-03",
                    "quantity": 220,
                    "risk": "medium",
                },
            ],
        }

    if name == "get_quality_alerts":
        return {
            "sku": sku,
            "alerts": [
                {
                    "alert_id": "frog_qa_781",
                    "status": "open",
                    "severity": "high",
                    "summary": "Lily-pad coating chipping in lot LP-42",
                },
                {
                    "alert_id": "frog_qa_795",
                    "status": "in_progress",
                    "severity": "medium",
                    "summary": "Pond-crate scuff rate above threshold",
                },
                {
                    "alert_id": "frog_qa_802",
                    "status": "resolved",
                    "severity": "low",
                    "summary": "Froge label alignment issue corrected",
                },
            ],
        }

    raise ValueError(f"Unknown tool: {name}")


def run_response(
    *,
    connection: ResponsesConnection,
    model: str,
    previous_response_id: Optional[str],
    input_payload: Union[str, ResponseInputParam],
    tools: list[FunctionToolParam],
    tool_choice: ToolChoice,
    show_events: bool,
) -> RunResponseResult:
    connection.response.create(
        model=model,
        input=input_payload,
        stream=True,
        previous_response_id=previous_response_id,
        tools=tools,
        tool_choice=tool_choice,
    )

    text_parts: list[str] = []
    function_calls: list[FunctionCallRequest] = []
    response_id: Optional[str] = None

    for event in connection:
        if event.type == "response.output_text.delta":
            text_parts.append(event.delta)
            continue

        if event.type == "response.output_item.done" and event.item.type == "function_call":
            function_calls.append(
                FunctionCallRequest(
                    name=event.item.name,
                    arguments_json=event.item.arguments,
                    call_id=event.item.call_id,
                )
            )
            continue

        if getattr(event, "type", None) == "error":
            raise RuntimeError(f"WebSocket error event: {event!r}")

        if isinstance(event, (ResponseCompletedEvent, ResponseFailedEvent, ResponseIncompleteEvent)):
            response_id = event.response.id
            if not isinstance(event, ResponseCompletedEvent):
                raise RuntimeError(f"Response ended with {event.type} (id={response_id})")
            if show_events:
                print(f"[{event.type}]")
            break

        if getattr(event, "type", None) == "response.done":
            # Responses over WebSocket currently emit `response.done` as the final event.
            # The payload still includes `response.id`, which we use for chaining.
            event_response = getattr(event, "response", None)
            event_response_id: Optional[str] = None
            if isinstance(event_response, dict):
                event_response_dict = cast(Dict[str, object], event_response)
                raw_event_response_id = event_response_dict.get("id")
                if isinstance(raw_event_response_id, str):
                    event_response_id = raw_event_response_id
            else:
                raw_event_response_id = getattr(event_response, "id", None)
                if isinstance(raw_event_response_id, str):
                    event_response_id = raw_event_response_id

            if not isinstance(event_response_id, str):
                raise RuntimeError(f"response.done event did not include a valid response.id: {event!r}")

            response_id = event_response_id
            if show_events:
                print("[response.done]")
            break

        if show_events:
            print(f"[{event.type}]")

    if response_id is None:
        raise RuntimeError("No terminal response event received.")

    return RunResponseResult(
        text="".join(text_parts),
        response_id=response_id,
        function_calls=function_calls,
    )


def run_turn(
    *,
    connection: ResponsesConnection,
    model: str,
    previous_response_id: Optional[str],
    turn_prompt: str,
    forced_tool_name: ToolName,
    show_events: bool,
    show_tool_io: bool,
) -> RunTurnResult:
    accumulated_text_parts: list[str] = []

    current_input: Union[str, ResponseInputParam] = turn_prompt
    current_tool_choice: ToolChoice = {"type": "function", "name": forced_tool_name}
    current_previous_response_id = previous_response_id

    while True:
        response_result = run_response(
            connection=connection,
            model=model,
            previous_response_id=current_previous_response_id,
            input_payload=current_input,
            tools=TOOLS,
            tool_choice=current_tool_choice,
            show_events=show_events,
        )

        if response_result.text:
            accumulated_text_parts.append(response_result.text)

        current_previous_response_id = response_result.response_id
        if not response_result.function_calls:
            break

        tool_outputs: ResponseInputParam = []
        for function_call in response_result.function_calls:
            tool_name = parse_tool_name(function_call.name)
            arguments = parse_sku_arguments(function_call.arguments_json)
            output_payload = call_tool(tool_name, arguments)
            if show_tool_io:
                print(f"[tool_call] {function_call.name}({function_call.arguments_json})")
                print(f"[tool_output] {json.dumps(output_payload)}")

            function_call_output: FunctionCallOutputItem = {
                "type": "function_call_output",
                "call_id": function_call.call_id,
                "output": json.dumps(output_payload),
            }
            tool_outputs.append(cast(ResponseInputItemParam, function_call_output))

        current_input = tool_outputs
        current_tool_choice = "none"

    return RunTurnResult(
        assistant_text="".join(accumulated_text_parts).strip(),
        response_id=current_previous_response_id,
    )


def main() -> None:
    args = parse_args()

    client = OpenAI()
    extra_headers = {"OpenAI-Beta": BETA_HEADER_VALUE} if args.use_beta_header else {}

    with client.responses.connect(extra_headers=extra_headers) as connection:
        previous_response_id: Optional[str] = None
        for index, turn in enumerate(DEMO_TURNS, start=1):
            print(f"\n=== Turn {index} ===")
            print(f"User: {turn['prompt']}")
            turn_result = run_turn(
                connection=connection,
                model=args.model,
                previous_response_id=previous_response_id,
                turn_prompt=turn["prompt"],
                forced_tool_name=turn["tool_name"],
                show_events=args.show_events,
                show_tool_io=args.show_tool_io,
            )
            previous_response_id = turn_result.response_id
            print(f"Assistant: {turn_result.assistant_text}")


if __name__ == "__main__":
    main()
