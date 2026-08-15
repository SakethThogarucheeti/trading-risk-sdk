from __future__ import annotations

from trading_types.schemas import SignalEvent

from trading_risk_sdk.policy import RiskContext

_AFTER_CUTOFF = "AFTER_CUTOFF"


class TimeCutoffGate:
    """Rejects signals submitted after the intraday cutoff time."""

    async def check(self, event: SignalEvent, ctx: RiskContext) -> str | None:
        if ctx.now.time() > ctx.cutoff:
            return _AFTER_CUTOFF
        return None
