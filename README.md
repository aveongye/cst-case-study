# Case Study

This project provides an end-to-end analytics workflow for a fund case study. It processes raw cashflow data, validates it, computes key financial metrics (IRR and NAV), and proposes FX forward hedging trades to mitigate currency risk exposure.

The pipeline is modular, with clear separation between data handling, validation, metric calculations, and hedging strategy generation.

## Project structure

```
.
├── README.md
├── requirements.txt
├── outputs/                     # Generated output CSVs
├── CST_Case_Study_data__1_.xlsx # Input Excel dataset
└── src/
    ├── main.py                  # CLI entrypoint for running the pipeline
    └── case_study/
        ├── __init__.py
        ├── run.py               # Orchestration of the full case study workflow
        ├── data/
        │   ├── loader.py        # Data loading and filtering utilities
        │   ├── models.py        # Pydantic models defining schema validation
        │   └── validation.py    # Validation logic for raw data
        ├── metric_calculations/
        │   ├── irr.py           # IRR (Internal Rate of Return) calculations
        │   └── nav.py           # NAV (Net Asset Value) calculations
        └── hedging_strategies/
            └── fx_forwards.py   # FX Forward trade proposals for hedging

```

## Getting started

1. **Install dependencies** (Python 3.9+):
   ```bash
   python3 -m pip install -r requirements.txt
   ```
2. **Run from command line**:
   ```bash
   python3 -m src.main
   ```
   Arguments:

- `--file`: Path to the Excel workbook (default: `CST_Case_Study_data__1_.xlsx`)
- `--output-dir`: Output directory for CSVs (default: `outputs`)
- `--fund`: Name of the fund to analyse (default: `Fund I`)

## Outputs

Running the command generates the following CSV files:

- `currency_irrs.csv` – Currency-level IRRs in local currency
- `fund_irr.csv` – Fund-level IRR in base currency (EUR)
- `nav_schedule_<CURRENCY>.csv` – NAV schedule for each local currency
- `fx_forward_trades.csv` – Proposed FX hedge trades

## Notes on methodology

**NAV Schedule**

NAV = Net Asset Value = Fund Assets - Fund Liabilities

The NAV schedule is a quarter-by-quarter timeline showing the current value of each investment in its local currency (GBP, EUR, or USD).

`Net_Asset_Value_Local`: Net Asset Value (present value of all remaining cashflows)

**Proposed Hedge Strategy**

Fund I's GBP and USD investments are exposed to currency risk against the base EUR, as FX fluctuations can erode the EUR-equivalent value of these assets. To mitigate this, the strategy employs a 3-month rolling fair value hedge using FX forward contracts on GBP/EUR and USD/EUR pairs.

- Instrument: Foreign Currency / EUR Forwards
- Direction: Sell Foreign Currency / Buy EUR (locks in EUR value against Foreign Currency depreciation risks)
- Notional Basis: Foreign Currency Net Asset Present Value
- Hedge Ratio: 100% of outstanding NAV exposure
- Tenor: 3 months, rolled on each delivery date from NAV schedule
- Settlement: Net cash-settled; Offsets FX mark-to-market on fund's NAV
- Hedge Type: Fair value hedge (protects balance-sheet value rather than only cashflows)

## Testing

```bash
python3 -m pytest tests
```
