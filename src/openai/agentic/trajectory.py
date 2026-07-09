"""Trajectory tracking for Frobenius-verified agentic loops.

An AgentTrajectory records every winding of the THINK→ACT→OBSERVE→UPDATE
loop, maintaining monotonic advance (Ω_z invariant) and providing
structural health metrics.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Optional

from .contracts import DualToolResult


@dataclass
class AgentCycle:
    """A single winding of the agentic loop.

    Attributes:
        winding: Monotonically increasing winding number (never resets).
        timestamp: Unix time when the cycle was recorded.
        action_name: Name of the tool called in this winding.
        action_input: Arguments passed to the tool.
        dual_result: The DualToolResult from action + verification.
        update_note: Free-text note about what was learned.
        done: Whether this cycle issued a terminal signal.
        conclusion: The final conclusion if done is True.
        frobenius_closed: Cached from dual_result.
    """

    winding: int
    timestamp: float = field(default_factory=time.time)
    action_name: str = ""
    action_input: dict[str, Any] = field(default_factory=dict)
    dual_result: Optional[DualToolResult] = None
    update_note: str = ""
    done: bool = False
    conclusion: str = ""
    frobenius_closed: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "winding": self.winding,
            "timestamp": self.timestamp,
            "action_name": self.action_name,
            "action_input": self.action_input,
            "dual_result": self.dual_result.to_dict() if self.dual_result else None,
            "update_note": self.update_note,
            "done": self.done,
            "conclusion": self.conclusion,
            "frobenius_closed": self.frobenius_closed,
        }

    def __repr__(self) -> str:
        closed = "✓" if self.frobenius_closed else "✗"
        return (
            f"AgentCycle(winding={self.winding}, action={self.action_name}, "
            f"frobenius={closed}, done={self.done})"
        )


class AgentTrajectory:
    """Monotonic trajectory of agentic windings.

    The winding counter NEVER resets (Ω_z invariant) — each agent
    call increments monotonically, providing a total order over all
    actions the system has ever taken.

    Attributes:
        _cycles: Ordered list of completed AgentCycle records.
        _winding_counter: Global counter that never resets.
    """

    def __init__(self) -> None:
        self._cycles: list[AgentCycle] = []
        self._winding_counter: int = 0

    @property
    def winding_count(self) -> int:
        """Total number of windings completed (monotonically increasing)."""
        return len(self._cycles)

    @property
    def frobenius_ratio(self) -> float:
        """Fraction of windings that closed Frobenius (μ∘δ=id)."""
        if not self._cycles:
            return 1.0
        closed = sum(1 for c in self._cycles if c.frobenius_closed)
        return closed / len(self._cycles)

    def append(
        self,
        action_name: str,
        action_input: dict[str, Any],
        dual_result: Optional[DualToolResult] = None,
        update_note: str = "",
        done: bool = False,
        conclusion: str = "",
    ) -> AgentCycle:
        """Record a new winding and return the cycle."""
        self._winding_counter += 1
        cycle = AgentCycle(
            winding=self._winding_counter,
            action_name=action_name,
            action_input=action_input,
            dual_result=dual_result,
            update_note=update_note,
            done=done,
            conclusion=conclusion,
            frobenius_closed=dual_result.frobenius_closed if dual_result else True,
        )
        self._cycles.append(cycle)
        return cycle

    def last(self) -> Optional[AgentCycle]:
        """Return the most recent cycle, if any."""
        return self._cycles[-1] if self._cycles else None

    def to_context(self, max_characters: int = 8000) -> str:
        """Serialize the trajectory to a compact string for prompt context."""
        lines: list[str] = []
        for cycle in self._cycles[-20:]:  # last 20 at most
            closed = "✓" if cycle.frobenius_closed else "✗"
            done_mark = " [DONE]" if cycle.done else ""
            lines.append(
                f"[{cycle.winding}] {cycle.action_name} {closed}{done_mark}"
            )
            if cycle.update_note and len(lines[-1]) < 200:
                lines[-1] += f" — {cycle.update_note[:120]}"
        return "\n".join(lines)

    def structural_health(self) -> dict[str, Any]:
        """Return a health report with key structural invariants."""
        return {
            "winding_count": self.winding_count,
            "frobenius_ratio": self.frobenius_ratio,
            "total_cycles": len(self._cycles),
            "last_winding": self.last().winding if self.last() else None,
            "done_reached": any(c.done for c in self._cycles),
        }

    def __len__(self) -> int:
        return len(self._cycles)

    def __getitem__(self, idx: int) -> AgentCycle:
        return self._cycles[idx]
