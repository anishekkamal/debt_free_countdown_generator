# Debt-Free Countdown Generator

This project provides a simple web application to estimate the date you can become debt-free based on your total debt, monthly payment, and average interest rate. It features a FastAPI backend for calculation and a static JavaScript frontend for the user interface and display.

The frontend includes a visual "Freedom Date Card" designed to be easily shareable (e.g., via screenshot).


## Setup

1.  **Clone or Download:** Get the project files onto your computer.
2.  **Install Python:** Ensure you have Python 3.7+ installed.
3.  **Set up Backend:**
    *   Navigate to the `backend/` directory in your terminal.
    *   Create a virtual environment (recommended):
        ```bash
        python -m venv venv
        ```
    *   Activate the virtual environment:
        *   On macOS/Linux:
            ```bash
            source venv/bin/activate
            ```
        *   On Windows:
            ```bash
            venv\Scripts\activate
            ```
    *   Install dependencies:
        ```bash
        pip install -r requirements.txt
        ```
4.  **Set up Frontend:** The frontend is static. You just need to open `frontend/index.html` in a web browser. No separate server is required for the frontend files themselves.

## How to Run

1.  **Start the Backend Server:**
    *   Open your terminal and navigate to the `backend/` directory.
    *   Activate your virtual environment (if not already active).
    *   Run the FastAPI app using uvicorn:
        ```bash
        uvicorn main:app --reload
        ```
    *   You should see output indicating uvicorn is running, likely on `http://127.0.0.1:8000`. The `--reload` flag is useful during development.
2.  **Open the Frontend:**
    *   Navigate to the `frontend/` directory in your file explorer.
    *   Double-click on `index.html` to open it in your preferred web browser.
3.  **Use the Generator:**
    *   Enter your total outstanding debt, the fixed amount you plan to pay each month (this should be *more* than the minimums required if you have multiple debts, as this calculator simplifies to a single payment/APR), and an estimated average annual interest rate (APR).
    *   Click "Generate Countdown".
    *   The "Freedom Date Card" section will appear, displaying your estimated debt-free date, time until freedom, total months, and estimated total interest paid.

## Shareable Visual

The "Freedom Date Card" is styled to be a distinct visual block. To "share" it, you can:

*   Use your browser's built-in screenshot functionality.
*   Use your operating system's screenshot tools.
*   (More advanced) Implement client-side libraries like `html2canvas` or `dom-to-image` to generate an image file (not included in this basic version).

## Important Notes & Limitations

*   **Simplified Model:** This calculator uses a simplified model assuming a single total debt amount, a single fixed monthly payment (which must cover interest), and a single average APR.
*   **No Minimum Payments:** It does not factor in varying minimum payments across multiple debts. The 'Total Monthly Payment' is assumed to be the *total* amount you are paying, ideally including extra payments beyond minimums.
*   **Estimates Only:** The calculations are estimates. Actual payoff time and interest paid can vary due to fees, changes in interest rates (variable APRs), changes in payment amounts, or specific loan terms (like how minimum payments are calculated).
*   **Consult a Professional:** This tool is for informational purposes only. Always consult with a financial advisor for personalized debt management advice.

## Customization

*   **Styling:** Modify `frontend/static/css/style.css`.
*   **Frontend Logic:** Enhance `frontend/static/js/script.js` (e.g., improve validation, add date pickers, implement actual image generation for sharing).
*   **Backend Logic:** The core calculation is in `backend/main.py`. You could extend this (though it would make the frontend input more complex) to handle multiple debts similar to the first calculator, but that would change the "single freedom date" concept.
*   **Debtzero Branding:** Remember to replace the placeholder link in the `card-footer` of `index.html` with your actual Debtzero.club website URL.

## Troubleshooting

*   **Backend not running:** Check the terminal output for errors when running `uvicorn main:app --reload`. Ensure FastAPI, uvicorn, pydantic, and python-dateutil are installed (`pip install -r requirements.txt`).
*   **Frontend not displaying results:** Open your browser's developer console (usually F12). Check the "Console" and "Network" tabs for errors. Look for failed requests to `http://127.0.0.1:8000/api/calculate-freedom-date`. Ensure the backend server is running and accessible on port 8000 and that there are no CORS errors (the backend is configured to allow all origins for dev).
*   **Calculation Errors:** If the backend returns an error message, double-check your input values. Ensure your monthly payment is sufficient to cover the interest on the total debt amount.