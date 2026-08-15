from __future__ import annotations

from typing import Any

from trading_risk_sdk.gates.circuit_breaker import CircuitBreakerGate
from trading_risk_sdk.gates.daily_loss import DailyLossGate
from trading_risk_sdk.gates.duplicate_position import DuplicatePositionGate
from trading_risk_sdk.gates.time_cutoff import TimeCutoffGate
from trading_risk_sdk.policy import RiskGate

_GATES: dict[str, type[RiskGate]] = {
    "time_cutoff": TimeCutoffGate,
    "circuit_breaker": CircuitBreakerGate,
    "daily_loss": DailyLossGate,
    "duplicate_position": DuplicatePositionGate,
}


def get_gate(gate_id: str) -> type[RiskGate]:
    try:
        return _GATES[gate_id]
    except KeyError:
        raise KeyError(
            f"Unknown gate_id {gate_id!r}. Registered gates: {sorted(_GATES)}"
        ) from None


def create_gate(gate_id: str, params: dict[str, Any] | None = None) -> RiskGate:
    return get_gate(gate_id)(**(params or {}))


def registered_gates() -> list[str]:
    return sorted(_GATES)
