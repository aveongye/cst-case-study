"""
FX hedging utilities
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

import pandas as pd
from dateutil.relativedelta import relativedelta


@dataclass
class ForwardTrade:
    currency_pair: str
    trade_date: datetime
    delivery_date: datetime
    direction: str
    notional_currency: str
    notional_amount: float


def _nav_value_on_date(nav_df: pd.DataFrame, current_date: datetime) -> float:
    row = nav_df[nav_df["Date"] == current_date]
    if row.empty:
        raise ValueError(f"No NAV data available on {current_date}.")
    return float(row["Net_Asset_Value_Local"].iloc[0])


def propose_fx_trades(
    nav_schedules: dict[str, pd.DataFrame],
    fund_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Propose FX forward hedges aligned with NAV schedule dates.
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
        if currency not in nav_schedules:
            raise ValueError(f"NAV schedule for currency '{currency}' not available.")
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
            
            # Hedge based on NAV at delivery date (the exposure we're protecting)
            # This ensures perfect hedge coverage when the forward delivers
            notional_amount = _nav_value_on_date(nav_df, delivery_date)
            
            # Skip trades with zero or negative exposure
            if notional_amount <= 0 or abs(notional_amount) < 0.01:
                continue

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


