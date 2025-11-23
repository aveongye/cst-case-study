"""
Tests for FX forward hedging strategies.
"""

from datetime import datetime

import pandas as pd
import pytest

from src.case_study.hedging_strategies.fx_forwards import (
    _nav_value_on_date,
    propose_fx_trades,
)


def test_nav_value_on_date(sample_nav_schedule):
    """Test NAV value lookup."""
    assert _nav_value_on_date(sample_nav_schedule, datetime(2025, 12, 31)) == 102.5




def test_propose_fx_trades(sample_nav_schedule, sample_fund_df_multi_currency):
    """Test FX trade proposal generation."""
    nav_schedules = {"GBP": sample_nav_schedule}
    trades = propose_fx_trades(nav_schedules, sample_fund_df_multi_currency)

    assert len(trades) > 0
    assert "currency_pair" in trades.columns
    assert "notional_amount" in trades.columns
    assert all(trades["currency_pair"] == "GBP/EUR")
    assert all(trades["direction"] == "Sell")


def test_propose_fx_trades_missing_currency(sample_nav_schedule, sample_fund_df_multi_currency):
    """Test that trades are generated when NAV data is available."""
    nav_schedules = {"GBP": sample_nav_schedule}
    trades = propose_fx_trades(nav_schedules, sample_fund_df_multi_currency)
    assert len(trades) > 0
    assert all(trades["currency_pair"] == "GBP/EUR")


def test_propose_fx_trades_zero_notional_skipped(sample_fund_df_multi_currency):
    """Test that trades with zero or negative notional are skipped."""
    nav_schedules = {
        "GBP": pd.DataFrame(
            {
                "Date": [datetime(2025, 9, 30), datetime(2025, 12, 31)],
                "Net_Asset_Value_Local": [0.0, -100000.0],
            }
        )
    }
    # Create fund_df with zero cashflows for GBP
    fund_df = sample_fund_df_multi_currency.copy()
    fund_df.loc[fund_df["Local_Currency"] == "GBP", "Cashflow_Amount_Local"] = 0.0
    trades = propose_fx_trades(nav_schedules, fund_df)
    # First trade: NAV = 0.0, cashflow = 0.0, post-transaction = 0.0 (skipped)
    # Second trade would be on 2025-12-31 but NAV is -100k, so post-transaction = -100k (skipped)
    assert len(trades) == 0


def test_propose_fx_trades_auto_excludes_base_currency(sample_nav_schedule, sample_fund_df_multi_currency):
    """Test that base currency is automatically excluded from hedging."""
    nav_schedules = {"GBP": sample_nav_schedule, "EUR": sample_nav_schedule}
    trades = propose_fx_trades(nav_schedules, sample_fund_df_multi_currency)
    # Should only hedge GBP, not EUR
    assert len(trades) > 0
    assert all(trades["currency_pair"] == "GBP/EUR")
    assert "EUR/EUR" not in trades["currency_pair"].values


def test_propose_fx_trades_custom_base_currency(sample_nav_schedule, sample_fund_df_multi_currency):
    """Test that custom base currency works correctly."""
    nav_schedules = {"GBP": sample_nav_schedule, "USD": sample_nav_schedule}
    # Change base currency to USD
    fund_df = sample_fund_df_multi_currency.copy()
    fund_df["Base_Currency"] = "USD"
    trades = propose_fx_trades(nav_schedules, fund_df)
    # Should hedge GBP against USD, not USD against itself
    assert len(trades) > 0
    assert all(trades["currency_pair"] == "GBP/USD")

