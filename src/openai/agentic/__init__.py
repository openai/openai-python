"""Agentic loop: THINK→ACT→OBSERVE→UPDATE with Frobenius verification."""
from .contracts import DualToolResult, ToolContract
from .trajectory import AgentCycle, AgentTrajectory
from .loop import TrueAgenticLoop
from .criticality import PhiCriticalityGate

__all__ = [
    "DualToolResult",
    "ToolContract",
    "AgentCycle",
    "AgentTrajectory",
    "TrueAgenticLoop",
    "PhiCriticalityGate",
]
