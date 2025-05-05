import sys
import os
from datetime import date
from dateutil.relativedelta import relativedelta
import math

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional # Needed for Optional fields in Pydantic v1

# Add the parent directory to the system path (if needed based on your setup)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # WARNING: Change this to your frontend URL in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models for Request, Response, and Error ---

class DebtParameters(BaseModel):
    total_debt: float = Field(..., gt=0, description="Total outstanding debt amount")
    monthly_payment: float = Field(..., gt=0, description="Total amount paid towards debt each month")
    annual_interest_rate: float = Field(..., ge=0, description="Annual interest rate (APR)")

class FreedomDateResult(BaseModel):
    freedom_date: date
    total_months: int
    total_interest_paid: float
    initial_debt: float
    monthly_payment: float
    annual_interest_rate: float

# UPDATED: Pydantic model for custom error response details
class ErrorDetail(BaseModel):
    """Structured detail for custom 400 errors."""
    code: str # e.g., "INSUFFICIENT_PAYMENT", "CALCULATION_TOO_LONG"
    message: str # User-friendly message
    suggestion_value: Optional[float] = None # NEW: Optional value for suggestion (e.g., monthly interest)
    suggestion_unit: Optional[str] = None # NEW: Optional unit for suggestion (e.g., "$", "months")


# --- Calculation Logic (Updated Again) ---

def simulate_payoff_date(initial_balance: float, monthly_payment: float, annual_interest_rate: float):
    """
    Simulates debt payoff month-by-month. Returns freedom date, months, interest.
    Raises HTTPException with structured detail on specific calculation errors.
    """
    if initial_balance <= 0:
        # Already debt free!
        return date.today(), 0, 0.0

    # monthly_payment > 0 check handled by Pydantic gt=0

    monthly_interest_rate = annual_interest_rate / 100 / 12

    # Check if payment is sufficient to cover even the first month's interest
    monthly_interest_first_month = initial_balance * monthly_interest_rate # Calculate this value
    if annual_interest_rate > 0 and monthly_payment <= monthly_interest_first_month:
        # Use the new structured error detail, including suggestion
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorDetail(
                code="INSUFFICIENT_PAYMENT",
                message="Your monthly payment is not enough to cover the monthly interest accrual.",
                suggestion_value=monthly_interest_first_month, # Pass the calculated interest
                suggestion_unit="$" # Indicate the unit
            ).dict() # .dict() serializes the Pydantic model to a dictionary
        )

    # --- Simulation ---
    current_balance = initial_balance
    total_interest_paid = 0.0
    months = 0
    MAX_MONTHS = 1200 # Safety break: 100 years

    while current_balance > 0 and months < MAX_MONTHS:
        months += 1
        interest_this_month = current_balance * monthly_interest_rate
        current_balance += interest_this_month
        total_interest_paid += interest_this_month

        payment_amount = min(monthly_payment, current_balance)
        current_balance -= payment_amount

    # Check if loop ended due to hitting MAX_MONTHS
    if months >= MAX_MONTHS and current_balance > 0:
        # Use the new structured error detail - no specific suggestion value needed here initially
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorDetail(
                code="CALCULATION_TOO_LONG",
                message=f"Calculation exceeded {MAX_MONTHS} months (100 years). Your payment amount is too low to pay off this debt within a reasonable timeframe."
            ).dict()
        )

    # Calculate the freedom date
    freedom_date = date.today() + relativedelta(months=+months)

    return freedom_date, months, total_interest_paid

# --- API Endpoint (No major change needed here, it raises the HTTPException) ---

@app.post(
    "/api/calculate-freedom-date",
    response_model=FreedomDateResult,
    # Document the 400 response structure
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorDetail, # Use our new error model
            "description": "Specific calculation error (e.g., insufficient payment, calculation too long)",
        }
    }
)
async def calculate_freedom_date_api(params: DebtParameters):
    """
    Calculates the estimated debt freedom date based on input parameters.
    Returns calculation results or a structured error on specific conditions.
    """
    try:
        freedom_date, total_months, total_interest_paid = simulate_payoff_date(
            params.total_debt,
            params.monthly_payment,
            params.annual_interest_rate
        )

        return FreedomDateResult(
            freedom_date=freedom_date,
            total_months=total_months,
            total_interest_paid=total_interest_paid,
            initial_debt=params.total_debt,
            monthly_payment=params.monthly_payment,
            annual_interest_rate=params.annual_interest_rate
        )
    except HTTPException as e:
        # Re-raise HTTPExceptions raised by simulate_payoff_date
        raise e
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred: {e}") # Log server-side
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred during calculation." # Generic message for unexpected errors
        )

# Optional: Root endpoint
@app.get("/")
async def read_root():
    return {"message": "Debt-Free Countdown Generator Backend is running."}