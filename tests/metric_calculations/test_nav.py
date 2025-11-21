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


def test_calculate_nav_at_time(sample_fund_df):
    """Test NAV calculation at time t."""
    result = calculate_nav_at_time(
        sample_fund_df, datetime(2025, 9, 30), 0.10
    )
    # Should include all cashflows at or after the target date (including negative investment)
    assert result < 0  # Investment is negative, so NPV should be negative initially

    # No remaining cashflows
    last_date = sample_fund_df["Date"].max()
    # At the last date, there should still be cashflows on that date
    result_last = calculate_nav_at_time(
        sample_fund_df, last_date, 0.10
    )
    assert result_last >= 0  # Final principal repayment should be positive


def test_generate_nav_schedule(sample_fund_df):
    """Test NAV schedule generation."""
    currency_irrs = {"GBP": 0.10}
    schedules = generate_nav_schedule(sample_fund_df, currency_irrs)

    assert "GBP" in schedules
    assert len(schedules["GBP"]) == 3
    assert "Date" in schedules["GBP"].columns
    assert "Net_Asset_Value_Local" in schedules["GBP"].columns
    
    # NAV should be calculated as NPV of remaining cashflows at all dates
    first_row = schedules["GBP"].iloc[0]
    # First date includes the initial negative investment, so NAV will be negative
    assert first_row["Net_Asset_Value_Local"] < 0

