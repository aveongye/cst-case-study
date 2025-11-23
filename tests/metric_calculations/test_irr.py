"""
Tests for IRR calculation functions.
"""

from datetime import datetime

import pandas as pd
import pytest

from src.case_study.metric_calculations.irr import (
    calculate_currency_irrs,
    calculate_fund_irr,
    calculate_irr,
)

# Expected values based on sample_fund_df fixture
EXPECTED_GBP_IRR = 0.0514069002
EXPECTED_USD_IRR = 0.0619986651
EXPECTED_EUR_IRR = 0.0514069002
EXPECTED_FUND_IRR = 0.0515682272


def test_calculate_irr(sample_fund_df):
    """Test IRR calculation with known cashflows."""
    gbp_df = sample_fund_df[sample_fund_df["Local_Currency"] == "GBP"]
    cashflows = gbp_df["Cashflow_Amount_Local"].tolist()
    dates = gbp_df["Date"].tolist()
    irr = calculate_irr(cashflows, dates)
    assert abs(irr - EXPECTED_GBP_IRR) < 1e-6


def test_calculate_irr_errors():
    """Test IRR error cases."""
    with pytest.raises(ValueError, match="empty"):
        calculate_irr([], [])
    
    with pytest.raises(ValueError, match="same length"):
        calculate_irr([-100.0, 110.0], [datetime(2025, 1, 1)])


def test_calculate_currency_irrs(sample_fund_df):
    """Test currency IRR calculation with expected values."""
    irrs = calculate_currency_irrs(sample_fund_df)
    assert set(irrs.keys()) == {"GBP", "USD", "EUR"}
    assert abs(irrs["GBP"] - EXPECTED_GBP_IRR) < 1e-6
    assert abs(irrs["USD"] - EXPECTED_USD_IRR) < 1e-6
    assert abs(irrs["EUR"] - EXPECTED_EUR_IRR) < 1e-6


def test_calculate_fund_irr(sample_fund_df):
    """Test fund IRR calculation with expected value."""
    irr = calculate_fund_irr(sample_fund_df)
    assert abs(irr - EXPECTED_FUND_IRR) < 1e-6



