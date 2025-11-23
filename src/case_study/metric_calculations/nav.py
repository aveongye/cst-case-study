"""
NAV related calculations for the CST case study analytics.
"""

from __future__ import annotations

import math
from datetime import datetime

import pandas as pd

from ..constants import DAYS_IN_YEAR


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

    # Vectorized calculation for better performance
    days_diff = (remaining_cashflows["Date"] - target_date).dt.days
    discount_factors = (1 + irr) ** (days_diff / DAYS_IN_YEAR)
    present_value = (remaining_cashflows["Cashflow_Amount_Local"] / discount_factors).sum()
    
    # Use math.isclose() for robust floating-point comparison
    # abs_tol=1e-6 is appropriate for financial calculations (handles rounding errors)
    if math.isclose(present_value, 0.0, abs_tol=1e-6):
        return 0.0
    
    return float(present_value)


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
