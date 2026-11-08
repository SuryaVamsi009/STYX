"""
Tests for cost_model.py - Gate 2 accounting validation.
"""

import pytest
from decimal import Decimal
from bridge.cost_model import (
    IndianChargesConfig,
    TradeLeg,
    calculate_total_costs,
    calculate_double_cost_check,
    DEFAULT_CONFIG,
)


class TestCostModel:
    """Test Indian charges cost model against hand calculations."""

    def test_equity_intraday_buy_sell_roundtrip(self):
        """Test a simple equity intraday roundtrip."""
        config = IndianChargesConfig(
            as_of="2026-11-08",
            source="Test config",
            brokerage_flat_inr=Decimal("20"),
            brokerage_pct_cap=Decimal("0.0003"),
            stt_equity_intraday_pct=Decimal("0.00025"),
            exchange_charges_equity_pct=Decimal("0.0000345"),
            sebi_fees_pct=Decimal("0.000001"),
            stamp_duty_intraday_pct=Decimal("0.00003"),
            gst_pct=Decimal("0.18"),
            slippage_bps=Decimal("5"),
        )

        legs = [
            TradeLeg("RELIANCE", "BUY", 100, Decimal("2500"), "EQUITY", "INTRADAY"),
            TradeLeg("RELIANCE", "SELL", 100, Decimal("2510"), "EQUITY", "INTRADAY"),
        ]

        result = calculate_total_costs(legs, config)

        # Hand calculation:
        # Buy: 100 * 2500 = 250,000
        # Sell: 100 * 2510 = 251,000
        # Total turnover = 501,000
        #
        # Brokerage: min(20, 501000 * 0.0003) = min(20, 150.3) = 20 per leg = 40 total
        # STT: 251000 * 0.00025 = 62.75 (sell side only)
        # Exchange: 501000 * 0.0000345 = 17.2845
        # SEBI: 501000 * 0.000001 = 0.501
        # Stamp: (250000 + 251000) * 0.00003 = 15.03 (both sides intraday)
        # GST: 18% on (40 + 17.2845 + 0.501) = 18% * 57.7855 = 10.40139
        # Slippage: 501000 * 5/10000 = 250.5
        #
        # Total = 40 + 62.75 + 17.2845 + 0.501 + 15.03 + 10.40139 + 250.5 = 396.46689

        assert result["turnover"] == Decimal("501000")
        assert result["brokerage"] == Decimal("40")
        assert abs(result["stt"] - Decimal("62.75")) < Decimal("0.01")
        assert abs(result["total_costs"] - Decimal("396.47")) < Decimal("0.02")

    def test_double_cost_check(self):
        """Test double-cost sensitivity check."""
        config = IndianChargesConfig(
            as_of="2026-11-08",
            source="Test config",
            slippage_bps=Decimal("5"),
        )

        legs = [
            TradeLeg("RELIANCE", "BUY", 100, Decimal("2500"), "EQUITY", "INTRADAY"),
            TradeLeg("RELIANCE", "SELL", 100, Decimal("2510"), "EQUITY", "INTRADAY"),
        ]

        normal = calculate_total_costs(legs, config)
        double = calculate_double_cost_check(legs, config)

        # Double cost should have 2x slippage
        assert double["slippage"] == normal["slippage"] * 2
        assert double["total_costs"] > normal["total_costs"]

    def test_delivery_vs_intraday_stamp_duty(self):
        """Test stamp duty differs for delivery vs intraday."""
        config = IndianChargesConfig(
            as_of="2026-11-08",
            source="Test config",
            stamp_duty_delivery_pct=Decimal("0.00015"),
            stamp_duty_intraday_pct=Decimal("0.00003"),
        )

        delivery_legs = [
            TradeLeg("RELIANCE", "BUY", 100, Decimal("2500"), "EQUITY", "DELIVERY"),
        ]
        intraday_legs = [
            TradeLeg("RELIANCE", "BUY", 100, Decimal("2500"), "EQUITY", "INTRADAY"),
        ]

        delivery_result = calculate_total_costs(delivery_legs, config)
        intraday_result = calculate_total_costs(intraday_legs, config)

        # Delivery: stamp on buy side only at 0.015%
        # Intraday: stamp on both sides at 0.003%
        assert delivery_result["stamp_duty"] == Decimal("3.75")  # 250000 * 0.00015
        assert intraday_result["stamp_duty"] == Decimal("0.75")  # 250000 * 0.00003


if __name__ == "__main__":
    pytest.main([__file__, "-v"])