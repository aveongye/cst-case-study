"""
Data models and validation logic
"""

from datetime import date, datetime
from typing import ClassVar, Iterable

from dateutil import parser
from pydantic import BaseModel, Field, ValidationError, field_validator


class CashflowRecord(BaseModel):
    """
    Normalized representation of a single cashflow entry.
    """

    ID: int
    Fund_Name: str = Field(alias="Fund Name")
    Date: datetime
    Cashflow_Type: str = Field(alias="Cashflow Type")
    Local_Currency: str = Field(alias="Local Currency")
    Cashflow_Amount_Local: float = Field(alias="Cashflow Amount Local")
    Cashflow_Amount_Base: float = Field(alias="Cashflow Amount Base")
    Base_Currency: str = Field(alias="Base Currency")

    _allowed_cashflow_types: ClassVar[tuple[str, ...]] = (
        "Investment",
        "Interest",
        "Principal Repayment",
    )
    _allowed_currencies: ClassVar[tuple[str, ...]] = ("GBP", "EUR", "USD")
    _currency_corrections: ClassVar[dict[str, str]] = {"GPB": "GBP"}

    @field_validator("Date", mode="before")
    @classmethod
    def _validate_date(cls, value: object) -> datetime:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            cleaned = value.strip().replace("`", "")
            return parser.parse(cleaned, dayfirst=True)
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time())
        raise TypeError(f"Unsupported date value: {value!r}")

    @field_validator("Cashflow_Type")
    @classmethod
    def _validate_cashflow_type(cls, value: str) -> str:
        if value not in cls._allowed_cashflow_types:
            raise ValueError(f"Invalid Cashflow_Type: {value}")
        return value

    @field_validator("Local_Currency", mode="before")
    @classmethod
    def _normalize_currency(cls, value: str) -> str:
        if value in cls._currency_corrections:
            return cls._currency_corrections[value]
        return value

    @field_validator("Local_Currency")
    @classmethod
    def _validate_currency(cls, value: str) -> str:
        if value not in cls._allowed_currencies:
            raise ValueError(f"Invalid Local_Currency: {value}")
        return value

    @field_validator("Base_Currency")
    @classmethod
    def _validate_base_currency(cls, value: str) -> str:
        if value != "EUR":
            raise ValueError("Base_Currency must be EUR")
        return value


