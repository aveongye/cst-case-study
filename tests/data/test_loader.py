"""
Tests for data loading utilities.
"""

import pandas as pd
import pytest

from src.case_study.data.loader import filter_by_fund


def test_filter_by_fund():
    """Test filtering by fund name."""
    df = pd.DataFrame(
        {
            "Fund_Name": ["Fund I", "Fund I", "Fund II", "Fund I"],
            "Date": ["2025-09-30", "2025-12-31", "2025-09-30", "2026-03-31"],
            "Cashflow_Amount_Local": [-100, 2.5, -200, 2.5],
        }
    )

    result = filter_by_fund(df, "Fund I")
    assert len(result) == 3
    assert all(result["Fund_Name"] == "Fund I")
    assert result["Cashflow_Amount_Local"].sum() == -95.0


def test_filter_by_fund_no_match():
    """Test filtering when no matching fund exists raises ValueError."""
    df = pd.DataFrame(
        {
            "Fund_Name": ["Fund I", "Fund I"],
            "Date": ["2025-09-30", "2025-12-31"],
            "Cashflow_Amount_Local": [-100, 2.5],
        }
    )
    with pytest.raises(ValueError, match="Fund 'Fund III' not found"):
        filter_by_fund(df, "Fund III")


def test_filter_by_fund_empty_dataframe():
    """Test filtering on empty DataFrame raises ValueError."""
    df = pd.DataFrame({"Fund_Name": [], "Date": [], "Cashflow_Amount_Local": []})
    with pytest.raises(ValueError, match="Cannot filter empty DataFrame"):
        filter_by_fund(df, "Fund I")



