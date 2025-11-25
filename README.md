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

## Methodology

### IRR Calculation

**Internal Rate of Return (IRR)** is the discount rate $r$ that makes the net present value (NPV) of the entire cash flow stream zero when discounted to the initial date. It is solved numerically using the Newton-Raphson method on the equation:

$$\sum_{i=0}^{n} \frac{CF_i}{(1 + r)^{(d_i / 365)}} = 0$$

where:

- $CF_i$ is the cash flow at date $t_i$
- $d_i$ is the number of days from the initial date $t_0$ to $t_i$
- A 365-day year convention is used for the discount exponent
- $r$ is the IRR (discount rate)

**Calculation approach:**

- **Currency-level IRR**: Calculated separately for each currency using cashflows in that currency
- **Fund-level IRR**: Calculated using all cashflows converted to base currency (EUR)
- Solved numerically using the `xirr` library (implements Newton-Raphson method)

### NAV Calculation

**Net Asset Value (NAV)** at each date $t$ is the NPV of all remaining cash flows (including the cash flow at $t$) discounted to $t$ at the IRR:

$$NAV(t) = \sum_{j \geq k} \frac{CF_j}{(1 + r)^{(d_j / 365)}}$$

**Note:** NAV is calculated **pre-transaction**, meaning it reflects the value **before** the cashflow on date $t$ is received or paid.

where:

- $k$ is the index of date $t$
- $CF_j$ is the cash flow at future date $t_j$ (where $j \geq k$)
- $d_j$ is the number of days from $t$ to the future date $t_j$
- $r$ is the currency-specific IRR (discount rate)
- A 365-day year convention is used for the discount exponent

**Key properties:**

- **NAV($t_0$) = 0**: At the initial investment date, NAV is 0
- **NAV(t) for t > $t_0$**: Present value of all remaining cashflows (both positive and negative) from date $t$ onwards
- **Pre-transaction valuation**: NAV represents the fund's value before the cashflow on date $t$ is executed
- **Discount rate**: Uses the currency-specific IRR as the discount factor
- **Quarterly schedule**: NAV is calculated at each quarter-end date

#### NAV Schedule Example (GBP)

Below is the NAV schedule for GBP with detailed explanations for each value. All calculations use exact day counts between dates and the GBP IRR of ≈9.951%.

| Date       | NAV (GBP)      | Explanation                                                                                                                    |
| ---------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| 2025-09-30 | 0              | NPV of all 21 cash flows = -£100M investment + PV of 19 interest payments + PV of £100M principal = 0 by IRR definition.       |
| 2025-12-31 | 102,419,859.44 | NPV of remaining 20 cash flows = + £2.5M interest + PV of 18 interest payments + PV of £100M principal. See calculation below. |
| 2026-03-31 | 102,284,599.01 | NPV of remaining 19 cash flows = + £2.5M interest + PV of 17 interest payments + PV of £100M principal.                        |
| ...        | ...            | ...                                                                                                                            |
| 2030-03-31 | 100,296,797.88 | NPV of remaining 3 cash flows = + £2.5M interest + PV of 1 interest payments + PV of £100M principal.                          |
| 2030-06-30 | 100,137,314.24 | NPV of remaining 2 cash flows = + £2.5M interest + PV of £100M principal. See calculation below.                               |
| 2030-09-30 | 100,000,000.00 | Final cash flow (principal £100M) with no discounting.                                                                         |

**Example Calculations:**

**2025-12-31 (NAV ≈ £102,419,859.44):**

$$\text{NAV} = \frac{£2,500,000}{(1+0.09951)^{0/365}} + \sum_{i=1}^{18} \frac{£2,500,000}{(1+0.09951)^{d_i/365}} + \frac{£100,000,000}{(1+0.09951)^{1734/365}}$$

Where:

- £2,500,000 is the interest payment on 2025-12-31 (no discounting, same date)
- The sum represents 18 future interest payments of £2,500,000 each, discounted from their respective dates ($d_i$ days from 2025-12-31)
- £100,000,000 is the principal payment on 2030-09-30, discounted over 1,734 days at the GBP IRR of 9.951%

**2030-06-30 (NAV ≈ £100,137,314.24):**

$$\text{NAV} = \frac{£2,500,000}{(1+0.09951)^{0/365}} + \frac{£100,000,000}{(1+0.09951)^{92/365}} = £2,500,000 + \frac{£100,000,000}{1.0240} ≈ £100,137,314$$

Where:

