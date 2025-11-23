"""
IRR related calculations
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Iterable

from collections import OrderedDict, defaultdict
import pandas as pd
from xirr.math import xirr


def calculate_irr(cashflows: Iterable[float], dates: Iterable[date | datetime]) -> float:
    cashflow_list = list(cashflows)
    date_list = list(dates)

    if len(cashflow_list) != len(date_list):
        raise ValueError("Cashflows and dates must have the same length.")
    if not cashflow_list:
        raise ValueError("Cannot calculate IRR for an empty series.")

    aggregated = defaultdict(float)
    for dt, cf in zip(date_list, cashflow_list):
        aggregated[pd.Timestamp(dt).to_pydatetime()] += cf
    ordered = OrderedDict(sorted(aggregated.items(), key=lambda item: item[0]))
    return float(xirr(dict(ordered)))


def calculate_currency_irrs(fund_df: pd.DataFrame) -> dict[str, float]:
    """
    Calculate IRR per currency in the provided fund dataframe.
    
    Args:
        fund_df: DataFrame containing cashflow data with currency information (must be non-empty)
                Required columns are validated by Pydantic in validate_cashflows()
        
    Returns:
        Dictionary mapping currency codes to their IRRs
    """
    irrs: dict[str, float] = {}
    for currency, curr_df in fund_df.groupby("Local_Currency"):
        sorted_df = curr_df.sort_values("Date")
        cashflows = sorted_df["Cashflow_Amount_Local"].tolist()
        dates = sorted_df["Date"].tolist()
        irrs[currency] = calculate_irr(cashflows, dates)
    return irrs


def calculate_fund_irr(fund_df: pd.DataFrame) -> float:
    """
    Calculate the IRR of the fund in base currency.
    
    Args:
        fund_df: DataFrame containing cashflow data in base currency (must be non-empty)
                Required columns are validated by Pydantic in validate_cashflows()
        
    Returns:
        Fund-level IRR as a float
    """
    sorted_df = fund_df.sort_values("Date")
    return calculate_irr(sorted_df["Cashflow_Amount_Base"], sorted_df["Date"])


