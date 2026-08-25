"""Tests for sizer.py — VolatilitySizer, calculate_quantity."""

from __future__ import annotations

from trading_risk_sdk.sizer import VolatilitySizer, calculate_quantity


def test_sizer_basic_quantity() -> None:
    # equity=100_000, risk=1%, stop=50 → 100_000 * 0.01 / 50 = 20
    assert calculate_quantity(stop_distance=50, equity=100_000, risk_pct=1.0) == 20


def test_sizer_rounds_down_fractional() -> None:
    # 100_000 * 0.01 / 60 = 16.6... → floor → 16
    assert calculate_quantity(stop_distance=60, equity=100_000, risk_pct=1.0) == 16


def test_sizer_lot_size_rounds_down_to_lot() -> None:
    # raw=37, lot=25 → 37 // 25 * 25 = 25
    qty = calculate_quantity(stop_distance=27, equity=100_000, risk_pct=1.0, lot_size=25)
    assert qty == 25


def test_sizer_lot_size_below_one_lot_returns_zero() -> None:
    qty = calculate_quantity(stop_distance=84, equity=100_000, risk_pct=1.0, lot_size=25)
    assert qty == 0


def test_sizer_zero_stop_distance_returns_zero() -> None:
    assert calculate_quantity(stop_distance=0, equity=100_000, risk_pct=1.0) == 0


def test_sizer_negative_stop_distance_returns_zero() -> None:
    assert calculate_quantity(stop_distance=-5, equity=100_000, risk_pct=1.0) == 0


def test_sizer_very_small_equity_returns_zero() -> None:
    assert calculate_quantity(stop_distance=100, equity=0.5, risk_pct=1.0) == 0


def test_sizer_no_lot_size_returns_raw() -> None:
    qty = calculate_quantity(stop_distance=10, equity=100_000, risk_pct=1.0, lot_size=None)
    assert qty == 100


def test_sizer_notional_cap_binds_when_entry_price_set() -> None:
    # raw = floor(100_000 * 0.01 / 1.0) = 1000, but the 20% notional cap at
    # entry_price=1000 allows only floor(100_000 * 0.20 / 1000) = 20.
    qty = calculate_quantity(
        stop_distance=1.0, equity=100_000, risk_pct=1.0, entry_price=1000.0
    )
    assert qty == 20


def test_sizer_notional_cap_does_not_bind_when_risk_qty_already_smaller() -> None:
    # raw = 20 (same as test_sizer_basic_quantity); notional cap at
    # entry_price=100 allows floor(100_000 * 0.20 / 100) = 200, well above raw,
    # so the risk-based quantity is unaffected.
    qty = calculate_quantity(
        stop_distance=50, equity=100_000, risk_pct=1.0, entry_price=100.0
    )
    assert qty == 20


def test_sizer_zero_entry_price_skips_notional_cap() -> None:
    # entry_price=0.0 (the default) must not apply any notional cap at all —
    # this is the branch every existing test before this one exercised.
    qty = calculate_quantity(stop_distance=1.0, equity=100_000, risk_pct=1.0, entry_price=0.0)
    assert qty == 1000


def test_volatility_sizer_applies_notional_cap_from_signal_entry_price(
    signal_factory, context_factory
) -> None:
    # End-to-end through VolatilitySizer.size(), the actual live call path —
    # every real strategy signal carries a non-zero entry_price.
    sizer = VolatilitySizer()
    signal = signal_factory(stop_distance=1.0, entry_price=1000.0)
    ctx = context_factory(equity=100_000.0, risk_per_trade_pct=1.0)
    assert sizer.size(signal, ctx) == 20


def test_volatility_sizer_size_delegates_to_calculate_quantity(signal_factory, context_factory) -> None:
    sizer = VolatilitySizer()
    signal = signal_factory(stop_distance=50.0)
    ctx = context_factory(equity=100_000.0, risk_per_trade_pct=1.0)
    assert sizer.size(signal, ctx) == 20


def test_volatility_sizer_respects_lot_size(signal_factory, context_factory) -> None:
    sizer = VolatilitySizer(lot_size=25)
    signal = signal_factory(stop_distance=27.0)
    ctx = context_factory(equity=100_000.0, risk_per_trade_pct=1.0)
    assert sizer.size(signal, ctx) == 25
