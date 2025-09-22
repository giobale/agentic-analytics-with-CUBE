# ABOUTME: Docker container for the orchestrator service with system prompt caching
# ABOUTME: Includes startup scripts for system prompt generation and health checks

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV APP_HOME=/app

# Create app directory and cache directory
WORKDIR $APP_HOME
RUN mkdir -p /app/cache /app/scripts /app/logs

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy orchestrator source code
COPY . .

# Copy startup and utility scripts
COPY scripts/ ./scripts/
RUN chmod +x ./scripts/*.sh

# Create a non-root user for security
RUN useradd -m -u 1000 orchestrator && \
    chown -R orchestrator:orchestrator /app
USER orchestrator

# Health check endpoint
EXPOSE 8080

# Set entrypoint to startup script
ENTRYPOINT ["./scripts/startup.sh"]