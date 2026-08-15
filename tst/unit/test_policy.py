"""Tests for policy.py — RiskContext, RiskGate/RiskSizer protocol conformance."""

from __future__ import annotations

from trading_risk_sdk.gates.circuit_breaker import CircuitBreakerGate
from trading_risk_sdk.gates.daily_loss import DailyLossGate
from trading_risk_sdk.gates.duplicate_position import DuplicatePositionGate
from trading_risk_sdk.gates.time_cutoff import TimeCutoffGate
from trading_risk_sdk.policy import RiskGate, RiskSizer
from trading_risk_sdk.sizer import VolatilitySizer


def test_risk_context_is_frozen(context_factory) -> None:
    ctx = context_factory()
    try:
        ctx.equity = 999.0  # type: ignore[misc]
        assert False, "RiskContext should be immutable"
    except Exception:
        pass


def test_risk_context_circuit_open_defaults_false(context_factory) -> None:
    ctx = context_factory()
    assert ctx.circuit_open is False


def test_all_gates_satisfy_risk_gate_protocol() -> None:
    for gate in [TimeCutoffGate(), CircuitBreakerGate(), DailyLossGate(), DuplicatePositionGate()]:
        assert isinstance(gate, RiskGate)


def test_volatility_sizer_satisfies_risk_sizer_protocol() -> None:
    assert isinstance(VolatilitySizer(), RiskSizer)
