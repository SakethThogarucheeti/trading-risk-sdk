from __future__ import annotations

from datetime import UTC, datetime, time
from uuid import uuid4

import pytest
from trading_types.schemas import InstrumentType, Side, SignalEvent, SignalType

from trading_risk_sdk.policy import RiskContext

NOW = datetime(2024, 1, 1, 20, 0, tzinfo=UTC)
# 20:00 UTC == 01:30 IST the next day -- deliberately far from NOW.time() (20:00) so a gate that
# reads ctx.now.time() where ctx.now_local is required fails loudly instead of passing by
# coincidence (the old fixture's 10:00 UTC could pass either way undetected).
NOW_LOCAL = time(1, 30)
TODAY = NOW.date()


def make_signal(**overrides) -> SignalEvent:
    base = dict(
        signal_id=uuid4(),
        strategy_id="ema_cross",
        symbol="INFY",
        instrument_type=InstrumentType.EQUITY,
        side=Side.BUY,
        signal_type=SignalType.ENTRY,
        stop_distance=10.0,
        timestamp=NOW,
        tick_log_id=1,
    )
    return SignalEvent(**{**base, **overrides})


def make_context(**overrides) -> RiskContext:
    base = dict(
        now=NOW,
        now_local=NOW_LOCAL,
        today=TODAY,
        equity=100_000.0,
        max_daily_loss_pct=2.0,
        risk_per_trade_pct=1.0,
        cutoff=time(15, 30),
        realized_pnl=0.0,
        position=None,
        circuit_open=False,
    )
    return RiskContext(**{**base, **overrides})


@pytest.fixture
def signal_factory():
    return make_signal


@pytest.fixture
def context_factory():
    return make_context
