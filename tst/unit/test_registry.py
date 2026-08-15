"""Tests for trading_risk_sdk.registry"""

from __future__ import annotations

import pytest

from trading_risk_sdk.gates.circuit_breaker import CircuitBreakerGate
from trading_risk_sdk.gates.daily_loss import DailyLossGate
from trading_risk_sdk.gates.duplicate_position import DuplicatePositionGate
from trading_risk_sdk.gates.time_cutoff import TimeCutoffGate
from trading_risk_sdk.registry import create_gate, get_gate, registered_gates


def test_registered_gates_lists_all_four() -> None:
    assert registered_gates() == [
        "circuit_breaker",
        "daily_loss",
        "duplicate_position",
        "time_cutoff",
    ]


def test_get_gate_returns_class_not_instance() -> None:
    assert get_gate("time_cutoff") is TimeCutoffGate


def test_get_gate_unknown_id_raises_with_available_list() -> None:
    with pytest.raises(KeyError, match="does_not_exist"):
        get_gate("does_not_exist")


def test_create_gate_with_no_params() -> None:
    gate = create_gate("time_cutoff")
    assert isinstance(gate, TimeCutoffGate)


def test_create_gate_with_params_splatted_into_constructor() -> None:
    gate = create_gate("daily_loss", {"enabled": False})
    assert isinstance(gate, DailyLossGate)
    assert gate._enabled is False  # noqa: SLF001 -- verifying param actually reached the ctor


def test_create_gate_circuit_breaker_no_params() -> None:
    gate = create_gate("circuit_breaker")
    assert isinstance(gate, CircuitBreakerGate)


def test_create_gate_duplicate_position_no_params() -> None:
    gate = create_gate("duplicate_position")
    assert isinstance(gate, DuplicatePositionGate)


def test_create_gate_bad_param_name_raises_type_error() -> None:
    with pytest.raises(TypeError):
        create_gate("time_cutoff", {"nonexistent_param": 1})
