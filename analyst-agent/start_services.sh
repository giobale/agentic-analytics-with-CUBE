#!/bin/bash

# ABOUTME: Startup script for analyst agent container
# ABOUTME: Runs both FastAPI server and Streamlit app concurrently

set -e

echo "🚀 Starting Analyst Agent Services..."

# Change to the app directory
cd /app

# Start FastAPI server in background
echo "📡 Starting FastAPI API Server on port 8502..."
cd /app/frontend
python api_server.py &
API_PID=$!

# Wait a moment for API server to start
sleep 5

# Start Streamlit app
echo "🎨 Starting Streamlit Frontend on port 8501..."
cd /app/frontend
streamlit run streamlit_analyst_app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false &
STREAMLIT_PID=$!

# Function to handle shutdown
cleanup() {
    echo "🛑 Shutting down services..."
    kill $API_PID 2>/dev/null || true
    kill $STREAMLIT_PID 2>/dev/null || true
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

echo "✅ Both services started successfully!"
echo "   📡 API Server: http://localhost:8502"
echo "   🎨 Streamlit App: http://localhost:8501"

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?