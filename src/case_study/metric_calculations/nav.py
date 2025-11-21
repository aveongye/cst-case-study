"""
NAV related calculations for the CST case study analytics.
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd

DAYS_IN_YEAR = 365.0


def calculate_nav_at_time(
    curr_df: pd.DataFrame,
    target_date: datetime,
    irr: float,
) -> float:
    """
    Calculate Net Asset Value at time t as the present value of all remaining cashflows.
    
    Formula: NAV(t) = Σ (CF_t / (1 + r)^((t - t0) / 365))
    where:
    - NAV(t) is the Net Asset Value at time t
    - CF_t is the cashflow at time t
    - r is the currency IRR
    - t0 is the target date
    - t is the cashflow date
    
    Includes all cashflows occurring at or after the target date (both positive and negative).
    
    Args:
        curr_df: Complete cashflow schedule for the currency
        target_date: Valuation date
        irr: Currency-specific internal rate of return
        
    Returns:
        Net Asset Value (present value of all remaining cashflows at or after the target date)
    """
    remaining_cashflows = curr_df[curr_df["Date"] >= target_date]
    
    if remaining_cashflows.empty:
        return 0.0

    present_value = 0.0
    for _, row in remaining_cashflows.iterrows():
        days_diff = (row["Date"] - target_date).days
        discount_factor = (1 + irr) ** (days_diff / DAYS_IN_YEAR)
        present_value += row["Cashflow_Amount_Local"] / discount_factor
    
    # Round values very close to zero to exactly zero to handle floating point precision
    # Using 1e-4 threshold to catch floating point errors in NPV calculations
    if abs(present_value) < 1e-4:
        return 0.0
    
    return present_value


def generate_nav_schedule(
    fund_df: pd.DataFrame,
    currency_irrs: dict[str, float],
) -> dict[str, pd.DataFrame]:
    """
    Build NAV schedules grouped by currency.
    
    Each schedule contains the following columns:
    - Date: Reporting date
    - Net_Asset_Value_Local: NAV = Net Present Value of all remaining cashflows
    
    NAV(0) = 0 at the first date
    NAV(t) = NPV of all remaining cashflows at time t, for t > 0
    
    Args:
        fund_df: Cashflow data for the fund
        currency_irrs: Dictionary mapping currency codes to their IRRs
        
    Returns:
        Dictionary mapping currency codes to their NAV schedule DataFrames
    """
    schedules: dict[str, pd.DataFrame] = {}
    
    for currency, curr_df in fund_df.groupby("Local_Currency"):
        sorted_df = curr_df.sort_values("Date").reset_index(drop=True)
        irr = currency_irrs[currency]
        
        schedule_rows = []
        dates = sorted(sorted_df["Date"].unique())
        
        for current_date in dates:
            nav_present_value = calculate_nav_at_time(
                sorted_df, current_date, irr
            )

            schedule_rows.append(
                {
                    "Date": current_date,
                    "Net_Asset_Value_Local": nav_present_value,
                }
            )

        schedules[currency] = pd.DataFrame(schedule_rows)
    
    return schedules
