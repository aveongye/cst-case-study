"""
Tests for data models and validation.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from src.case_study.data.models import CashflowRecord

# Test constants
FUND_I = "Fund I"
VALID_CURRENCY_GBP = "GBP"
INVALID_CURRENCY_JPY = "JPY"
INVALID_CURRENCY_TYPO_GPB = "GPB"
INVALID_BASE_CURRENCY_USD = "USD"
INVALID_CASHFLOW_TYPE = "Invalid"


def test_valid_record(base_cashflow_record):
    """Test that a valid record is accepted."""
    record = CashflowRecord.model_validate(base_cashflow_record)
    assert record.ID == 1
    assert record.Fund_Name == FUND_I
    assert record.Local_Currency == VALID_CURRENCY_GBP


def test_invalid_cashflow_type(base_cashflow_record):
    """Test that invalid cashflow type is rejected."""
    base_cashflow_record["Cashflow Type"] = INVALID_CASHFLOW_TYPE
    with pytest.raises(ValidationError):
        CashflowRecord.model_validate(base_cashflow_record)


def test_invalid_currency(base_cashflow_record):
    """Test that invalid currency is rejected."""
    base_cashflow_record["Local Currency"] = INVALID_CURRENCY_JPY
    with pytest.raises(ValidationError):
        CashflowRecord.model_validate(base_cashflow_record)


def test_invalid_base_currency(base_cashflow_record):
    """Test that non-EUR base currency is rejected."""
    base_cashflow_record["Base Currency"] = INVALID_BASE_CURRENCY_USD
    with pytest.raises(ValidationError):
        CashflowRecord.model_validate(base_cashflow_record)


def test_currency_correction(base_cashflow_record):
    """Test that GPB typo is corrected to GBP."""
    base_cashflow_record["Local Currency"] = INVALID_CURRENCY_TYPO_GPB
    record = CashflowRecord.model_validate(base_cashflow_record)
    assert record.Local_Currency == VALID_CURRENCY_GBP


def test_date_parsing(base_cashflow_record):
    """Test that various date formats are parsed correctly."""
    # String date
    record1 = CashflowRecord.model_validate(base_cashflow_record)
    assert isinstance(record1.Date, datetime)

    # Datetime object
    base_cashflow_record["Date"] = datetime(2025, 9, 30)
    record2 = CashflowRecord.model_validate(base_cashflow_record)
    assert isinstance(record2.Date, datetime)

