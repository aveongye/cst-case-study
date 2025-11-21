from datetime import datetime

import pandas as pd
import pytest


@pytest.fixture
def sample_fund_df():
    return pd.DataFrame(
        {
            "Local_Currency": ["GBP", "GBP", "GBP"],
            "Date": [datetime(2025, 9, 30), datetime(2025, 12, 31), datetime(2026, 3, 31)],
            "Cashflow_Type": ["Investment", "Interest", "Principal Repayment"],
            "Cashflow_Amount_Local": [-100.0, 2.5, 100.0],
            "Cashflow_Amount_Base": [-114.0, 2.86, 114.0],
        }
    )


@pytest.fixture
def sample_fund_df_multi_currency():
    return pd.DataFrame(
        {
            "Local_Currency": ["GBP", "GBP", "GBP", "USD", "USD", "USD"],
            "Date": [
                datetime(2025, 9, 30), datetime(2025, 12, 31), datetime(2026, 3, 31),
                datetime(2025, 9, 30), datetime(2025, 12, 31), datetime(2026, 3, 31),
            ],
            "Cashflow_Type": [
                "Investment", "Interest", "Principal Repayment",
                "Investment", "Interest", "Principal Repayment",
            ],
            "Cashflow_Amount_Local": [-100.0, 2.5, 100.0, -200.0, 5.0, 200.0],
            "Cashflow_Amount_Base": [-114.0, 2.86, 114.0, -228.0, 5.72, 228.0],
        }
    )


@pytest.fixture
def sample_excel_file(tmp_path):
    data = {
        "ID": [1, 2, 3],
        "Fund Name": ["Fund I", "Fund I", "Fund I"],
        "Date": ["2025-09-30", "2025-12-31", "2030-09-30"],
        "Cashflow Type": ["Investment", "Interest", "Principal Repayment"],
        "Local Currency": ["GBP", "GBP", "GBP"],
        "Cashflow Amount Local": [-100.0, 2.5, 100.0],
        "Cashflow Amount Base": [-114.0, 2.86, 114.0],
        "Base Currency": ["EUR", "EUR", "EUR"],
    }
    df = pd.DataFrame(data)
    file_path = tmp_path / "test_data.xlsx"
    df.to_excel(file_path, index=False)
    return file_path


@pytest.fixture
def sample_nav_schedule():
    return pd.DataFrame(
        {
            "Date": [datetime(2025, 9, 30), datetime(2025, 12, 31), datetime(2026, 3, 31)],
            "Net_Asset_Value_Local": [100.0, 102.5, 105.0],
        }
    )


@pytest.fixture
def base_cashflow_record():
    return {
        "ID": 1,
        "Fund Name": "Fund I",
        "Date": "2025-09-30",
        "Cashflow Type": "Investment",
        "Local Currency": "GBP",
        "Cashflow Amount Local": -100000000.0,
        "Cashflow Amount Base": -114573800.0,
        "Base Currency": "EUR",
    }
