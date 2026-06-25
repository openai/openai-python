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

import ast
import json
import math
import operator

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


# A whitelist-based arithmetic evaluator. We deliberately avoid eval(): the model
# controls `expression`, and eval() — even with empty __builtins__ — can still run
# dunder introspection or resource-exhausting expressions. Walking the AST and
# permitting only arithmetic nodes keeps model-supplied input from reaching the host.

_ALLOWED_BINARY_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_ALLOWED_UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}
# A small, safe subset of the math module.
_ALLOWED_NAMES = {"pi": math.pi, "e": math.e, "tau": math.tau}
_ALLOWED_FUNCS = {"sqrt": math.sqrt, "floor": math.floor, "ceil": math.ceil, "abs": abs}

# Cap exponents so the model can't request a multi-gigabyte integer (e.g. 9**9**9).
_MAX_EXPONENT = 1000


def _eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return node.value
        raise ValueError(f"unsupported constant: {node.value!r}")
    if isinstance(node, ast.BinOp):
        op = _ALLOWED_BINARY_OPS.get(type(node.op))
        if op is None:
            raise ValueError(f"unsupported operator: {type(node.op).__name__}")
        left, right = _eval_node(node.left), _eval_node(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > _MAX_EXPONENT:
            raise ValueError("exponent too large")
        return op(left, right)
    if isinstance(node, ast.UnaryOp):
        op = _ALLOWED_UNARY_OPS.get(type(node.op))
        if op is None:
            raise ValueError(f"unsupported unary operator: {type(node.op).__name__}")
        return op(_eval_node(node.operand))
    if isinstance(node, ast.Name):
        if node.id in _ALLOWED_NAMES:
            return _ALLOWED_NAMES[node.id]
        raise ValueError(f"unknown name: {node.id}")
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name) or node.func.id not in _ALLOWED_FUNCS:
            raise ValueError("unsupported function call")
        if node.keywords:
            raise ValueError("keyword arguments are not supported")
        return _ALLOWED_FUNCS[node.func.id](*(_eval_node(arg) for arg in node.args))
    raise ValueError(f"unsupported expression: {type(node).__name__}")


def calculate(expression: str) -> str:
    """Evaluate an arithmetic expression via a whitelisted AST walk (no eval, no builtins).

    Supports +, -, *, /, //, %, ** and a small math subset (sqrt, floor, ceil, abs,
    pi, e, tau). Anything else is rejected rather than executed.
    """
    try:
        tree = ast.parse(expression, mode="eval")
        return str(_eval_node(tree.body))
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
