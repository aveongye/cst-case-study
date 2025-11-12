"""
High-level orchestration for running the analytics flow
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import pandas as pd

from .metric_calculations.irr import (
    calculate_currency_irrs,
    calculate_fund_irr,
)
from .metric_calculations.nav import generate_nav_schedule
from .data.loader import read_excel, filter_by_fund
from .data.validation import validate_cashflows
from .hedging_strategies.fx_forwards import propose_fx_trades


@dataclass
class CaseStudyResult:
    fund_name: str
    currency_irrs: dict[str, float]
    fund_irr: float
    nav_schedules: dict[str, pd.DataFrame]
    fx_trades: pd.DataFrame


def run_case_study(
    file_path: Path | str,
    fund_name: str = "Fund I",
) -> CaseStudyResult:
    """
    Execute the end-to-end case study flow.
    """

    raw_df = read_excel(file_path)
    cashflows = validate_cashflows(raw_df)
    fund_df = filter_by_fund(cashflows, fund_name=fund_name)
    currency_irrs = calculate_currency_irrs(fund_df)
    fund_irr = calculate_fund_irr(fund_df)
    nav_schedules = generate_nav_schedule(fund_df, currency_irrs)
    fx_trades = propose_fx_trades(nav_schedules, currency_irrs)
    return CaseStudyResult(
        fund_name=fund_name,
        currency_irrs=currency_irrs,
        fund_irr=fund_irr,
        nav_schedules=nav_schedules,
        fx_trades=fx_trades,
    )


