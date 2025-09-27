#!/bin/bash

# ABOUTME: Startup script for analyst agent container
# ABOUTME: Runs both FastAPI server and Streamlit app concurrently

set -e

echo "🚀 Starting Analyst Agent Services..."

# Change to the app directory
cd /app

# Initialize volumes with existing data if they're empty
echo "📁 Initializing volumes with existing data..."

# Initialize datasets volume
if [ -d "/app/init-data/datasets" ] && [ ! -z "$(ls -A /app/init-data/datasets 2>/dev/null)" ]; then
    # Check if mounted volume is empty
    if [ -z "$(ls -A /app/analyst-service/datasets 2>/dev/null)" ]; then
        echo "   📊 Copying initial datasets to volume..."
        cp -r /app/init-data/datasets/* /app/analyst-service/datasets/ 2>/dev/null || true
    else
        echo "   📊 Datasets volume already has data, skipping initialization"
    fi
else
    echo "   📊 No initial datasets to copy"
fi

# Initialize history volume
if [ -d "/app/init-data/history" ] && [ ! -z "$(ls -A /app/init-data/history 2>/dev/null)" ]; then
    # Check if mounted volume is empty
    if [ -z "$(ls -A /app/analyst-service/history 2>/dev/null)" ]; then
        echo "   📋 Copying initial history to volume..."
        cp -r /app/init-data/history/* /app/analyst-service/history/ 2>/dev/null || true
    else
        echo "   📋 History volume already has data, skipping initialization"
    fi
else
    echo "   📋 No initial history to copy"
fi

echo "✅ Volume initialization completed!"

# Verify files are accessible
echo "🔍 Verifying volume contents..."
echo "   📊 Datasets directory contents:"
ls -la /app/analyst-service/datasets/ 2>/dev/null || echo "   ❌ Datasets directory not accessible"
echo "   📋 History directory contents:"
ls -la /app/analyst-service/history/ 2>/dev/null || echo "   ❌ History directory not accessible"

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