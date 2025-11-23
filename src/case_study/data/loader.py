"""
Data loading utilities
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_excel(path: Path | str) -> pd.DataFrame:
    """
    Read the raw Excel data into a dataframe.
    
    Args:
        path: Path to the Excel file
        
    Returns:
        DataFrame containing the Excel data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file cannot be read as Excel
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Excel file not found: {path}")
    
    try:
        return pd.read_excel(path)
    except Exception as e:
        raise ValueError(f"Failed to read Excel file {path}: {e}") from e


def filter_by_fund(dataframe: pd.DataFrame, fund_name: str) -> pd.DataFrame:
    """
    Return only the rows belonging to the specified fund.
    
    Args:
        dataframe: DataFrame containing fund data
        fund_name: Name of the fund to filter by
        
    Returns:
        DataFrame filtered to only include rows for the specified fund
        
    Raises:
        ValueError: If dataframe is empty or if the fund is not found in the data
    """
    if dataframe.empty:
        raise ValueError("Cannot filter empty DataFrame")
    
    filtered = dataframe.loc[dataframe["Fund_Name"] == fund_name]
    
    if filtered.empty:
        available_funds = sorted(dataframe["Fund_Name"].unique().tolist())
        raise ValueError(
            f"Fund '{fund_name}' not found. Available funds: {available_funds}"
        )
    
    return filtered


