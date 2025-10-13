#!/bin/bash

# ABOUTME: Verification script to check analyst-agent data persistence
# ABOUTME: Run this after starting docker-compose to verify files are properly mounted

echo "🔍 Verifying Analyst Agent Data Persistence"
echo "==========================================="

# Function to check if container is running
check_container() {
    if docker ps --format "table {{.Names}}" | grep -q "ai-data-analyst"; then
        echo "✅ Analyst Agent container is running"
        return 0
    else
        echo "❌ Analyst Agent container is not running"
        echo "   Run: docker-compose up -d analyst-agent"
        return 1
    fi
}

# Function to check files in container
check_container_files() {
    echo ""
    echo "📊 Checking datasets in container:"
    docker exec ai-data-analyst ls -la /app/analyst-service/datasets/ 2>/dev/null || echo "❌ Could not access datasets directory"

    echo ""
    echo "📋 Checking history in container:"
    docker exec ai-data-analyst ls -la /app/analyst-service/history/ 2>/dev/null || echo "❌ Could not access history directory"

    echo ""
    echo "🔍 Checking specific files:"
    if docker exec ai-data-analyst test -f /app/analyst-service/datasets/123456789.csv; then
        echo "✅ 123456789.csv found in container"
    else
        echo "❌ 123456789.csv NOT found in container"
    fi

    if docker exec ai-data-analyst test -f /app/analyst-service/history/analysis_history.json; then
        echo "✅ analysis_history.json found in container"
    else
        echo "❌ analysis_history.json NOT found in container"
    fi
}

# Function to check volumes
check_volumes() {
    echo ""
    echo "💾 Checking Docker volumes:"
    echo "   📊 Datasets volume:"
    docker volume inspect $(docker-compose ps -q analyst-agent | head -1 | xargs docker inspect --format='{{range .Mounts}}{{if eq .Destination "/app/analyst-service/datasets"}}{{.Name}}{{end}}{{end}}') >/dev/null 2>&1 && echo "✅ Datasets volume exists" || echo "❌ Datasets volume missing"

    echo "   📋 History volume:"
    docker volume inspect $(docker-compose ps -q analyst-agent | head -1 | xargs docker inspect --format='{{range .Mounts}}{{if eq .Destination "/app/analyst-service/history"}}{{.Name}}{{end}}{{end}}') >/dev/null 2>&1 && echo "✅ History volume exists" || echo "❌ History volume missing"
}

# Function to show container logs
show_logs() {
    echo ""
    echo "📝 Recent container logs (startup):"
    docker logs ai-data-analyst --tail 20 2>/dev/null || echo "❌ Could not retrieve logs"
}

# Main execution
if check_container; then
    check_container_files
    check_volumes
    show_logs

    echo ""
    echo "🌐 Access URLs:"
    echo "   📊 Streamlit App: http://localhost:8501"
    echo "   📡 API Server: http://localhost:8502"
    echo ""
    echo "💡 If files are missing, try rebuilding the container:"
    echo "   docker-compose down"
    echo "   docker-compose build analyst-agent"
    echo "   docker-compose up -d analyst-agent"
else
    echo ""
    echo "Please start the analyst-agent container first:"
    echo "   docker-compose up -d analyst-agent"
fi