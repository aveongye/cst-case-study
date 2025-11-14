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


def test_calculate_irr(sample_fund_df):
    """Test IRR calculation."""
    cashflows = sample_fund_df["Cashflow_Amount_Local"].tolist()
    dates = sample_fund_df["Date"].tolist()
    irr = calculate_irr(cashflows, dates)
    assert 0.05 < irr < 0.06  # Around 5% return for 6 months


def test_calculate_irr_errors():
    """Test IRR error cases."""
    with pytest.raises(ValueError, match="empty"):
        calculate_irr([], [])
    
    with pytest.raises(ValueError, match="same length"):
        calculate_irr([-100.0, 110.0], [datetime(2025, 1, 1)])


def test_calculate_currency_irrs(sample_fund_df):
    """Test currency IRR calculation."""
    irrs = calculate_currency_irrs(sample_fund_df)
    assert "GBP" in irrs
    assert 0.0 < irrs["GBP"] < 1.0


def test_calculate_currency_irrs_multiple_currencies(sample_fund_df_multi_currency):
    """Test IRR calculation for multiple currencies."""
    irrs = calculate_currency_irrs(sample_fund_df_multi_currency)
    assert "GBP" in irrs
    assert "USD" in irrs
    assert 0.0 < irrs["GBP"] < 1.0
    assert 0.0 < irrs["USD"] < 1.0


def test_calculate_currency_irrs_missing_columns():
    """Test missing columns raises error."""
    df = pd.DataFrame({"Local_Currency": ["GBP"], "Date": [datetime(2025, 1, 1)]})
    with pytest.raises(ValueError, match="Missing required columns"):
        calculate_currency_irrs(df)


def test_calculate_fund_irr(sample_fund_df):
    """Test fund IRR calculation."""
    irr = calculate_fund_irr(sample_fund_df)
    assert isinstance(irr, float)
    assert 0.0 < irr < 1.0


def test_calculate_fund_irr_missing_columns():
    """Test missing columns raises error."""
    df = pd.DataFrame({"Date": [datetime(2025, 1, 1)]})
    with pytest.raises(ValueError, match="Missing required columns"):
        calculate_fund_irr(df)

