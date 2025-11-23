"""
Tests for NAV calculation functions.
"""

from datetime import datetime

import pandas as pd
import pytest

from src.case_study.metric_calculations.nav import (
    calculate_nav_at_time,
    generate_nav_schedule,
)

# Expected values based on sample_fund_df fixture
EXPECTED_NAV_2025_12_31 = 101.2715460850
EXPECTED_NAV_FINAL = 100.0


def test_calculate_nav_at_time_initial_date(sample_fund_df):
    """Test NAV calculation at initial date with actual IRR."""
    from src.case_study.metric_calculations.irr import calculate_currency_irrs
    
    gbp_df = sample_fund_df[sample_fund_df["Local_Currency"] == "GBP"]
    irrs = calculate_currency_irrs(sample_fund_df)
    result = calculate_nav_at_time(gbp_df, datetime(2025, 9, 30), irrs["GBP"])
    # NAV(0) should be 0 (IRR makes NPV = 0)
    assert abs(result) < 1e-6


def test_calculate_nav_at_time_final_date(sample_fund_df):
    """Test NAV calculation at final date with actual IRR."""
    from src.case_study.metric_calculations.irr import calculate_currency_irrs
    
    gbp_df = sample_fund_df[sample_fund_df["Local_Currency"] == "GBP"]
    irrs = calculate_currency_irrs(sample_fund_df)
    last_date = gbp_df["Date"].max()
    result = calculate_nav_at_time(gbp_df, last_date, irrs["GBP"])
    assert abs(result - EXPECTED_NAV_FINAL) < 1e-6


def test_generate_nav_schedule(sample_fund_df):
    """Test NAV schedule generation with actual calculated IRRs."""
    from src.case_study.metric_calculations.irr import calculate_currency_irrs
    
    currency_irrs = calculate_currency_irrs(sample_fund_df)
    schedules = generate_nav_schedule(sample_fund_df, currency_irrs)

    assert set(schedules.keys()) == {"GBP", "USD", "EUR"}
    
    # Check GBP schedule with actual values
    gbp_schedule = schedules["GBP"]
    assert len(gbp_schedule) == 3
    assert list(gbp_schedule.columns) == ["Date", "Net_Asset_Value_Local"]
    assert abs(gbp_schedule.iloc[0]["Net_Asset_Value_Local"]) < 1e-6
    assert abs(gbp_schedule.iloc[1]["Net_Asset_Value_Local"] - EXPECTED_NAV_2025_12_31) < 1e-6
    assert abs(gbp_schedule.iloc[2]["Net_Asset_Value_Local"] - EXPECTED_NAV_FINAL) < 1e-6

