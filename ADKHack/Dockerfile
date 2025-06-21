# Disaster Response System - Docker Container
# Optimized for Google Cloud Run and Agent Engine deployment

FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8080

# Create app directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY python_agents/requirements.txt ./python_agents/
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r python_agents/requirements.txt && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p python_agents/simulated_data && \
    mkdir -p logs

# Set Python path to include python_agents directory
ENV PYTHONPATH=/app:/app/python_agents

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port
EXPOSE 8080

# Default command - launch ADK FastAPI server
CMD ["python", "-m", "google_adk.run", "--port", "8080"] 