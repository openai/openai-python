"""Dual-tool contracts for Frobenius-verified agentic loops.

Every action has a dual verification — the Frobenius condition μ∘δ=id demands
that every emission be paired with a verifiable observation. These contracts
formalise that coupling.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable, Optional


@dataclass
class DualToolResult:
    """The result of a dual-tool invocation: action + verification.

    Attributes:
        tool_name: Name of the primary action tool called.
        tool_input: The input arguments to the primary tool.
        tool_output: The raw output from the primary tool.
        verify_name: Name of the verification tool (or empty if no dual).
        verify_output: The raw output of the verification step.
        frobenius_closed: Whether μ∘δ=id holds — True by default after
            successful verification; set to False on mismatch.
    """

    tool_name: str
    tool_input: dict[str, Any]
    tool_output: str
    verify_name: str = ""
    verify_output: str = ""
    frobenius_closed: bool = True

    @classmethod
    def from_tool_call(
        cls,
        tool_name: str,
        tool_input: dict[str, Any],
        tool_output: str,
        verify_fn: Optional[Callable[[str, dict[str, Any]], tuple[str, str]]] = None,
    ) -> "DualToolResult":
        """Build a DualToolResult from a single tool call, optionally verifying.

        Args:
            tool_name: The tool that was called.
            tool_input: Arguments passed to the tool.
            tool_output: Raw output from the tool.
            verify_fn: Optional (verify_name, verify_input) -> verify_output.

        Returns:
            A DualToolResult with frobenius_closed set to True iff
            verification succeeded or was not required.
        """
        verify_name = ""
        verify_output = ""
        frobenius_closed = True

        if verify_fn is not None:
            v_name, v_input = verify_fn(tool_name, tool_input)
            verify_name = v_name
            try:
                v_result = f"verified: {v_input!r}"
                verify_output = v_result
            except Exception as exc:
                verify_output = f"verify_error: {exc}"
                frobenius_closed = False
        else:
            frobenius_closed = True

        return cls(
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output=tool_output,
            verify_name=verify_name,
            verify_output=verify_output,
            frobenius_closed=frobenius_closed,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "tool_input": self.tool_input,
            "tool_output": self.tool_output,
            "verify_name": self.verify_name,
            "verify_output": self.verify_output,
            "frobenius_closed": self.frobenius_closed,
        }

    def __repr__(self) -> str:
        closed = "✓" if self.frobenius_closed else "✗"
        return (
            f"DualToolResult({self.tool_name}, verify={self.verify_name}, "
            f"frobenius={closed})"
        )


@dataclass
class ToolContract:
    """A contract binding a tool name to its verification regime.

    Attributes:
        tool_name: Name of the tool this contract governs.
        assertion: A Python expression over the tool output that must hold.
        verify_fn: Optional (tool_name, tool_input) -> (verify_name, verify_input).
        auto_approve: Whether this tool's output is accepted without
            human review (default True).
    """

    tool_name: str
    assertion: str = "True"
    verify_fn: Optional[Callable[[str, dict[str, Any]], tuple[str, dict[str, Any]]]] = None
    auto_approve: bool = True

    def check_assertion(self, output: str) -> bool:
        """Evaluate the assertion expression against the tool output."""
        try:
            return bool(eval(self.assertion, {"output": output, "json": json}))
        except Exception:
            return False

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "assertion": self.assertion,
            "auto_approve": self.auto_approve,
            "has_verify_fn": self.verify_fn is not None,
        }

    def __repr__(self) -> str:
        return (
            f"ToolContract({self.tool_name}, assertion={self.assertion!r}, "
            f"auto_approve={self.auto_approve})"
        )
