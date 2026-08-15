from __future__ import annotations

from trading_types.schemas import SignalEvent

from trading_risk_sdk.policy import RiskContext

_CIRCUIT_OPEN = "CIRCUIT_OPEN"


class CircuitBreakerGate:
    """
    Rejects signals when the market-data circuit breaker is open (stale feed).

    Pure gate — reads ``ctx.circuit_open`` rather than holding a live reference
    to a stateful circuit-breaker object. The caller is responsible for
    pre-fetching live circuit state into the RiskContext snapshot before
    running the gate chain, the same way it already pre-fetches
    ``realized_pnl``/``position``.
    """

    async def check(self, event: SignalEvent, ctx: RiskContext) -> str | None:
        if ctx.circuit_open:
            return _CIRCUIT_OPEN
        return None
