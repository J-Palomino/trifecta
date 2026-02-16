# DaisyChain Proxy API - Standalone Deployment
# This service connects remotely to MeshCentral and provides REST API access
# Deploy this independently from MeshCentral infrastructure

FROM python:3.11-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Create non-root user for security
RUN useradd -m -u 1000 proxyuser && \
    chown -R proxyuser:proxyuser /app

USER proxyuser

# Expose port (Railway will assign PORT dynamically)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run the application
# The app.py __main__ block handles PORT environment variable
CMD ["python", "app.py"]
