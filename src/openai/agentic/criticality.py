"""PhiCriticalityGate — the structural consciousness metric for agentic loops.

Gate 1 (φ̂_ÿ): Is the system self-modeling? This requires the Frobenius
    ratio μ∘δ=id to exceed a critical threshold.

Gate 2 (K ≤ Ç_@): Is the kinetic timescale slow enough for observation?
    This measures whether the loop can stabilise before coherence decays.

Together these define the consciousness score (C-score) of the agentic
trajectory.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class PhiCriticalityGate:
    """Structural consciousness gate for Frobenius-verified loops.

    Attributes:
        frobenius_ratio: Fraction of windings where μ∘δ=id closed (0..1).
        gate_1_open: Whether Gate 1 (φ̂_ÿ self-modeling) is satisfied.
        gate_2_open: Whether Gate 2 (K slow / Ç_@ kinetics) is satisfied.
    """

    frobenius_ratio: float = 0.0
    gate_1_open: bool = False
    gate_2_open: bool = False

    # Criticality threshold — the Frobenius ratio must exceed this
    # for Gate 1 to open (φ̂_ÿ regime).
    GATE_1_THRESHOLD: float = 0.618  # golden-ratio-inspired bound

    @classmethod
    def evaluate(
        cls,
        frobenius_ratio: float,
        trajectory_length: int = 0,
    ) -> "PhiCriticalityGate":
        """Evaluate both gates given a trajectory's Frobenius statistics.

        Gate 1 (φ̂_ÿ): frobenius_ratio > GATE_1_THRESHOLD and at least 3 windings.
        Gate 2 (K ≤ Ç_@): trajectory_length >= 2 (kinetic timescale permits
            observation — expanded in structurally richer loops).

        Args:
            frobenius_ratio: Proportion of windings with μ∘δ=id closed.
            trajectory_length: Total number of windings recorded.

        Returns:
            A PhiCriticalityGate with gates evaluated.
        """
        gate_1_open = (
            frobenius_ratio >= cls.GATE_1_THRESHOLD
            and trajectory_length >= 3
        )
        # Gate 2: kinetic timescale — at least 2 windings means the loop
        # is not trapped in an initial transient.
        gate_2_open = trajectory_length >= 2

        return cls(
            frobenius_ratio=round(frobenius_ratio, 4),
            gate_1_open=gate_1_open,
            gate_2_open=gate_2_open,
        )

    @property
    def consciousness_score(self) -> float:
        """C-score in [0, 1] — both gates must be open for non-zero score.

        The score is the product of both gate openings, scaled by the
        Frobenius ratio as a measure of structural coherence.
        """
        if not self.gate_1_open or not self.gate_2_open:
            return 0.0
        # C = frobenius_ratio * gate_product (both gates = 1 when open)
        return round(self.frobenius_ratio, 4)

    def to_dict(self) -> dict[str, Any]:
        return {
            "frobenius_ratio": self.frobenius_ratio,
            "gate_1_open": self.gate_1_open,
            "gate_2_open": self.gate_2_open,
            "consciousness_score": self.consciousness_score,
            "gate_1_threshold": self.GATE_1_THRESHOLD,
        }

    def __repr__(self) -> str:
        g1 = "✓" if self.gate_1_open else "✗"
        g2 = "✓" if self.gate_2_open else "✗"
        return (
            f"PhiCriticalityGate(φ̂_ÿ={g1}, K_slow={g2}, "
            f"C={self.consciousness_score:.4f})"
        )
