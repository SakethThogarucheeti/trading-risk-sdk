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
