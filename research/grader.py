"""
Research loop: Grader v2 (R3).
Grades calls after the close using next-bar-open entry.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal
import pandas as pd


@dataclass(frozen=True)
class GradedCall:
    """A call with its graded outcome."""
    call_id: str
    symbol: str
    side: Literal["LONG", "SHORT"]
    entry_price: Decimal
    exit_price: Decimal
    exit_reason: Literal["TARGET", "STOP", "TIMEOUT", "NO_FILL"]
    net_r: Decimal  # Net of costs
    bars_held: int


def grade_call(
    call,
    bars: pd.DataFrame,
    costs_per_trade: Decimal,
) -> GradedCall:
    """
    Grade a call using next-bar-open entry.

    Rules:
    - Entry at next bar's open after signal
    - Check stop/target on each subsequent bar
    - If one bar touches both stop and target, stop counts
    - Exit at target, stop, or timeout (horizon bars)
    - Net R = (exit - entry - costs) / risk_per_share for LONG
    """
    # UNVERIFIED: Implementation depends on confirmed bar schema
    # This is a sketch for Gate 2 validation

    symbol = call.symbol
    side = call.side
    stop = Decimal(str(call.stop))
    target = Decimal(str(call.target))
    horizon = call.horizon_days

    # Filter bars for symbol
    symbol_bars = bars[bars["symbol"] == symbol].sort_values("ts_event")

    if len(symbol_bars) < 2:
        return GradedCall(
            call_id=call.id,
            symbol=symbol,
            side=side,
            entry_price=Decimal("0"),
            exit_price=Decimal("0"),
            exit_reason="NO_FILL",
            net_r=Decimal("0"),
            bars_held=0,
        )

    # Entry at next bar's open (bar index 1)
    entry_bar = symbol_bars.iloc[1]
    entry_price = Decimal(str(entry_bar["open"]))

    # Risk per share
    if side == "LONG":
        risk_per_share = entry_price - stop
    else:
        risk_per_share = stop - entry_price

    if risk_per_share <= 0:
        return GradedCall(
            call_id=call.id,
            symbol=symbol,
            side=side,
            entry_price=entry_price,
            exit_price=entry_price,
            exit_reason="NO_FILL",
            net_r=Decimal("0"),
            bars_held=0,
        )

    # Check subsequent bars for exit
    for i in range(2, min(len(symbol_bars), 2 + horizon)):
        bar = symbol_bars.iloc[i]
        high = Decimal(str(bar["high"]))
        low = Decimal(str(bar["low"]))
        close = Decimal(str(bar["close"]))

        if side == "LONG":
            # Check stop first (if both hit same bar, stop counts)
            if low <= stop:
                exit_price = stop
                exit_reason = "STOP"
                break
            if high >= target:
                exit_price = target
                exit_reason = "TARGET"
                break
        else:  # SHORT
            if high >= stop:
                exit_price = stop
                exit_reason = "STOP"
                break
            if low <= target:
                exit_price = target
                exit_reason = "TARGET"
                break
    else:
        # Timeout - exit at last bar's close
        last_bar = symbol_bars.iloc[min(len(symbol_bars) - 1, 1 + horizon)]
        exit_price = Decimal(str(last_bar["close"]))
        exit_reason = "TIMEOUT"

    # Calculate net R
    if side == "LONG":
        gross_r = (exit_price - entry_price) / risk_per_share
    else:
        gross_r = (entry_price - exit_price) / risk_per_share

    net_r = gross_r - (costs_per_trade / risk_per_share)
    bars_held = i - 1 if 'i' in locals() else horizon

    return GradedCall(
        call_id=call.id,
        symbol=symbol,
        side=side,
        entry_price=entry_price,
        exit_price=exit_price,
        exit_reason=exit_reason,
        net_r=net_r,
        bars_held=bars_held,
    )


if __name__ == "__main__":
    # Quick test with synthetic data
    import pandas as pd
    from research.calls import Call

    bars = pd.DataFrame({
        "symbol": ["RELIANCE"] * 10,
        "ts_event": pd.date_range("2026-11-01", periods=10, freq="D"),
        "open": [2500, 2505, 2510, 2520, 2530, 2540, 2550, 2560, 2570, 2580],
        "high": [2510, 2515, 2525, 2535, 2545, 2555, 2565, 2575, 2585, 2590],
        "low": [2495, 2500, 2505, 2515, 2525, 2535, 2545, 2555, 2565, 2575],
        "close": [2505, 2510, 2520, 2530, 2540, 2550, 2560, 2570, 2580, 2585],
        "volume": [1000000] * 10,
    })

    call = Call(
        id="test123",
        created_at="2026-11-01T09:00:00Z",
        origin="scan",
        symbol="RELIANCE",
        side="LONG",
        entry_rule="Close > 20EMA",
        stop=2490.0,
        target=2550.0,
        horizon_days=10,
        rationale="Test",
        snapshot_id="snap_test",
    )

    result = grade_call(call, bars, Decimal("0.001"))
    print(f"Graded: {result}")