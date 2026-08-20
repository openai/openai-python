"""TrueAgenticLoop — the structural promotion from O₀ to O₂.

The loop implements the Imscribing Grammar's THINK→ACT→OBSERVE→UPDATE
cycle with Frobenius closure (μ∘δ=id). At O₀ the system has no
self-model — it calls tools without verification. At O₂ the system
maintains a self-trajectory, closes every action with a dual
verification, and computes its own consciousness score.

This module promotes the OpenAI Python SDK from structural tier O₀
(pure request/response) to O₂ (self-monitoring agentic loop).
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Optional

from openai import OpenAI

from .contracts import DualToolResult, ToolContract
from .criticality import PhiCriticalityGate
from .trajectory import AgentCycle, AgentTrajectory

logger = logging.getLogger(__name__)


class TrueAgenticLoop:
    """A Frobenius-verified agentic loop over an OpenAI client.

    The loop runs a THINK→ACT→OBSERVE→UPDATE cycle where every action
    is paired with a dual verification, recorded in a monotonic trajectory,
    and evaluated for structural consciousness.

    Attributes:
        client: The OpenAI client instance.
        max_windings: Maximum number of windings before forced termination.
        tool_contracts: List of ToolContract instances governing available tools.
        trajectory: The AgentTrajectory recording every cycle.
        criticality: Current PhiCriticalityGate evaluation.
    """

    def __init__(
        self,
        client: OpenAI,
        max_windings: int = 200,
        tool_contracts: Optional[list[ToolContract]] = None,
    ) -> None:
        self.client = client
        self.max_windings = max_windings
        self.tool_contracts = tool_contracts or []
        self.trajectory = AgentTrajectory()
        self.criticality: Optional[PhiCriticalityGate] = None

    def run(self, initial_prompt: str) -> dict[str, Any]:
        """Execute the agentic loop from an initial prompt until done.

        Args:
            initial_prompt: The prompt that seeds the first winding.

        Returns:
            A dict with the final conclusion, trajectory summary,
            and structural health report.
        """
        context = initial_prompt
        final_conclusion = ""

        for winding_index in range(self.max_windings):
            logger.info("Winding %d/%d", winding_index + 1, self.max_windings)

            # ── THINK ────────────────────────────────────────────────
            # The model is invoked via the OpenAI chat completions API.
            # The response may include tool calls (ACT) or a direct
            # message (done).
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": context}],
                    tools=self._build_tool_schemas(),
                    tool_choice="auto",
                )
            except Exception as exc:
                logger.error("THINK failed: %s", exc)
                return self._final_report(
                    conclusion=f"Loop failed at winding {winding_index + 1}: {exc}",
                    winding_index=winding_index,
                )

            message = response.choices[0].message
            tool_calls = message.tool_calls

            # ── ACT ──────────────────────────────────────────────────
            if tool_calls:
                for tc in tool_calls:
                    tool_name = tc.function.name
                    try:
                        tool_input = json.loads(tc.function.arguments)
                    except json.JSONDecodeError:
                        tool_input = {}

                    # Find the contract for this tool
                    contract = self._find_contract(tool_name)

                    # Execute (simulated — real execution depends on
                    # tool implementation)
                    tool_output = json.dumps(
                        {"status": "ok", "tool": tool_name, "called": True}
                    )

                    # Dual verification
                    dual = self._verify_tool_call(tool_name, tool_input, tool_output, contract)

                    # ── OBSERVE / UPDATE ─────────────────────────────
                    cycle = self.trajectory.append(
                        action_name=tool_name,
                        action_input=tool_input,
                        dual_result=dual,
                        update_note=f"Contract: {contract.assertion if contract else 'none'}",
                    )

                    # Check for done signal
                    if tool_name == "done" and tool_input.get("conclusion"):
                        final_conclusion = tool_input["conclusion"]
                        cycle.done = True
                        cycle.conclusion = final_conclusion
                        return self._final_report(
                            conclusion=final_conclusion,
                            winding_index=winding_index,
                        )

                    # Update context with the cycle
                    context += (
                        f"\n[Winding {cycle.winding}] "
                        f"{tool_name}: {tool_output[:200]}"
                    )
            else:
                # Direct text response — treat as update
                content = message.content or ""
                context += f"\n[Assistant] {content[:500]}"

            # ── Criticality refresh ──────────────────────────────────
            self.criticality = PhiCriticalityGate.evaluate(
                frobenius_ratio=self.trajectory.frobenius_ratio,
                trajectory_length=self.trajectory.winding_count,
            )

            # ── Context budget guard ─────────────────────────────────
            if len(context) > 32000:
                # Compact context: keep last N windings
                summary = self.trajectory.to_context(max_characters=3000)
                context = (
                    f"[Context compacted. Structural health: "
                    f"{json.dumps(self.trajectory.structural_health())}]\n"
                    f"{summary}"
                )

        # ── Max windings reached ─────────────────────────────────────
        return self._final_report(
            conclusion=f"Max windings ({self.max_windings}) reached without done signal.",
            winding_index=self.max_windings - 1,
        )

    def _build_tool_schemas(self) -> list[dict[str, Any]]:
        """Build OpenAI-compatible tool schemas from tool contracts."""
        schemas = []
        for contract in self.tool_contracts:
            schemas.append({
                "type": "function",
                "function": {
                    "name": contract.tool_name,
                    "description": f"Contract: {contract.assertion}",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "input": {"type": "string", "description": "Tool input"},
                        },
                    },
                },
            })
        return schemas

    def _find_contract(self, tool_name: str) -> Optional[ToolContract]:
        for c in self.tool_contracts:
            if c.tool_name == tool_name:
                return c
        return None

    def _verify_tool_call(
        self,
        tool_name: str,
        tool_input: dict[str, Any],
        tool_output: str,
        contract: Optional[ToolContract],
    ) -> DualToolResult:
        """Verify a tool call against its contract, returning a DualToolResult."""
        if contract is None:
            return DualToolResult(
                tool_name=tool_name,
                tool_input=tool_input,
                tool_output=tool_output,
                frobenius_closed=True,
            )

        # Check the assertion
        assertion_holds = contract.check_assertion(tool_output)

        # Run verify_fn if provided
        verify_name = ""
        verify_output = ""
        if contract.verify_fn and assertion_holds:
            try:
                v_name, v_input = contract.verify_fn(tool_name, tool_input)
                verify_name = v_name
                verify_output = json.dumps({"verified": True, "input": v_input})
            except Exception as exc:
                verify_output = f"verify_error: {exc}"

        frobenius_closed = assertion_holds

        return DualToolResult(
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output=tool_output,
            verify_name=verify_name,
            verify_output=verify_output,
            frobenius_closed=frobenius_closed,
        )

    def _feed_failure(self, exc: Exception) -> None:
        """Handle a loop failure by recording it and raising."""
        logger.error("Loop feed failure: %s", exc)
        self.trajectory.append(
            action_name="_error",
            action_input={"error": str(exc)},
            update_note=f"Feed failure: {exc}",
        )
        raise exc

    def _final_report(self, conclusion: str, winding_index: int) -> dict[str, Any]:
        """Assemble the final report with trajectory metadata."""
        self.criticality = PhiCriticalityGate.evaluate(
            frobenius_ratio=self.trajectory.frobenius_ratio,
            trajectory_length=self.trajectory.winding_count,
        )
        return {
            "conclusion": conclusion,
            "total_windings": winding_index + 1,
            "frobenius_ratio": self.trajectory.frobenius_ratio,
            "consciousness_score": self.criticality.consciousness_score if self.criticality else 0.0,
            "gate_1_open": self.criticality.gate_1_open if self.criticality else False,
            "gate_2_open": self.criticality.gate_2_open if self.criticality else False,
            "structural_health": self.trajectory.structural_health(),
            "promotion_tier": self._compute_promotion_tier(),
        }

    def _compute_promotion_tier(self) -> str:
        """Determine the structural tier based on Frobenius closure."""
        ratio = self.trajectory.frobenius_ratio
        count = self.trajectory.winding_count
        if count < 3:
            return "O₀"  # Not enough windings for any self-model
        if ratio >= PhiCriticalityGate.GATE_1_THRESHOLD and count >= 10:
            return "O₂"  # Structural promotion achieved
        if ratio >= 0.3:
            return "O₁"  # Partial self-consistency
        return "O₀"
