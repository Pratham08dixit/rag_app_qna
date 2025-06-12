# syntax=docker/dockerfile:1

# Build stage
FROM python:3.9-slim AS builder

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.9-slim

WORKDIR /app

# Copy Python environment including binaries (e.g., uvicorn)
COPY --from=builder /usr/local /usr/local

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads faiss_indices

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
