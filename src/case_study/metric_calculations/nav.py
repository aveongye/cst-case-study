"""
NAV related calculations for the CST case study analytics.
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd

DAYS_IN_YEAR = 365.0


def calculate_cashflow_local(rows_on_date: pd.DataFrame) -> float:
    """
    Calculate the net cashflow amount for the current date.
    """
    return float(rows_on_date["Cashflow_Amount_Local"].sum())


def calculate_loan_receivable_local(
    current_principal: float, rows_on_date: pd.DataFrame
) -> float:
    """
    Calculate the outstanding principal (loan receivable).
    
    Args:
        current_principal: Outstanding principal balance before processing current date
        rows_on_date: Cashflow rows occurring on the current date
        
    Returns:
        Updated outstanding principal balance (never negative)
    """
    for _, row in rows_on_date.iterrows():
        amount = float(row["Cashflow_Amount_Local"])
        cashflow_type = row["Cashflow_Type"]

        if cashflow_type == "Investment" and amount < 0:
            current_principal += abs(amount)
        elif cashflow_type == "Principal Repayment" and amount > 0:
            current_principal = max(current_principal - amount, 0.0)

    return current_principal


def calculate_cash_on_hand_local(
    current_cash: float, rows_on_date: pd.DataFrame
) -> float:
    """
    Calculate cumulative cash on hand by adding any positive cashflows
    received on the current date.
    
    Args:
        current_cash: Cumulative cash balance before processing current date
        rows_on_date: Cashflow rows occurring on the current date
        
    Returns:
        Updated cumulative cash balance
    """
    positive_cash = rows_on_date.loc[
        rows_on_date["Cashflow_Amount_Local"] > 0, "Cashflow_Amount_Local"
    ].sum()
    return current_cash + float(positive_cash)


def calculate_accrued_interest_local(
    remaining_interest: float, rows_on_date: pd.DataFrame
) -> float:
    """
    Calculate remaining accrued interest by subtracting any interest payments
    received on the current date.
    
    Args:
        remaining_interest: Remaining interest balance before processing current date
        rows_on_date: Cashflow rows occurring on the current date
        
    Returns:
        Updated remaining interest balance (never negative)
    """
    interest_received = rows_on_date.loc[
        rows_on_date["Cashflow_Type"] == "Interest", "Cashflow_Amount_Local"
    ].sum()
    if interest_received > 0:
        remaining_interest = max(remaining_interest - float(interest_received), 0.0)
    return remaining_interest


def calculate_net_asset_value_local(
    loan_receivable: float,
    cash_on_hand: float,
    accrued_interest: float,
) -> float:
    """
    Calculate the total undiscounted contractual value as the sum of its components.
    
    Net Asset Value = Loan Receivable + Cash On Hand + Accrued Interest
    
    This represents the total contractual value of all cashflows (principal + interest)
    over the entire life of the loan. The sum of the three components remains constant
    across all dates, but their individual values change as cashflows are received.
    
    Args:
        loan_receivable: Outstanding principal balance
        cash_on_hand: Cumulative cash received
        accrued_interest: Remaining interest to be received
        
    Returns:
        Total undiscounted contractual value (constant across all dates)
    """
    return loan_receivable + cash_on_hand + accrued_interest

def calculate_future_cashflows_present_value_local(
    curr_df: pd.DataFrame,
    target_date: datetime,
    irr: float,
) -> float:
    """
    Calculate the present value of all future cashflows using the currency IRR.
    
    Formula: PV = Σ (CF_t / (1 + r)^((t - t0) / 365))
    where:
    - PV is the present value
    - CF_t is the cashflow at time t
    - r is the currency IRR
    - t0 is the target date
    - t is the cashflow date
    
    Args:
        curr_df: Complete cashflow schedule for the currency
        target_date: Valuation date
        irr: Currency-specific internal rate of return
        
    Returns:
        Present value of all cashflows after the target date
    """
    future_cashflows = curr_df[
        (curr_df["Date"] > target_date) & (curr_df["Cashflow_Amount_Local"] > 0)
    ]
    
    if future_cashflows.empty:
        return 0.0

    present_value = 0.0
    for _, row in future_cashflows.iterrows():
        days_diff = (row["Date"] - target_date).days
        discount_factor = (1 + irr) ** (days_diff / DAYS_IN_YEAR)
        present_value += row["Cashflow_Amount_Local"] / discount_factor
    
    return present_value


def calculate_net_asset_present_value_local(
    future_cashflows_pv: float,
    cash_on_hand: float,
) -> float:
    """
    Calculate the total net asset present value as the sum of future cashflows PV and cash on hand.
    
    Net Asset Present Value = Future Cashflows Present Value + Cash On Hand
    
    This represents the total present value of the asset, including both the discounted
    value of future cashflows and the interest payment that has already been received.
    
    Args:
        future_cashflows_pv: Present value of all future cashflows
        cash_on_hand: Cumulative cash received (no discounting needed as it's already received)
        
    Returns:
        Total net asset present value
    """
    return future_cashflows_pv + cash_on_hand


def generate_nav_schedule(
    fund_df: pd.DataFrame,
    currency_irrs: dict[str, float],
) -> dict[str, pd.DataFrame]:
    """
    Build NAV schedules grouped by currency.
    
    Each schedule contains the following columns:
    - Date: Reporting date
    - Cashflow_Local: Net cashflow on the reporting date
    - Loan_Receivable_Local: Outstanding principal balance
    - Cash_On_Hand_Local: Cumulative cash received
    - Accrued_Interest_Local: Remaining interest to be received
    - Net_Asset_Value_Local: Total undiscounted contractual value
    - Future_Cashflows_Present_Value_Local: Present value of future cashflows
    - Net_Asset_Present_Value_Local: Total present value (future cashflows PV + cash on hand)
    
    Args:
        fund_df: Cashflow data for the fund
        currency_irrs: Dictionary mapping currency codes to their IRRs
        
    Returns:
        Dictionary mapping currency codes to their NAV schedule DataFrames
    """
    schedules: dict[str, pd.DataFrame] = {}
    
    for currency, curr_df in fund_df.groupby("Local_Currency"):
        sorted_df = curr_df.sort_values("Date").reset_index(drop=True)
        irr = currency_irrs[currency]

        # Initialize running balances
        total_interest = float(
            sorted_df.loc[
                sorted_df["Cashflow_Type"] == "Interest", "Cashflow_Amount_Local"
            ].sum()
        )
        
        schedule_rows = []
        cash_on_hand = 0.0
        interest_remaining = total_interest
        principal_outstanding = 0.0
        
        for current_date, rows_on_date in sorted_df.groupby("Date"):
            cashflow_local = calculate_cashflow_local(rows_on_date)
            principal_outstanding = calculate_loan_receivable_local(
                principal_outstanding, rows_on_date
            )
            cash_on_hand = calculate_cash_on_hand_local(cash_on_hand, rows_on_date)
            interest_remaining = calculate_accrued_interest_local(
                interest_remaining, rows_on_date
            )
            nav_value = calculate_net_asset_value_local(
                principal_outstanding, cash_on_hand, interest_remaining
            )
            future_cashflows_present_value = calculate_future_cashflows_present_value_local(
                sorted_df, current_date, irr
            )
            net_asset_present_value = calculate_net_asset_present_value_local(
                future_cashflows_present_value, cash_on_hand
            )

            schedule_rows.append(
                {
                    "Date": current_date,
                    "Cashflow_Local": cashflow_local,
                    "Loan_Receivable_Local": principal_outstanding,
                    "Cash_On_Hand_Local": cash_on_hand,
                    "Accrued_Interest_Local": interest_remaining,
                    "Net_Asset_Value_Local": nav_value,
                    "Future_Cashflows_Present_Value_Local": future_cashflows_present_value,
                    "Net_Asset_Present_Value_Local": net_asset_present_value,
                }
            )

        schedules[currency] = pd.DataFrame(schedule_rows)
    
    return schedules
