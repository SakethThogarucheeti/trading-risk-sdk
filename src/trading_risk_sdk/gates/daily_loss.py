from __future__ import annotations

from trading_types.schemas import SignalEvent

from trading_risk_sdk.policy import RiskContext

_DAILY_LOSS_LIMIT = "DAILY_LOSS_LIMIT"


class DailyLossGate:
    """
    Rejects signals when today's realized PnL is a loss exceeding the configured max.

    A profitable day never trips this gate -- only a loss beyond the configured
    limit does, matching the gate's name/config field/docstring.

    Pass ``enabled=False`` (set by DI when paper_trading=True) to make this gate
    a pass-through without any conditional inside RiskFilter.
    """

    def __init__(self, enabled: bool = True) -> None:
        self._enabled = enabled

    async def check(self, event: SignalEvent, ctx: RiskContext) -> str | None:
        if not self._enabled:
            return None
        limit = ctx.equity * ctx.max_daily_loss_pct / 100.0
        if ctx.realized_pnl < -limit:
            return _DAILY_LOSS_LIMIT
        return None
