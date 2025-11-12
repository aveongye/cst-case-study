"""
NAV related calculations for the CST case study analytics.
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd

DAYS_IN_YEAR = 365.0


def calculate_net_asset_present_value(
    curr_df: pd.DataFrame,
    target_date: datetime,
    irr: float,
) -> float:
    """
    Present value of future cashflows beyond the target date.
    """

    future_cf = curr_df[curr_df["Date"] > target_date]
    if future_cf.empty:
        return 0.0

    present_value = 0.0
    for _, row in future_cf.iterrows():
        days_diff = (row["Date"] - target_date).days
        discount_factor = (1 + irr) ** (days_diff / DAYS_IN_YEAR)
        present_value += row["Cashflow_Amount_Local"] / discount_factor
    return present_value

def calculate_net_asset_value(
    curr_df: pd.DataFrame,
    target_date: datetime,
) -> float:
    """
    Value of future cashflows (principal + interest) beyond the target date, without discounting.
    """

    future_cf = curr_df[curr_df["Date"] > target_date]
    if future_cf.empty:
        return 0.0
    return float(future_cf["Cashflow_Amount_Local"].sum())


def generate_nav_schedule(
    fund_df: pd.DataFrame,
    currency_irrs: dict[str, float],
) -> dict[str, pd.DataFrame]:
    """
    Build NAV schedules grouped by currency.
    """

    schedules: dict[str, pd.DataFrame] = {}
    for currency, curr_df in fund_df.groupby("Local_Currency"):
        sorted_df = curr_df.sort_values("Date").reset_index(drop=True)
        irr = currency_irrs[currency]

        schedule_rows = []
        for current_date, rows_on_date in sorted_df.groupby("Date"):
            cashflow_amount = rows_on_date["Cashflow_Amount_Local"].sum()

            nav_present_value = calculate_net_asset_present_value(sorted_df, current_date, irr)
            nav_value = calculate_net_asset_value(sorted_df, current_date)

            schedule_rows.append(
                {
                    "Date": current_date,
                    "Cashflow_Local": cashflow_amount,
                    "Net_Asset_Value_Local": nav_value,
                    "Net_Asset_Present_Value_Local": nav_present_value,
                }
            )

        schedules[currency] = pd.DataFrame(schedule_rows)
    return schedules
