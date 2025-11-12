# Client Success Team – Junior Software Engineer Case Study

This repository contains a Python solution that ingests the supplied Excel cashflow model, validates the
records with Pydantic, and produces Fund I analytics:

- Currency-level and fund-level IRR
- A NAV schedule per currency
- A 3‑month rolling FX forward hedge proposal sized to 100% of the NAV exposure

## Project structure

```
.
├── README.md
├── requirements.txt
├── src/
│   ├── case_study/
│   │   ├── __init__.py
│   │   ├── metric_calculations/
│   │   │   ├── irr.py
│   │   │   └── nav.py
│   │   ├── data/
│   │   │   ├── schema.py
│   │   │   └── validation.py
│   │   ├── hedging_strategies/
│   │   │   └── fx_forwards.py
│   │   ├── run.py
│   └── main.py
├── outputs/
└── CST_Case_Study_data__1_.xlsx
```

All analytics files are written to `outputs/` by default.

## Getting started

1. **Install dependencies** (Python 3.9+):
   ```bash
   python3 -m pip install -r requirements.txt
   ```
2. **Run the analytics pipeline** (silent run that exports CSV files):
   ```bash
   python3 -m src.main --file CST_Case_Study_data__1_.xlsx
   ```

Optional flags:

- `-f/--file PATH` – point to a different Excel workbook if needed.
- `-o/--output-dir DIR` – choose a custom directory for the generated CSV files.

## Outputs

Running the command generates the following CSV files:

- `currency_irrs.csv` – per-currency IRR values (local currency basis).
- `fund_irr.csv` – fund-level IRR in base currency (EUR).
- `nav_schedule_<CURRENCY>.csv` – NAV schedule for each local currency.
- `fx_forward_trades.csv` – hedge recommendations with trade and delivery dates and notionals.

## Data quality checks

The data validation step standardises column names, normalises currency codes (correcting typographical issues such as
`GPB` → `GBP`), drops incomplete rows, and validates types via Pydantic models before analytics are run. All
transformations are performed in-memory prior to analytics.

## Notes on methodology

- **IRR** values are computed with an XIRR implementation that supports irregular cashflow spacing.
- **NAV schedule** tracks cumulative local and base currency NAV per quarter and the share of total fund NAV per currency.
- **FX hedges** assume a 100% hedge ratio and roll forwards every three months, selling the foreign currency
  and buying the fund’s base currency (EUR) for outstanding NAV.

Feel free to adjust the hedging parameters (tenor, hedge ratio) within `case_study.hedging_strategies.fx_forwards.propose_fx_trades` to explore alternative strategies, or invoke `case_study.run_case_study(...)` directly from Python to consume the results programmatically.