- £2,500,000 is the interest payment on 2030-06-30 (no discounting, same date)
- £100,000,000 is the principal payment on 2030-09-30, discounted over 92 days (# days from 2030-06-30 to 2030-09-30) at the GBP IRR of 9.951%

**Key Observations:**

1. **Initial NAV = 0**: By IRR definition, the NPV of all cashflows at the investment date equals zero.

2. **NAV Growth Pattern**: After the initial date, NAV increases as the negative investment cashflow is excluded and the remaining positive cashflows are discounted over shorter periods.

3. **Gradual Decline**: As the investment matures, NAV gradually decreases because:

   - Interest payments are received (reducing future cashflows)
   - Principal repayment approaches (less discounting required)
   - Fewer high-value future cashflows remain

4. **Final NAV = Principal**: On the final date (2030-09-30), only the principal repayment remains, so NAV equals the principal amount (£100M) with no discounting.

### FX Forward Hedging Strategy

**Objective:** Eliminate currency risk exposure by hedging 100% of NAV exposure using FX forward contracts.

#### Strategy Overview

The fund holds investments in multiple currencies (GBP, USD) but reports in EUR. FX movements can erode the EUR-equivalent value of these assets. The hedging strategy uses **rolling 3-month FX forward contracts** to lock in exchange rates.

#### Hedge Mechanics

**1. Forward Contract Structure:**

- **Instrument**: FX Forward contracts (e.g., GBP/EUR, USD/EUR)
- **Direction**: Always `Sell` foreign currency / `Buy` base currency (EUR)
- **Purpose**: Lock in EUR value against foreign currency depreciation

**2. Notional Amount Logic**

The hedge notional is calculated by taking the **NAV at the delivery date** and discounting it back to the trade date using the currency IRR. This expresses the NAV exposure at delivery "in terms of" the trade date, accounting for the time value of money.

**Key Concept:**

- NAV at any date is already a present value (PV) of all remaining cashflows as of that date
- NAV(delivery_date) represents the PV of future cashflows as of the delivery date
- By discounting NAV(delivery_date) back to the trade date, we get the PV of those same cashflows as of the trade date, after settlement of all cashflow(s) on the trade date (i.e. The notional amount is conceptually similar to a "post-transaction NAV")
- This ensures the hedge notional reflects the economic exposure at the time the forward contract is entered, which is assumed to be EOD

**Formula:**

- Hedge Notional = NAV(delivery_date) / (1 + r)^(days/365)
- Where:
  - NAV(delivery_date) is the NAV at the delivery date (already a PV)
  - r is the currency-specific IRR
  - days is the number of days from trade_date to delivery_date

**Examples:**

- **Initial trade (2025-09-30, delivery 2025-12-31)**:

  - NAV at delivery date (2025-12-31) = £102,419,859.44 (PV of cashflows as of 2025-12-31)
  - Days to delivery = 92 days
  - GBP IRR = 9.951%
  - Notional = £102,419,859.44 / (1.09951)^(92/365) = £100,000,000.00
  - _Note: This equals the initial investment because discounting NAV(2025-12-31) back to 2025-09-30 gives the PV of future cashflows at 2025-09-30 after cashflow settlement (i.e. -£100M), which equals the initial investment amount. On 2025-09-30, the NAV exposure starts immediately after post investment outflow._

- **Subsequent trade (2025-12-31, delivery 2026-03-31)**:
  - NAV at delivery date (2026-03-31) = £102,284,599.01 (PV of cashflows as of 2026-03-31)
  - Days to delivery = 90 days
  - Notional = £102,284,599.01 / (1.09951)^(90/365) = £99,919,859.44
  - _This represents the PV (as of 2025-12-31) of the NAV exposure that will exist at 2026-03-31._

**3. Rolling Mechanism:**

- **Trade Date**: Enter forward on NAV date (e.g., 2025-09-30)
- **Delivery Date**: Next NAV date (e.g., 2025-12-31)
- **Rolling**: On delivery date, settle old forward and enter new forward
- **Continuous Coverage**: No gaps between contracts

**4. Hedge Effectiveness:**

- **Present value coverage**: Hedge notional = NAV(delivery_date) discounted to trade_date
- **Time value adjustment**: Accounts for the time value of money by discounting the delivery date NAV back to the trade date using the currency IRR
- **Mathematical consistency**: Since NAV is already a present value calculation, discounting it back maintains consistency with the NAV methodology
- **Hedge alignment**: The notional reflects the economic exposure (in present value terms) at the time the forward contract is entered

#### Example Trade Lifecycle

```
2025-09-30: Enter Forward 1
  - Trade Date: 2025-09-30
  - Delivery Date: 2025-12-31
  - NAV at delivery date (2025-12-31): £102,419,859.44
  - Days to delivery: 92 days
  - GBP IRR: 9.951%
  - Notional: £102,419,859.44 / (1.09951)^(92/365) ≈ £100,000,000.00 GBP

2025-12-31: Roll Forward
  - Settle Forward 1 (deliver £100,000,000.00 GBP)
  - Enter Forward 2
  - Trade Date: 2025-12-31
  - Delivery Date: 2026-03-31
  - NAV at delivery date (2026-03-31): £102,284,599.01
  - Days to delivery: 90 days
  - Notional: £102,284,599.01 / (1.09951)^(90/365) ≈ £99,919,859.44 GBP

...continues quarterly until final cashflow...
```

#### Why NAV-Based (Not Cashflow-Based)?

**NAV-based hedging** protects the total economic exposure (present value of all future cashflows), not just individual cashflows. This provides
**Fair value hedge**, protecting balance-sheet value, not just cashflow timing.

## Testing

Run the full test suite:

```bash
python3 -m pytest tests
```

Run tests with verbose output:

```bash
python3 -m pytest tests -v
```

Run tests for a specific module:

```bash
python3 -m pytest tests/metric_calculations/test_nav.py
python3 -m pytest tests/hedging_strategies/test_fx_forwards.py
```
