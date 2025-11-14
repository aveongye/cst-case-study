"""
FX hedging utilities
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

import pandas as pd
from dateutil.relativedelta import relativedelta

DEFAULT_START_DATE = datetime(2025, 9, 30)
DEFAULT_END_DATE = datetime(2030, 9, 30)
DEFAULT_CURRENCIES = ("GBP", "USD")


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
    return float(row["Net_Asset_Present_Value_Local"].iloc[0])


def propose_fx_trades(
    nav_schedules: dict[str, pd.DataFrame],
    currencies_to_hedge: Iterable[str] = DEFAULT_CURRENCIES,
    start_date: datetime = DEFAULT_START_DATE,
    end_date: datetime = DEFAULT_END_DATE,
) -> pd.DataFrame:
    """
    Propose FX forward hedges aligned with NAV schedule dates.
    """

    trades: list[ForwardTrade] = []
    for currency in currencies_to_hedge:
        if currency not in nav_schedules:
            raise ValueError(f"NAV schedule for currency '{currency}' not available.")
        nav_df = nav_schedules[currency]
        nav_dates = [d for d in nav_df["Date"].sort_values() if start_date <= d <= end_date]
        if not nav_dates:
            continue

        for idx, trade_date in enumerate(nav_dates):
            notional_amount = _nav_value_on_date(nav_df, trade_date)
            if notional_amount == 0:
                continue
            if idx + 1 < len(nav_dates):
                delivery_date = nav_dates[idx + 1]
            else:
                delivery_date = min(trade_date + relativedelta(months=3), end_date)

            trades.append(
                ForwardTrade(
                    currency_pair=f"{currency}/EUR",
                    trade_date=trade_date,
                    delivery_date=delivery_date,
                    direction="Sell",
                    notional_currency=currency,
                    notional_amount=round(notional_amount, 2),
                )
            )

    return pd.DataFrame([trade.__dict__ for trade in trades])


