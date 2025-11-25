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
from src.case_study.metric_calculations.irr import calculate_currency_irrs
from src.case_study.metric_calculations.nav import generate_nav_schedule

# Expected values based on sample_fund_df fixture
EXPECTED_GBP_IRR = 0.0514069002
EXPECTED_NAV_2025_12_31 = 101.2715460850
EXPECTED_GBP_TRADE_1_NOTIONAL = 100.0
EXPECTED_GBP_TRADE_2_NOTIONAL = 98.77
EXPECTED_USD_TRADE_1_NOTIONAL = 200.0
EXPECTED_USD_TRADE_2_NOTIONAL = 197.06


def test_nav_value_on_date(sample_fund_df):
    """Test NAV value lookup by date."""
    currency_irrs = calculate_currency_irrs(sample_fund_df)
    nav_schedules = generate_nav_schedule(sample_fund_df, currency_irrs)
    gbp_schedule = nav_schedules["GBP"]
    
    assert abs(_nav_value_on_date(gbp_schedule, datetime(2025, 12, 31)) - EXPECTED_NAV_2025_12_31) < 1e-6


def test_propose_fx_trades(sample_fund_df):
    """Test FX trade proposal generation with actual NAV schedules."""
    currency_irrs = calculate_currency_irrs(sample_fund_df)
    nav_schedules = generate_nav_schedule(sample_fund_df, currency_irrs)
    trades = propose_fx_trades(nav_schedules, sample_fund_df, currency_irrs)

    assert len(trades) == 4  # 2 GBP trades + 2 USD trades
    
    # Check GBP trades
    gbp_trades = trades[trades["currency_pair"] == "GBP/EUR"].sort_values("trade_date")
    assert len(gbp_trades) == 2
    assert gbp_trades.iloc[0]["trade_date"] == datetime(2025, 9, 30)
    assert gbp_trades.iloc[0]["delivery_date"] == datetime(2025, 12, 31)
    assert gbp_trades.iloc[0]["notional_amount"] == EXPECTED_GBP_TRADE_1_NOTIONAL
    assert gbp_trades.iloc[1]["trade_date"] == datetime(2025, 12, 31)
    assert gbp_trades.iloc[1]["delivery_date"] == datetime(2026, 3, 31)
    assert gbp_trades.iloc[1]["notional_amount"] == EXPECTED_GBP_TRADE_2_NOTIONAL
    
    # Check USD trades
    usd_trades = trades[trades["currency_pair"] == "USD/EUR"].sort_values("trade_date")
    assert len(usd_trades) == 2
    assert usd_trades.iloc[0]["notional_amount"] == EXPECTED_USD_TRADE_1_NOTIONAL
    assert usd_trades.iloc[1]["notional_amount"] == EXPECTED_USD_TRADE_2_NOTIONAL
    
    # All trades should be Sell
    assert all(trades["direction"] == "Sell")

def test_propose_fx_trades_auto_excludes_base_currency(sample_fund_df):
    """Test that base currency is automatically excluded from hedging."""
    currency_irrs = calculate_currency_irrs(sample_fund_df)
    nav_schedules = generate_nav_schedule(sample_fund_df, currency_irrs)
    trades = propose_fx_trades(nav_schedules, sample_fund_df, currency_irrs)
    
    # Should only hedge GBP and USD, not EUR (base currency)
    assert len(trades) == 4
    assert all(trades["currency_pair"].isin(["GBP/EUR", "USD/EUR"]))
    assert "EUR/EUR" not in trades["currency_pair"].values

