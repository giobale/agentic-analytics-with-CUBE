# ABOUTME: Dockerfile for analyst agent containing both API server and Streamlit frontend
# ABOUTME: Runs both FastAPI server and Streamlit app to provide complete analyst functionality

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY analyst-service/requirements.txt /app/analyst-service/requirements.txt
COPY frontend/requirements.txt /app/frontend/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/analyst-service/requirements.txt
RUN pip install --no-cache-dir -r /app/frontend/requirements.txt

# Copy the entire analyst-agent directory
COPY . /app/

# Create necessary directories
RUN mkdir -p /app/analyst-service/datasets \
    /app/analyst-service/results \
    /app/analyst-service/history \
    /app/frontend/logs \
    /app/init-data/datasets \
    /app/init-data/history

# After copying files, create backup copies for volume initialization
RUN if [ -d "/app/analyst-service/datasets" ]; then \
        cp -r /app/analyst-service/datasets/* /app/init-data/datasets/ 2>/dev/null || true; \
    fi && \
    if [ -d "/app/analyst-service/history" ]; then \
        cp -r /app/analyst-service/history/* /app/init-data/history/ 2>/dev/null || true; \
    fi

# Set environment variables
ENV PYTHONPATH=/app/analyst-service/src:/app/analyst-service
ENV STREAMLIT_PORT=8501
ENV ANALYST_API_PORT=8502

# Expose ports
EXPOSE 8501 8502

# Create startup script
COPY start_services.sh /app/start_services.sh
RUN chmod +x /app/start_services.sh

# Set the startup command
CMD ["/app/start_services.sh"]