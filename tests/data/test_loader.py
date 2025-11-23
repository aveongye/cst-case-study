"""
Tests for data loading utilities.
"""

import pandas as pd
import pytest

from src.case_study.data.loader import filter_by_fund

# Test constants
FUND_I = "Fund I"
FUND_II = "Fund II"
FUND_III = "Fund III"
EXPECTED_FUND_I_COUNT = 9  # All rows in sample_fund_df
EXPECTED_FUND_I_CASHFLOW_SUM = 9.75  # Sum of all cashflows in sample_fund_df


def test_filter_by_fund(sample_fund_df):
    """Test filtering by fund name."""
    # Add Fund_Name column to sample_fund_df for filtering test
    df = sample_fund_df.copy()
    df["Fund_Name"] = FUND_I
    
    # Add Fund II row to test multi-fund filtering
    fund_ii_row = pd.DataFrame({
        "Base_Currency": ["EUR"],
        "Local_Currency": ["GBP"],
        "Date": [sample_fund_df["Date"].iloc[0]],
        "Cashflow_Type": ["Investment"],
        "Cashflow_Amount_Local": [-200.0],
        "Cashflow_Amount_Base": [-228.0],
        "Fund_Name": [FUND_II],
    })
    df = pd.concat([df, fund_ii_row], ignore_index=True)
    
    result = filter_by_fund(df, FUND_I)
    assert len(result) == EXPECTED_FUND_I_COUNT
    assert all(result["Fund_Name"] == FUND_I)
    assert abs(result["Cashflow_Amount_Local"].sum() - EXPECTED_FUND_I_CASHFLOW_SUM) < 1e-6


def test_filter_by_fund_no_match(sample_fund_df):
    """Test filtering when no matching fund exists raises ValueError."""
    # Add Fund_Name column to sample_fund_df
    df = sample_fund_df.copy()
    df["Fund_Name"] = FUND_I
    
    with pytest.raises(ValueError, match=f"Fund '{FUND_III}' not found"):
        filter_by_fund(df, FUND_III)


def test_filter_by_fund_empty_dataframe():
    """Test filtering on empty DataFrame raises ValueError."""
    df = pd.DataFrame({"Fund_Name": [], "Date": [], "Cashflow_Amount_Local": []})
    with pytest.raises(ValueError, match="Cannot filter empty DataFrame"):
        filter_by_fund(df, FUND_I)



