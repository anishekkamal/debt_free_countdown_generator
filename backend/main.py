import sys
import os
from datetime import date
from dateutil.relativedelta import relativedelta
import math

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles # NEW: Import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional

# Add the parent directory to the system path (if needed based on your setup)
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# NOTE: When running inside Docker with WORKDIR /app and code copied to /app,
# the structure is flat relative to the app root. No sys.path changes needed if
# referencing modules relative to the app root (like backend.main).

app = FastAPI()

# NOTE: CORS is typically not needed for requests from the *same* origin.
# When the frontend is served by the FastAPI app itself (single origin),
# browser CORS restrictions don't apply to API calls from that frontend.
# Keep it for local testing flexibility or if you ever split frontend/backend later.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # WARNING: Change this to your frontend URL in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models (remain the same) ---

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

class ErrorDetail(BaseModel):
    """Structured detail for custom 400 errors."""
    code: str
    message: str
    suggestion_value: Optional[float] = None
    suggestion_unit: Optional[str] = None


# --- Calculation Logic (remains the same) ---

def simulate_payoff_date(initial_balance: float, monthly_payment: float, annual_interest_rate: float):
    # ... (function code remains the same) ...
    if initial_balance <= 0:
        return date.today(), 0, 0.0

    monthly_interest_rate = annual_interest_rate / 100 / 12

    monthly_interest_first_month = initial_balance * monthly_interest_rate
    if annual_interest_rate > 0 and monthly_payment <= monthly_interest_first_month:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorDetail(
                code="INSUFFICIENT_PAYMENT",
                message="Your monthly payment is not enough to cover the monthly interest accrual.",
                suggestion_value=monthly_interest_first_month,
                suggestion_unit="$"
            ).dict()
        )

    current_balance = initial_balance
    total_interest_paid = 0.0
    months = 0
    MAX_MONTHS = 1200

    while current_balance > 0 and months < MAX_MONTHS:
        months += 1
        interest_this_month = current_balance * monthly_interest_rate
        current_balance += interest_this_month
        total_interest_paid += interest_this_month

        payment_amount = min(monthly_payment, current_balance)
        current_balance -= payment_amount

    if months >= MAX_MONTHS and current_balance > 0:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorDetail(
                code="CALCULATION_TOO_LONG",
                message=f"Calculation exceeded {MAX_MONTHS} months (100 years). Your payment amount is too low to pay off this debt within a reasonable timeframe."
            ).dict()
        )

    freedom_date = date.today() + relativedelta(months=+months)

    return freedom_date, months, total_interest_paid

# --- API Endpoint (remains the same) ---

@app.post(
    "/api/calculate-freedom-date",
    response_model=FreedomDateResult,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorDetail,
            "description": "Specific calculation error (e.g., insufficient payment, calculation too long)",
        }
    }
)
async def calculate_freedom_date_api(params: DebtParameters):
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
        raise e
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred during calculation."
        )

# NEW: Mount StaticFiles to serve the frontend directory
# This MUST be placed AFTER your API routes so that API calls are matched first
app.mount(
    "/", # Mount at the root path
    StaticFiles(directory="frontend", html=True), # Serve files from the 'frontend' directory, serve index.html for root
    name="frontend_static" # Optional name
)

# The old root endpoint "/" will now be overridden by the StaticFiles mount.
# If you still wanted an API health check at the root, you'd need to place it
# BEFORE the StaticFiles mount. But mounting at "/" is standard for serving SPAs.