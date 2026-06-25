"""
Multi-turn tool-call loop using the Responses API.

This example shows the complete agent pattern that developers most often need:

  1. Send a user message that requires tool use.
  2. The model responds with one or more function_call items.
  3. Execute each function locally and collect the results.
  4. Pass the results back using `previous_response_id` + function_call_output items.
  5. Repeat until the model produces a plain-text answer (no more tool calls).
  6. Guard against unbounded loops with MAX_TURNS.

Run:
    python examples/responses/tool_call_loop.py
"""

from __future__ import annotations

import json
import math

from openai import OpenAI

client = OpenAI()

MAX_TURNS = 10

# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------


def get_weather(city: str) -> str:
    """Return a fake weather report. Replace with a real API call in production."""
    forecasts = {
        "tokyo": {"temperature": "18°C", "condition": "clear"},
        "london": {"temperature": "12°C", "condition": "overcast"},
        "new york": {"temperature": "22°C", "condition": "sunny"},
    }
    data = forecasts.get(city.lower(), {"temperature": "unknown", "condition": "unknown"})
    return json.dumps({"city": city, **data})


def calculate(expression: str) -> str:
    """Safely evaluate a Python arithmetic expression (no builtins, math module available)."""
    try:
        result = eval(expression, {"__builtins__": {}}, vars(math))  # noqa: S307
        return str(result)
    except Exception as exc:
        return f"error: {exc}"


TOOLS = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get the current weather for a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city name, e.g. 'Tokyo'.",
                }
            },
            "required": ["city"],
        },
    },
    {
        "type": "function",
        "name": "calculate",
        "description": "Evaluate a mathematical expression using Python arithmetic and the math module.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A Python arithmetic expression, e.g. '7 * 24 * 3600'.",
                }
            },
            "required": ["expression"],
        },
    },
]

TOOL_MAP = {"get_weather": get_weather, "calculate": calculate}

# ---------------------------------------------------------------------------
# Agent loop
# ---------------------------------------------------------------------------


def run_agent(user_message: str) -> str:
    """Run the tool-call loop until the model returns a final text answer."""
    print(f"User: {user_message}\n")

    # First turn — send the initial user message
    response = client.responses.create(
        model="gpt-4o-mini",
        input=user_message,
        tools=TOOLS,  # type: ignore[arg-type]
    )

    for turn in range(MAX_TURNS):
        # Collect any function calls the model wants to make
        tool_calls = [item for item in response.output if item.type == "function_call"]

        if not tool_calls:
            # No more tool calls — the model has produced its final answer
            return response.output_text

        # Execute each tool and collect outputs
        tool_outputs = []
        for call in tool_calls:
            args = json.loads(call.arguments)
            result = TOOL_MAP[call.name](**args)
            print(f"  [turn {turn + 1}] {call.name}({call.arguments}) → {result}")
            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": result,
                }
            )

        # Continue the conversation: pass tool outputs and reference the previous response
        # so the model has full context without us manually rebuilding the input list.
        response = client.responses.create(
            model="gpt-4o-mini",
            previous_response_id=response.id,
            input=tool_outputs,  # type: ignore[arg-type]
            tools=TOOLS,  # type: ignore[arg-type]
        )

    raise RuntimeError(f"Agent did not finish within MAX_TURNS={MAX_TURNS}")


if __name__ == "__main__":
    answer = run_agent(
        "What's the weather like in Tokyo and London? "
        "Also, how many seconds are in 7 weeks?"
    )
    print(f"\nAssistant: {answer}")
