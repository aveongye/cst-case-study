"""
Integration tests for the full pipeline.
"""

import pandas as pd
import pytest

from src.case_study.run import run_case_study


def test_run_case_study(sample_excel_file):
    """Test the full case study pipeline."""
    result = run_case_study(file_path=sample_excel_file, fund_name="Fund I")

    assert result.fund_name == "Fund I"
    assert isinstance(result.currency_irrs, dict)
    assert isinstance(result.fund_irr, float)
    assert "GBP" in result.nav_schedules
    assert len(result.fx_trades) > 0
    assert "currency_pair" in result.fx_trades.columns


def test_run_case_study_multiple_currencies(tmp_path, sample_fund_df_multi_currency):
    """Test pipeline with multiple currencies."""
    # Convert fund DataFrame to Excel format
    data = {
        "ID": list(range(1, len(sample_fund_df_multi_currency) + 1)),
        "Fund Name": ["Fund I"] * len(sample_fund_df_multi_currency),
        "Date": sample_fund_df_multi_currency["Date"].dt.strftime("%Y-%m-%d").tolist(),
        "Cashflow Type": sample_fund_df_multi_currency["Cashflow_Type"].tolist(),
        "Local Currency": sample_fund_df_multi_currency["Local_Currency"].tolist(),
        "Cashflow Amount Local": sample_fund_df_multi_currency["Cashflow_Amount_Local"].tolist(),
        "Cashflow Amount Base": sample_fund_df_multi_currency["Cashflow_Amount_Base"].tolist(),
        "Base Currency": ["EUR"] * len(sample_fund_df_multi_currency),
    }
    df = pd.DataFrame(data)
    file_path = tmp_path / "test_data_multi.xlsx"
    df.to_excel(file_path, index=False)

    result = run_case_study(file_path=file_path, fund_name="Fund I")

    assert "GBP" in result.nav_schedules
    assert "USD" in result.nav_schedules
    assert len(result.fx_trades) > 0

