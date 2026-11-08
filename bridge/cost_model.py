"""
Indian charges cost model for STYX.
Dated, sourced configuration. Validate against hand calculations in Gate 2.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal


@dataclass(frozen=True)
class IndianChargesConfig:
    """Indian market charges configuration with dated sources."""
    as_of: str  # ISO date when rates were verified
    source: str  # URL or document reference

    # Brokerage (example: flat fee capped at percentage)
    brokerage_flat_inr: Decimal = Decimal("20.0")
    brokerage_pct_cap: Decimal = Decimal("0.0003")  # 0.03%

    # STT (Securities Transaction Tax)
    stt_equity_delivery_pct: Decimal = Decimal("0.001")  # 0.1% on sell side
    stt_equity_intraday_pct: Decimal = Decimal("0.00025")  # 0.025% on sell side
    stt_futures_pct: Decimal = Decimal("0.0001")  # 0.01% on sell side
    stt_options_pct: Decimal = Decimal("0.0005")  # 0.05% on sell side (premium)

    # Exchange transaction charges
    exchange_charges_equity_pct: Decimal = Decimal("0.0000345")  # NSE
    exchange_charges_futures_pct: Decimal = Decimal("0.00002")  # NSE
    exchange_charges_options_pct: Decimal = Decimal("0.00005")  # NSE

    # SEBI fees
    sebi_fees_pct: Decimal = Decimal("0.000001")  # Rs 1 per crore

    # Stamp duty (varies by state, using Maharashtra as example)
    stamp_duty_delivery_pct: Decimal = Decimal("0.00015")  # 0.015%
    stamp_duty_intraday_pct: Decimal = Decimal("0.00003")  # 0.003%
    stamp_duty_futures_pct: Decimal = Decimal("0.00002")  # 0.002%
    stamp_duty_options_pct: Decimal = Decimal("0.00003")  # 0.003%

    # GST (18% on brokerage + exchange charges + SEBI fees)
    gst_pct: Decimal = Decimal("0.18")

    # Slippage model (basis points)
    slippage_bps: Decimal = Decimal("5")  # 5 bps default


@dataclass(frozen=True)
class TradeLeg:
    """Single trade leg for cost calculation."""
    symbol: str
    side: Literal["BUY", "SELL"]
    quantity: int
    price: Decimal
    instrument_type: Literal["EQUITY", "FUTURE", "OPTION"]
    product_type: Literal["DELIVERY", "INTRADAY"] = "INTRADAY"


def calculate_brokerage(turnover: Decimal, config: IndianChargesConfig) -> Decimal:
    """Calculate brokerage: min(flat, turnover * pct_cap)."""
    pct_brokerage = turnover * config.brokerage_pct_cap
    return min(config.brokerage_flat_inr, pct_brokerage)


def calculate_stt(leg: TradeLeg, config: IndianChargesConfig) -> Decimal:
    """Calculate STT based on instrument and product type."""
    turnover = leg.quantity * leg.price
    if leg.instrument_type == "EQUITY":
        if leg.product_type == "DELIVERY":
            return turnover * config.stt_equity_delivery_pct if leg.side == "SELL" else Decimal("0")
        else:  # INTRADAY
            return turnover * config.stt_equity_intraday_pct if leg.side == "SELL" else Decimal("0")
    elif leg.instrument_type == "FUTURE":
        return turnover * config.stt_futures_pct if leg.side == "SELL" else Decimal("0")
    elif leg.instrument_type == "OPTION":
        return turnover * config.stt_options_pct if leg.side == "SELL" else Decimal("0")
    return Decimal("0")


def calculate_exchange_charges(leg: TradeLeg, config: IndianChargesConfig) -> Decimal:
    """Calculate exchange transaction charges."""
    turnover = leg.quantity * leg.price
    if leg.instrument_type == "EQUITY":
        return turnover * config.exchange_charges_equity_pct
    elif leg.instrument_type == "FUTURE":
        return turnover * config.exchange_charges_futures_pct
    elif leg.instrument_type == "OPTION":
        return turnover * config.exchange_charges_options_pct
    return Decimal("0")


def calculate_sebi_fees(turnover: Decimal, config: IndianChargesConfig) -> Decimal:
    """Calculate SEBI fees."""
    return turnover * config.sebi_fees_pct


def calculate_stamp_duty(leg: TradeLeg, config: IndianChargesConfig) -> Decimal:
    """Calculate stamp duty (on buy side for delivery, both sides for intraday/F&O)."""
    turnover = leg.quantity * leg.price
    if leg.instrument_type == "EQUITY":
        if leg.product_type == "DELIVERY":
            return turnover * config.stamp_duty_delivery_pct if leg.side == "BUY" else Decimal("0")
        else:  # INTRADAY
            return turnover * config.stamp_duty_intraday_pct
    elif leg.instrument_type == "FUTURE":
        return turnover * config.stamp_duty_futures_pct
    elif leg.instrument_type == "OPTION":
        return turnover * config.stamp_duty_options_pct
    return Decimal("0")


def calculate_gst(brokerage: Decimal, exchange_charges: Decimal, sebi_fees: Decimal, config: IndianChargesConfig) -> Decimal:
    """Calculate GST on brokerage + exchange charges + SEBI fees."""
    return (brokerage + exchange_charges + sebi_fees) * config.gst_pct


def calculate_slippage(leg: TradeLeg, config: IndianChargesConfig) -> Decimal:
    """Calculate slippage cost in INR."""
    turnover = leg.quantity * leg.price
    return turnover * (config.slippage_bps / Decimal("10000"))


def calculate_total_costs(legs: list[TradeLeg], config: IndianChargesConfig) -> dict:
    """Calculate all costs for a list of trade legs."""
    total_turnover = sum(leg.quantity * leg.price for leg in legs)
    total_brokerage = sum(calculate_brokerage(leg.quantity * leg.price, config) for leg in legs)
    total_stt = sum(calculate_stt(leg, config) for leg in legs)
    total_exchange = sum(calculate_exchange_charges(leg, config) for leg in legs)
    total_sebi = sum(calculate_sebi_fees(leg.quantity * leg.price, config) for leg in legs)
    total_stamp = sum(calculate_stamp_duty(leg, config) for leg in legs)
    total_gst = calculate_gst(total_brokerage, total_exchange, total_sebi, config)
    total_slippage = sum(calculate_slippage(leg, config) for leg in legs)

    total_costs = total_brokerage + total_stt + total_exchange + total_sebi + total_stamp + total_gst + total_slippage

    return {
        "turnover": total_turnover,
        "brokerage": total_brokerage,
        "stt": total_stt,
        "exchange_charges": total_exchange,
        "sebi_fees": total_sebi,
        "stamp_duty": total_stamp,
        "gst": total_gst,
        "slippage": total_slippage,
        "total_costs": total_costs,
        "costs_as_pct_of_turnover": (total_costs / total_turnover * Decimal("100")) if total_turnover > 0 else Decimal("0"),
    }


def calculate_double_cost_check(legs: list[TradeLeg], config: IndianChargesConfig) -> dict:
    """Calculate costs with 2x slippage for sensitivity check."""
    double_config = IndianChargesConfig(
        as_of=config.as_of,
        source=config.source,
        brokerage_flat_inr=config.brokerage_flat_inr,
        brokerage_pct_cap=config.brokerage_pct_cap,
        stt_equity_delivery_pct=config.stt_equity_delivery_pct,
        stt_equity_intraday_pct=config.stt_equity_intraday_pct,
        stt_futures_pct=config.stt_futures_pct,
        stt_options_pct=config.stt_options_pct,
        exchange_charges_equity_pct=config.exchange_charges_equity_pct,
        exchange_charges_futures_pct=config.exchange_charges_futures_pct,
        exchange_charges_options_pct=config.exchange_charges_options_pct,
        sebi_fees_pct=config.sebi_fees_pct,
        stamp_duty_delivery_pct=config.stamp_duty_delivery_pct,
        stamp_duty_intraday_pct=config.stamp_duty_intraday_pct,
        stamp_duty_futures_pct=config.stamp_duty_futures_pct,
        stamp_duty_options_pct=config.stamp_duty_options_pct,
        gst_pct=config.gst_pct,
        slippage_bps=config.slippage_bps * 2,  # Double slippage
    )
    return calculate_total_costs(legs, double_config)


# Default configuration (UPDATE WITH DATED SOURCES BEFORE GATE 2)
DEFAULT_CONFIG = IndianChargesConfig(
    as_of="2026-11-08",
    source="UNVERIFIED - Update with actual broker schedule and regulatory circulars",
    # These are placeholder values - MUST be verified and sourced before Gate 2
)