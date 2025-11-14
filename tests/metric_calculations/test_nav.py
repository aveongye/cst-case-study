"""
Tests for NAV calculation functions.
"""

from datetime import datetime

import pandas as pd
import pytest

from src.case_study.metric_calculations.nav import (
    calculate_accrued_interest_local,
    calculate_cash_on_hand_local,
    calculate_cashflow_local,
    calculate_future_cashflows_present_value_local,
    calculate_loan_receivable_local,
    calculate_net_asset_present_value_local,
    calculate_net_asset_value_local,
    generate_nav_schedule,
)


def test_calculate_cashflow_local(sample_fund_df):
    """Test cashflow calculation."""
    rows = sample_fund_df.head(1)
    assert calculate_cashflow_local(rows) == -100.0


def test_calculate_loan_receivable_local(sample_fund_df):
    """Test loan receivable calculation."""
    # Investment increases principal
    investment_rows = sample_fund_df[sample_fund_df["Cashflow_Type"] == "Investment"]
    assert calculate_loan_receivable_local(0.0, investment_rows) == 100.0

    # Repayment decreases principal
    repayment_rows = sample_fund_df[sample_fund_df["Cashflow_Type"] == "Principal Repayment"]
    assert calculate_loan_receivable_local(100.0, repayment_rows) == 0.0

    # Never goes negative
    assert calculate_loan_receivable_local(50.0, repayment_rows) == 0.0


def test_calculate_cash_on_hand_local(sample_fund_df):
    """Test cash on hand accumulation."""
    interest_rows = sample_fund_df[sample_fund_df["Cashflow_Type"] == "Interest"]
    assert calculate_cash_on_hand_local(10.0, interest_rows) == 12.5

    # Negative cashflows ignored
    investment_rows = sample_fund_df[sample_fund_df["Cashflow_Type"] == "Investment"]
    assert calculate_cash_on_hand_local(10.0, investment_rows) == 10.0


def test_calculate_accrued_interest_local(sample_fund_df):
    """Test accrued interest calculation."""
    interest_rows = sample_fund_df[sample_fund_df["Cashflow_Type"] == "Interest"]
    assert calculate_accrued_interest_local(47.5, interest_rows) == 45.0

    # Never goes negative
    assert calculate_accrued_interest_local(2.0, interest_rows) == 0.0


def test_calculate_net_asset_value_local():
    """Test net asset value calculation."""
    result = calculate_net_asset_value_local(loan_receivable=100.0, cash_on_hand=20.0, accrued_interest=27.5)
    assert result == 147.5


def test_calculate_future_cashflows_present_value_local(sample_fund_df):
    """Test present value calculation."""
    result = calculate_future_cashflows_present_value_local(
        sample_fund_df, datetime(2025, 9, 30), 0.10
    )
    assert result > 0
    assert result < 105.0  # Less than undiscounted sum (100 principal + 2.5 interest)

    # No future cashflows
    last_date = sample_fund_df["Date"].max()
    assert calculate_future_cashflows_present_value_local(sample_fund_df, last_date, 0.10) == 0.0


def test_calculate_net_asset_present_value_local():
    """Test net asset present value calculation."""
    assert calculate_net_asset_present_value_local(100.0, 2.5) == 102.5


def test_generate_nav_schedule(sample_fund_df):
    """Test NAV schedule generation."""
    currency_irrs = {"GBP": 0.10}
    schedules = generate_nav_schedule(sample_fund_df, currency_irrs)

    assert "GBP" in schedules
    assert len(schedules["GBP"]) == 3
    assert "Net_Asset_Value_Local" in schedules["GBP"].columns
    assert "Net_Asset_Present_Value_Local" in schedules["GBP"].columns

