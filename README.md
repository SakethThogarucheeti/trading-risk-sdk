# trading-risk-sdk

Pure risk-calculation toolkit for the trading platform: given a signal and a pre-fetched context snapshot, decide whether to reject it and how large to size it. Used by [trading-platform](https://github.com/SakethThogarucheeti/trading-platform) and reusable standalone — no database, broker, or DI dependency.

## Contents

- `trading_risk_sdk.policy` — `RiskGate`, `RiskSizer` Protocols, `RiskContext` (immutable snapshot, includes `circuit_open: bool`).
- `trading_risk_sdk.sizer` — `VolatilitySizer`, `calculate_quantity` (ATR-based position sizing).
- `trading_risk_sdk.gates` — `TimeCutoffGate`, `CircuitBreakerGate`, `DailyLossGate`, `DuplicatePositionGate`. All four gates share one uniform shape: `async def check(event: SignalEvent, ctx: RiskContext) -> str | None`.

No database, broker, or DI dependency. Every gate is a pure function of `(SignalEvent, RiskContext)` — including `CircuitBreakerGate`, which reads `ctx.circuit_open` rather than holding a live reference to a stateful circuit-breaker object. The caller (trading-platform's `RiskFilter`) is responsible for pre-fetching live state (realized PnL, open position, circuit-breaker status) into the `RiskContext` snapshot before running the gate chain — the same pattern already used for `realized_pnl`/`position`.

## Stack

- Python 3.13+, [uv](https://docs.astral.sh/uv/)
- Pydantic, [trading-types](https://github.com/SakethThogarucheeti/trading-types)

## Setup

```bash
uv sync
```

## Testing

```bash
uv run pytest
```
