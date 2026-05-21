# Use official Python base image
FROM python:3.11-slim

# Image metadata
LABEL maintainer="Luis Medina"
LABEL description="Flight Delay Prediction API for LAX departures"
LABEL version="2.0"

# Set the working directory inside the container
WORKDIR /app

# Copy requirements file first (optimizes Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all necessary project files into the container
COPY airport_encodings.json .
COPY finalized_model.pkl .
COPY API_Python_v1.py .
COPY API_Python_v2.py .

# Create a non-root user for security
RUN useradd -m apiuser
USER apiuser

# Expose port 8000 for the web server
EXPOSE 8000

# Health check to verify the API is responding
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')" || exit 1

# Start the Uvicorn web server running the API
CMD ["uvicorn", "API_Python_v2:app", "--host", "0.0.0.0", "--port", "8000"]