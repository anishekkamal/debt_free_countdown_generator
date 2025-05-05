# Use a lightweight Python image as the base for the backend
FROM python:3.10-slim-buster as builder

# Set the working directory in the container
WORKDIR /app

# Copy the backend requirements file into the working directory
# This is done before copying the rest of the code to leverage Docker cache
COPY backend/requirements.txt ./backend/requirements.txt

# Install the backend dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# --- Build the final image ---
FROM python:3.10-slim-buster

# Set the working directory
WORKDIR /app

# Copy the installed packages from the builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin/uvicorn /usr/local/bin/uvicorn

# Copy the application code (backend and frontend) into the working directory
# The .dockerignore file at the root will prevent unnecessary files from being copied
COPY . .

# Expose the port the application will listen on
EXPOSE 8080

# Define the command to run the application using uvicorn
# Uvicorn will serve the FastAPI app which is configured to serve the static frontend files
# Define the command to run the application using uvicorn
# Use the shell form of CMD to allow shell variable expansion (${PORT:-8080})
CMD uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8080}