document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('countdown-form');
    const resultsContainer = document.getElementById('results-container');
    const freedomDateCard = document.getElementById('freedom-date-card'); // NEW: Reference to the card element
    const downloadCardBtn = document.getElementById('download-card-btn'); // NEW: Reference to the download button


    // References for the Shareable Card (remain the same)
    const freedomDateValueSpan = document.getElementById('freedom-date-value');
    const countdownValueSpan = document.getElementById('countdown-value');
    const totalMonthsSpan = document.getElementById('total-months');
    const totalInterestSpan = document.getElementById('total-interest');

    // References for the Modal (remain the same)
    const errorModal = document.getElementById('error-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalMessage = document.getElementById('modal-message');
    const modalCloseButton = document.getElementById('modal-close-button');


    // Function to format currency (remains the same)
    const formatCurrency = (value) => {
        return `$${parseFloat(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    };

     // Function to format a suggestion value with unit (remains the same)
    const formatSuggestion = (value, unit) => {
        if (unit === "$") {
            return `$${parseFloat(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        }
        return `${value} ${unit || ''}`;
    };


    // Function to calculate months/years difference (remains the same)
     const calculateMonthYearDifference = (futureDate) => {
        const today = new Date();
        const future = new Date(futureDate);

        if (future < today) {
             return "Already passed!";
        }

        let years = future.getFullYear() - today.getFullYear();
        let months = future.getMonth() - today.getMonth();

        if (future.getDate() < today.getDate()) {
             months--;
        }

        if (months < 0) {
            years--;
            months += 12;
        }

        const parts = [];
        if (years > 0) {
            parts.push(`${years} year${years > 1 ? 's' : ''}`);
        }
        if (months > 0) {
             parts.push(`${months} month${months > 1 ? 's' : ''}`);
        }

        if (parts.length === 0) {
             return "Less than a month!";
        }

        return parts.join(' and ');
    };


    // Function to show the modal (remains the same)
    const showModal = (title, message) => {
        modalTitle.textContent = title;
        modalMessage.textContent = message;
        errorModal.classList.remove('hidden');
    };

    // Function to hide the modal (remains the same)
    const hideModal = () => {
        errorModal.classList.add('hidden');
    };

    // Add event listener to close the modal (remains the same)
    modalCloseButton.addEventListener('click', hideModal);

    // Optional: Close modal if clicking outside content (remains the same)
    errorModal.addEventListener('click', (event) => {
        if (event.target === errorModal) {
            hideModal();
        }
    });

    // NEW: Function to handle the download button click
    const handleDownloadCard = () => {
        // Use html2canvas to capture the freedom-date-card element
        html2canvas(freedomDateCard, {
            // Optional: Configure html2canvas options if needed
            // For example, you might need scale for higher resolution
             scale: 2, // Increase scale for sharper image
             logging: false, // Reduce console noise from html2canvas
        }).then(function(canvas) {
            // Convert the canvas to a data URL (PNG format by default)
            const image = canvas.toDataURL("image/png");

            // Create a temporary link element
            const link = document.createElement('a');
            link.download = 'debt-free-countdown.png'; // Suggested filename
            link.href = image; // Set the href to the image data URL

            // Append link to body, trigger click, and remove link
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }).catch(err => {
            console.error("Error capturing card with html2canvas:", err);
            // Show an error modal if capturing fails
             showModal('Image Capture Error', 'Could not generate the image for download. Please try again.');
        });
    };

    // NEW: Add event listener to the download button
    downloadCardBtn.addEventListener('click', handleDownloadCard);


    // Function to display error messages (remains the same, uses showModal)
    const displayError = (errorData) => {
        let errorMessage = 'An unexpected error occurred. Please try again.';
        let errorTitle = 'Calculation Error';

        console.error("Received error data:", errorData);

        if (typeof errorData === 'string') {
            errorMessage = errorData;
        } else if (errorData && typeof errorData === 'object' && errorData.detail && typeof errorData.detail === 'object') {
             if (errorData.detail.code && errorData.detail.message) {
                  errorTitle = 'Calculation Error';
                  errorMessage = errorData.detail.message;

                  if (errorData.detail.suggestion_value !== undefined && errorData.detail.suggestion_unit) {
                       const formattedSuggestion = formatSuggestion(errorData.detail.suggestion_value, errorData.detail.suggestion_unit);
                       if (errorData.detail.code === "INSUFFICIENT_PAYMENT") {
                           errorMessage = `Your monthly payment is not enough to cover the monthly interest accrual (${formattedSuggestion}). Please increase your payment amount to more than ${formattedSuggestion}.`;
                       } else {
                            errorMessage += ` Suggestion: ${formattedSuggestion}`;
                       }
                  } else if (errorData.detail.code === "CALCULATION_TOO_LONG") {
                       errorMessage = `Your monthly payment is too low to pay off this debt within a reasonable timeframe (100+ years simulation). Please significantly increase your monthly payment amount or explore options for reducing your interest rate or principal.`;
                   }


             } else if (Array.isArray(errorData.detail)) {
                  errorTitle = 'Input Validation Error';
                  errorMessage = 'There was an issue with your input values:';
                   errorData.detail.forEach(err => {
                      const field = err.loc[err.loc.length - 1];
                      errorMessage += `\n- Field '${field}': ${err.msg}`;
                  });
                  console.error("FastAPI Validation Errors:", errorData.detail);

             } else if (typeof errorData.detail === 'string') {
                   errorTitle = 'Server Error';
                   errorMessage = `A server error occurred: ${errorData.detail}`;
             } else {
                  errorTitle = 'Unexpected Error';
                  errorMessage = 'Received an unexpected error detail format from the server.';
             }
        } else {
             errorTitle = 'Unexpected Response';
             errorMessage = 'Received an unexpected server response format.';
        }

        resultsContainer.classList.add('hidden'); // Hide results section
        downloadCardBtn.classList.add('hidden'); // Hide download button on error
        showModal(errorTitle, errorMessage);
    };

    // Handle form submission (remains the same, calls hideModal)
    form.addEventListener('submit', async (event) => {
        event.preventDefault();

        resultsContainer.classList.add('hidden');
        downloadCardBtn.classList.add('hidden'); // Hide download button before calculation
        hideModal();

        const totalDebtInput = document.getElementById('total-debt');
        const monthlyPaymentInput = document.getElementById('monthly-payment');
        const annualAprInput = document.getElementById('avg-apr');

        const totalDebt = parseFloat(totalDebtInput.value);
        const monthlyPayment = parseFloat(monthlyPaymentInput.value);
        const annualApr = parseFloat(annualAprInput.value);

        if (isNaN(totalDebt) || totalDebt <= 0) {
             showModal('Input Error', 'Please enter a valid positive number for total debt.');
             totalDebtInput.focus();
             return;
         }
          if (isNaN(monthlyPayment) || monthlyPayment <= 0) {
             showModal('Input Error', 'Please enter a valid positive number for monthly payment.');
             monthlyPaymentInput.focus();
             return;
         }
          if (isNaN(annualApr) || annualApr < 0) {
             showModal('Input Error', 'Please enter a valid non-negative number for average APR.');
             annualAprInput.focus();
             return;
         }

        const data = {
            total_debt: totalDebt,
            monthly_payment: monthlyPayment,
            annual_interest_rate: annualApr
        };

        try {
            const response = await fetch('http://127.0.0.1:8000/api/calculate-freedom-date', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const resultData = await response.json();

            if (!response.ok) {
                console.error("Backend Error Response:", response.status, resultData);
                displayError(resultData); // Use the updated displayError
                return;
            }

            displayResults(resultData);

        } catch (error) {
            console.error('Fetch or JSON parse error:', error);
            showModal('Connection Error', 'Could not connect to the calculation service. Please ensure the backend is running and accessible.');
        }
    });

    // Function to display the results received from the backend (MODIFIED to show download button)
    const displayResults = (results) => {
        hideModal();

        const freedomDate = new Date(results.freedom_date);
        const formattedFreedomDate = isNaN(freedomDate.getTime()) ?
            'Invalid Date' :
            freedomDate.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });

        let timeUntilFreedom = "";
        if (results.total_months === 0 && results.initial_debt > 0) {
            timeUntilFreedom = "Debt Free Now!";
        } else if (results.total_months === 0 && results.initial_debt <= 0) {
             timeUntilFreedom = "Already Debt Free!";
        }
        else {
             timeUntilFreedom = calculateMonthYearDifference(freedomDate);
        }

        freedomDateValueSpan.textContent = formattedFreedomDate;
        countdownValueSpan.textContent = timeUntilFreedom;
        totalMonthsSpan.textContent = results.total_months;
        totalInterestSpan.textContent = formatCurrency(results.total_interest_paid);

        resultsContainer.classList.remove('hidden'); // Show results section
        downloadCardBtn.classList.remove('hidden'); // NEW: Show download button


        // Scroll to results
        resultsContainer.scrollIntoView({ behavior: 'smooth' });
    };

}); // End DOMContentLoaded