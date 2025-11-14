"""
Data loading utilities
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


def read_excel(path: Path | str) -> pd.DataFrame:
    """
    Read the raw Excel data into a dataframe.
    """

    return pd.read_excel(path)


def filter_by_fund(dataframe: pd.DataFrame, fund_name: str) -> pd.DataFrame:
    """
    Return only the rows belonging to the specified fund.
    """
    return dataframe.loc[dataframe["Fund_Name"] == fund_name]


