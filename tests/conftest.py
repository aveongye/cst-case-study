from datetime import datetime

import pandas as pd
import pytest


@pytest.fixture
def sample_fund_df():
    """
    Fund DataFrame with GBP, USD, and EUR cashflows.
    
    Note: This is the primary fixture used across all tests. It contains:
    - GBP: 3 cashflows (Investment, Interest, Principal Repayment)
    - USD: 3 cashflows (Investment, Interest, Principal Repayment)
    - EUR: 3 cashflows (Investment, Interest, Principal Repayment)
    - Base currency: EUR
    - Dates: 2025-09-30, 2025-12-31, 2026-03-31
    
    Works for both single and multi-currency tests. Single currency tests
    can filter to specific currencies when needed.
    """
    return pd.DataFrame(
        {
            "Base_Currency": ["EUR", "EUR", "EUR", "EUR", "EUR", "EUR", "EUR", "EUR", "EUR"],
            "Local_Currency": ["GBP", "GBP", "GBP", "USD", "USD", "USD", "EUR", "EUR", "EUR"],
            "Date": [
                datetime(2025, 9, 30), datetime(2025, 12, 31), datetime(2026, 3, 31),
                datetime(2025, 9, 30), datetime(2025, 12, 31), datetime(2026, 3, 31),
                datetime(2025, 9, 30), datetime(2025, 12, 31), datetime(2026, 3, 31),
            ],
            "Cashflow_Type": [
                "Investment", "Interest", "Principal Repayment",
                "Investment", "Interest", "Principal Repayment",
                "Investment", "Interest", "Principal Repayment",
            ],
            "Cashflow_Amount_Local": [-100.0, 2.5, 100.0, -200.0, 6.0, 200.0, -50.0, 1.25, 50.0],
            "Cashflow_Amount_Base": [-114.0, 2.86, 114.0, -228.0, 5.72, 228.0, -50.0, 1.25, 50.0],
        }
    )


@pytest.fixture
def sample_excel_file(tmp_path, sample_fund_df):
    """
    Temporary Excel file with sample fund data.
    
    Note: Creates a temporary Excel file for integration tests that need
    to test the full pipeline from file reading. The file contains
    multi-currency data (GBP, USD, EUR) with 9 cashflows total.
    """
    data = {
        "ID": range(1, len(sample_fund_df) + 1),
        "Fund Name": ["Fund I"] * len(sample_fund_df),
        "Date": sample_fund_df["Date"].dt.strftime("%Y-%m-%d").tolist(),
        "Cashflow Type": sample_fund_df["Cashflow_Type"].tolist(),
        "Local Currency": sample_fund_df["Local_Currency"].tolist(),
        "Cashflow Amount Local": sample_fund_df["Cashflow_Amount_Local"].tolist(),
        "Cashflow Amount Base": sample_fund_df["Cashflow_Amount_Base"].tolist(),
        "Base Currency": ["EUR"] * len(sample_fund_df),
    }
    df = pd.DataFrame(data)
    file_path = tmp_path / "test_data.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def base_cashflow_record():
    """
    Base valid cashflow record as a dictionary for Pydantic validation tests.
    
    Note: This fixture provides a valid cashflow record that tests can modify
    to test different validation scenarios. Each test modifies one field to
    test a specific validation rule (invalid cashflow type, invalid currency, etc.).
    """
    return {
        "ID": 1,
        "Fund Name": "Fund I",
        "Date": "2025-09-30",
        "Cashflow Type": "Investment",
        "Local Currency": "GBP",
        "Cashflow Amount Local": -100.0,
        "Cashflow Amount Base": -114.0,
        "Base Currency": "EUR",
    }
