"""Tests for gates/ — TimeCutoffGate, CircuitBreakerGate, DailyLossGate, DuplicatePositionGate.

All four gates share one uniform pure shape: check(event, ctx) -> str | None.
"""

from __future__ import annotations

from datetime import time
from decimal import Decimal

from trading_types.schemas import Side, SignalType

from trading_risk_sdk.gates.circuit_breaker import CircuitBreakerGate
from trading_risk_sdk.gates.daily_loss import DailyLossGate
from trading_risk_sdk.gates.duplicate_position import DuplicatePositionGate
from trading_risk_sdk.gates.time_cutoff import TimeCutoffGate


class _Position:
    def __init__(self, net_qty: int) -> None:
        self.net_qty = net_qty
        self.avg_price = Decimal("100")


# ---------------------------------------------------------------------------
# TimeCutoffGate
# ---------------------------------------------------------------------------


async def test_time_cutoff_gate_rejects_after_cutoff(signal_factory, context_factory) -> None:
    gate = TimeCutoffGate()
    ctx = context_factory(cutoff=time(1, 0))  # now_local is 01:30 IST, past cutoff
    assert await gate.check(signal_factory(), ctx) == "AFTER_CUTOFF"


async def test_time_cutoff_gate_passes_before_cutoff(signal_factory, context_factory) -> None:
    # NOW (UTC) is 20:00 -- if the gate mistakenly read ctx.now.time() instead of
    # ctx.now_local (01:30 IST), a cutoff of 15:30 would incorrectly reject here.
    gate = TimeCutoffGate()
    ctx = context_factory(cutoff=time(15, 30))  # now_local is 01:30 IST, before cutoff
    assert await gate.check(signal_factory(), ctx) is None


# ---------------------------------------------------------------------------
# CircuitBreakerGate (pure form)
# ---------------------------------------------------------------------------


async def test_circuit_breaker_gate_rejects_when_open(signal_factory, context_factory) -> None:
    gate = CircuitBreakerGate()
    ctx = context_factory(circuit_open=True)
    assert await gate.check(signal_factory(), ctx) == "CIRCUIT_OPEN"


async def test_circuit_breaker_gate_passes_when_closed(signal_factory, context_factory) -> None:
    gate = CircuitBreakerGate()
    ctx = context_factory(circuit_open=False)
    assert await gate.check(signal_factory(), ctx) is None


# ---------------------------------------------------------------------------
# DailyLossGate
# ---------------------------------------------------------------------------


async def test_daily_loss_gate_rejects_when_limit_exceeded(signal_factory, context_factory) -> None:
    gate = DailyLossGate(enabled=True)
    ctx = context_factory(max_daily_loss_pct=2.0, realized_pnl=-5_000.0)  # limit=2_000
    assert await gate.check(signal_factory(), ctx) == "DAILY_LOSS_LIMIT"


async def test_daily_loss_gate_passes_under_limit(signal_factory, context_factory) -> None:
    gate = DailyLossGate(enabled=True)
    ctx = context_factory(max_daily_loss_pct=2.0, realized_pnl=-500.0)
    assert await gate.check(signal_factory(), ctx) is None


async def test_daily_loss_gate_does_not_reject_on_large_profit(signal_factory, context_factory) -> None:
    gate = DailyLossGate(enabled=True)
    ctx = context_factory(max_daily_loss_pct=2.0, realized_pnl=5_000.0)  # limit=2_000
    assert await gate.check(signal_factory(), ctx) is None


async def test_daily_loss_gate_disabled_always_passes(signal_factory, context_factory) -> None:
    gate = DailyLossGate(enabled=False)
    ctx = context_factory(max_daily_loss_pct=2.0, realized_pnl=-1_000_000.0)
    assert await gate.check(signal_factory(), ctx) is None


# ---------------------------------------------------------------------------
# DuplicatePositionGate
# ---------------------------------------------------------------------------


async def test_duplicate_position_gate_rejects_same_direction(signal_factory, context_factory) -> None:
    gate = DuplicatePositionGate()
    ctx = context_factory(position=_Position(net_qty=10))
    signal = signal_factory(side=Side.BUY, signal_type=SignalType.ENTRY)
    assert await gate.check(signal, ctx) == "ALREADY_IN_POSITION"


async def test_duplicate_position_gate_allows_opposite_direction(signal_factory, context_factory) -> None:
    gate = DuplicatePositionGate()
    ctx = context_factory(position=_Position(net_qty=10))
    signal = signal_factory(side=Side.SELL, signal_type=SignalType.ENTRY)
    assert await gate.check(signal, ctx) is None


async def test_duplicate_position_gate_passes_when_flat(signal_factory, context_factory) -> None:
    gate = DuplicatePositionGate()
    ctx = context_factory(position=None)
    signal = signal_factory(side=Side.BUY, signal_type=SignalType.ENTRY)
    assert await gate.check(signal, ctx) is None


async def test_duplicate_position_gate_ignores_exit_signals(signal_factory, context_factory) -> None:
    gate = DuplicatePositionGate()
    ctx = context_factory(position=_Position(net_qty=10))
    signal = signal_factory(side=Side.BUY, signal_type=SignalType.EXIT)
    assert await gate.check(signal, ctx) is None
