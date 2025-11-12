"""
Validation helpers 
"""

from __future__ import annotations

from typing import Iterable

import pandas as pd
from pydantic import ValidationError

from .models import CashflowRecord


def validate_records(rows: Iterable[dict]) -> list[CashflowRecord]:
    """
    Validate an iterable of raw rows and return the successfully parsed records.
    """

    records: list[CashflowRecord] = []
    for row in rows:
        try:
            records.append(CashflowRecord.model_validate(row))
        except ValidationError as exc:  # pragma: no cover - passthrough to caller
            raise ValidationError(  # type: ignore[call-arg]
                errors=exc.errors(include_context=True),
                model=CashflowRecord,
            ) from exc
    return records


def validate_cashflows(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate and normalize raw cashflow data into the expected schema.
    """

    records = validate_records(raw_df.to_dict(orient="records"))
    return pd.DataFrame([record.model_dump() for record in records])
