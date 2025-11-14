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


def test_nav_value_on_date_not_found(sample_nav_schedule):
    """Test that missing date raises ValueError."""
    # Use only first row to test missing date
    nav_df = sample_nav_schedule.head(1)
    with pytest.raises(ValueError, match="No NAV data available"):
        _nav_value_on_date(nav_df, datetime(2025, 12, 31))


def test_propose_fx_trades(sample_nav_schedule):
    """Test FX trade proposal generation."""
    nav_schedules = {"GBP": sample_nav_schedule.head(2)}  # Use first 2 rows
    fund_df = pd.DataFrame({"Base_Currency": ["EUR"]})

    trades = propose_fx_trades(nav_schedules, fund_df)

    assert len(trades) > 0
    assert "currency_pair" in trades.columns
    assert "notional_amount" in trades.columns
    assert all(trades["currency_pair"] == "GBP/EUR")
    assert all(trades["direction"] == "Sell")


def test_propose_fx_trades_missing_currency(sample_nav_schedule):
    """Test that missing currency raises ValueError."""
    nav_schedules = {"GBP": sample_nav_schedule.head(1)}
    fund_df = pd.DataFrame({"Base_Currency": ["EUR"]})
    # This test is no longer applicable since we auto-detect currencies
    # Instead, test that base currency is excluded
    trades = propose_fx_trades(nav_schedules, fund_df)
    assert len(trades) > 0
    assert all(trades["currency_pair"] == "GBP/EUR")


def test_propose_fx_trades_zero_notional_skipped():
    """Test that trades with zero notional are skipped."""
    nav_schedules = {
        "GBP": pd.DataFrame(
            {
                "Date": [datetime(2025, 9, 30)],
                "Net_Asset_Present_Value_Local": [0.0],
            }
        )
    }
    fund_df = pd.DataFrame({"Base_Currency": ["EUR"]})
    trades = propose_fx_trades(nav_schedules, fund_df)
    assert len(trades) == 0


def test_propose_fx_trades_auto_excludes_base_currency(sample_nav_schedule):
    """Test that base currency is automatically excluded from hedging."""
    nav_schedules = {"GBP": sample_nav_schedule.head(2), "EUR": sample_nav_schedule.head(2)}
    fund_df = pd.DataFrame({"Base_Currency": ["EUR"]})
    trades = propose_fx_trades(nav_schedules, fund_df)
    # Should only hedge GBP, not EUR
    assert len(trades) > 0
    assert all(trades["currency_pair"] == "GBP/EUR")
    assert "EUR/EUR" not in trades["currency_pair"].values


def test_propose_fx_trades_custom_base_currency(sample_nav_schedule):
    """Test that custom base currency works correctly."""
    nav_schedules = {"GBP": sample_nav_schedule.head(2), "USD": sample_nav_schedule.head(2)}
    fund_df = pd.DataFrame({"Base_Currency": ["USD"]})
    trades = propose_fx_trades(nav_schedules, fund_df)
    # Should hedge GBP against USD, not USD against itself
    assert len(trades) > 0
    assert all(trades["currency_pair"] == "GBP/USD")

