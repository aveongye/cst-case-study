"""
FX hedging utilities
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
import pandas as pd

from ..constants import DAYS_IN_YEAR


@dataclass
class ForwardTrade:
    currency_pair: str
    trade_date: datetime
    delivery_date: datetime
    direction: str
    notional_currency: str
    notional_amount: float


def _nav_value_on_date(nav_df: pd.DataFrame, current_date: datetime) -> float:
    """
    Get NAV value on a specific date.
    """
    row = nav_df[nav_df["Date"] == current_date]
    return float(row["Net_Asset_Value_Local"].iloc[0])


def propose_fx_trades(
    nav_schedules: dict[str, pd.DataFrame],
    fund_df: pd.DataFrame,
    currency_irrs: dict[str, float],
) -> pd.DataFrame:
    """
    Propose FX forward hedges aligned with NAV schedule dates.
    
    Args:
        nav_schedules: Dictionary mapping currency codes to NAV schedule DataFrames
        fund_df: DataFrame containing fund cashflow data (must be non-empty and contain Base_Currency)
        currency_irrs: Dictionary mapping currency codes to their IRRs
        
    Returns:
        DataFrame containing proposed FX forward trades
    """
    base_currency = fund_df["Base_Currency"].iloc[0]
    
    all_dates = []
    for nav_df in nav_schedules.values():
        all_dates.extend(nav_df["Date"].tolist())
    if not all_dates:
        return pd.DataFrame()
    start_date = min(all_dates)
    end_date = max(all_dates)
    
    currencies_to_hedge = [c for c in nav_schedules.keys() if c != base_currency]

    trades: list[ForwardTrade] = []
    for currency in currencies_to_hedge:
        nav_df = nav_schedules[currency]
        nav_dates = [d for d in nav_df["Date"].sort_values() if start_date <= d <= end_date]
        if not nav_dates:
            continue

        for idx, trade_date in enumerate(nav_dates):
            # Determine delivery date (next NAV date)
            if idx + 1 < len(nav_dates):
                delivery_date = nav_dates[idx + 1]
            else:
                # Last trade: skip if it would create same-day forward
                # The final cashflow (principal repayment) ends the exposure,
                # so no forward hedge is needed beyond this date
                continue
            
            # Calculate notional as the NAV at delivery date expressed in terms of the trade date
            # The NAV at delivery_date is a present value (PV) at that date
            # We discount it back to trade_date to express it "in terms of" the trade date
            # Notional = NAV(delivery_date) / (1 + r)^(days/365)
            # where r is the currency IRR and days is from trade_date to delivery_date
            # Example: NAV at 2025-12-31 = £102,419,859.44, discounted to 2025-09-30 = £100,000,000.00
            nav_at_delivery_date = _nav_value_on_date(nav_df, delivery_date)
            
            # Skip trades with zero or negative NAV at delivery date
            if nav_at_delivery_date <= 0 or math.isclose(nav_at_delivery_date, 0.0, abs_tol=1e-6):
                continue
            
            irr = currency_irrs[currency]
            days_to_delivery = (delivery_date - trade_date).days
            discount_factor = (1 + irr) ** (days_to_delivery / DAYS_IN_YEAR)
            notional_amount = nav_at_delivery_date / discount_factor

            trades.append(
                ForwardTrade(
                    currency_pair=f"{currency}/{base_currency}",
                    trade_date=trade_date,
                    delivery_date=delivery_date,
                    direction="Sell",
                    notional_currency=currency,
                    notional_amount=round(notional_amount, 2),
                )
            )

    return pd.DataFrame([trade.__dict__ for trade in trades])


