"""
Integration tests for the full pipeline.
"""

from datetime import datetime

import pandas as pd
import pytest

from src.case_study.run import run_case_study

# Expected structure constants (not values - those are tested in unit tests)
EXPECTED_NAV_SCHEDULE_DATES = {datetime(2025, 9, 30), datetime(2025, 12, 31), datetime(2026, 3, 31)}
EXPECTED_FX_TRADE_COLUMNS = {"currency_pair", "trade_date", "delivery_date", "direction", "notional_currency", "notional_amount"}


def test_run_case_study(sample_excel_file):
    """Test the full case study pipeline with multiple currencies."""
    result = run_case_study(file_path=sample_excel_file, fund_name="Fund I")

    # Verify basic result structure
    assert result.fund_name == "Fund I"
    assert isinstance(result.currency_irrs, dict)
    assert isinstance(result.fund_irr, float)
    assert isinstance(result.nav_schedules, dict)
    assert isinstance(result.fx_trades, pd.DataFrame)

    # Verify currency IRRs structure (values tested in test_irr.py)
    assert set(result.currency_irrs.keys()) == {"GBP", "USD", "EUR"}
    assert all(isinstance(irr, float) for irr in result.currency_irrs.values())

    # Verify fund IRR is a valid float (value tested in test_irr.py)
    assert isinstance(result.fund_irr, float)
    assert not (result.fund_irr == float("inf") or result.fund_irr == float("-inf"))

    # Verify NAV schedules structure (values tested in test_nav.py)
    assert set(result.nav_schedules.keys()) == {"GBP", "USD", "EUR"}
    for currency, schedule in result.nav_schedules.items():
        # Check columns
        assert list(schedule.columns) == ["Date", "Net_Asset_Value_Local"]
        # Check dates match expected cashflow dates
        assert set(schedule["Date"]) == EXPECTED_NAV_SCHEDULE_DATES
        # Check NAV(0) = 0 (first date should have NAV ≈ 0) - this is integration logic
        first_date_nav = schedule[schedule["Date"] == datetime(2025, 9, 30)]["Net_Asset_Value_Local"].iloc[0]
        assert abs(first_date_nav) < 1e-6
        # Check all NAV values are numeric
        assert schedule["Net_Asset_Value_Local"].dtype in ["float64", "float32"]

    # Verify FX trades structure (values tested in test_fx_forwards.py)
    assert len(result.fx_trades) > 0
    assert set(result.fx_trades.columns) == EXPECTED_FX_TRADE_COLUMNS
    # Verify only non-base currencies are hedged (GBP, USD, not EUR) - integration logic
    assert set(result.fx_trades["currency_pair"].unique()) == {"GBP/EUR", "USD/EUR"}
    assert "EUR/EUR" not in result.fx_trades["currency_pair"].values
    # Verify all trades are Sell direction
    assert all(result.fx_trades["direction"] == "Sell")
    # Verify trade dates are valid
    assert all(result.fx_trades["trade_date"] < result.fx_trades["delivery_date"])
    # Verify notional amounts are positive
    assert all(result.fx_trades["notional_amount"] > 0)

