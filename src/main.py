from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.case_study import CaseStudyResult, run_case_study

pd.set_option("display.float_format", lambda x: f"{x:,.2f}")


def _write_outputs(result: CaseStudyResult, output_dir: Path) -> None:
    """
    Persist pipeline outputs to CSV files.
    """

    output_dir.mkdir(parents=True, exist_ok=True)

    currency_irrs_df = (
        pd.DataFrame(result.currency_irrs.items(), columns=["Currency", "IRR"])
        .sort_values("Currency")
    )
    currency_irrs_df["IRR"] = currency_irrs_df["IRR"].apply(lambda x: f"{x * 100:.3f}%")
    currency_irrs_df.to_csv(output_dir / "currency_irrs.csv", index=False)

    fund_irr_df = pd.DataFrame(
        [(result.fund_name, f"{result.fund_irr * 100:.3f}%")],
        columns=["Fund_Name", "IRR"],
    )
    fund_irr_df.to_csv(output_dir / "fund_irr.csv", index=False)

    for currency, schedule in result.nav_schedules.items():
        schedule.to_csv(
            output_dir / f"nav_schedule_{currency}.csv",
            index=False,
            float_format="%.2f",
        )

    result.fx_trades.to_csv(output_dir / "fx_forward_trades.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the CST case study analytics pipeline.")
    parser.add_argument(
        "--file",
        default="CST_Case_Study_data__1_.xlsx",
        help="Path to the Excel workbook containing the case study data.",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Directory where CSV outputs will be written.",
    )
    parser.add_argument(
        "--fund",
        default="Fund I",
        help="Name of the fund to analyse (default: Fund I).",
    )
    args = parser.parse_args()

    result = run_case_study(file_path=args.file, fund_name=args.fund)
    _write_outputs(result, Path(args.output_dir))


if __name__ == "__main__":
    main()