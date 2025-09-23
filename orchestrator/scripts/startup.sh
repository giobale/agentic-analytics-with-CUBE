#!/bin/bash
# ABOUTME: Startup script for orchestrator container
# ABOUTME: Generates system prompt on startup and starts health check server

set -e

APP_HOME="/app"
CACHE_DIR="/app/cache"
SYSTEM_PROMPT_FILE="${CACHE_DIR}/system_prompt.txt"
SYSTEM_PROMPT_METADATA="${CACHE_DIR}/system_prompt_metadata.json"
LOG_FILE="/app/logs/orchestrator.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] ✅ $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ❌ $1${NC}" | tee -a "$LOG_FILE"
}

# Function to generate system prompt
generate_system_prompt() {
    log "Generating system prompt..."

    cd "$APP_HOME"

    if python3 -c "
import sys
import os
import json
from datetime import datetime

# Add the context_preparation directory to Python path
sys.path.insert(0, '/app/system-prompt-generator/context_preparation')
sys.path.insert(0, '/app/system-prompt-generator/utils')
sys.path.insert(0, '/app/system-prompt-generator')

print('Python paths added for system prompt generation')

try:
    # Import context manager directly from the file
    from context_manager import ContextManager

    print('ContextManager imported successfully')
    context_manager = ContextManager('/app/system-prompt-generator')
    print('Context manager created, generating prompt...')
    result = context_manager.generate_system_prompt()
    print('System prompt generated successfully')

    # Save system prompt to cache
    with open('$SYSTEM_PROMPT_FILE', 'w', encoding='utf-8') as f:
        f.write(result['system_prompt'])

    # Save metadata
    metadata = {
        'generated_at': datetime.now().isoformat(),
        'length': len(result['system_prompt']),
        'metadata': result.get('metadata', {})
    }

    with open('$SYSTEM_PROMPT_METADATA', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print(f'Cached system prompt: {len(result[\"system_prompt\"])} characters')

except Exception as e:
    print(f'Error generating system prompt: {str(e)}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"; then
        log_success "System prompt generated and cached"
        return 0
    else
        log_error "Failed to generate system prompt"
        return 1
    fi
}

# Function to wait for dependencies
wait_for_dependencies() {
    log "Waiting for CUBE instance to be ready..."

    CUBE_URL="${CUBE_BASE_URL:-http://cube-core:4000}"
    MAX_ATTEMPTS=30
    ATTEMPT=1

    while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
        if curl -s "${CUBE_URL}/readyz" > /dev/null 2>&1; then
            log_success "CUBE instance is ready"
            return 0
        fi

        log "Attempt ${ATTEMPT}/${MAX_ATTEMPTS}: CUBE not ready yet, waiting 5 seconds..."
        sleep 5
        ATTEMPT=$((ATTEMPT + 1))
    done

    log_error "CUBE instance did not become ready within expected time"
    return 1
}

# Function to start API server
start_api_server() {
    log "Starting FastAPI server on port 8080..."

    # Start the full API server
    python3 api_server.py &

    API_SERVER_PID=$!
    log_success "API server started (PID: $API_SERVER_PID)"
}

# Main startup sequence
main() {
    log "🚀 Starting Orchestrator Service"
    log "================================"

    # Check if system prompt already exists
    if [ -f "$SYSTEM_PROMPT_FILE" ]; then
        log_success "System prompt cache found, skipping generation"
    else
        # Wait for dependencies
        if ! wait_for_dependencies; then
            log_error "Dependencies not ready, exiting"
            exit 1
        fi

        # Generate system prompt
        if ! generate_system_prompt; then
            log_error "System prompt generation failed, exiting"
            exit 1
        fi
    fi

    # Start API server
    start_api_server

    log_success "Orchestrator service initialization complete"
    log "Service is now ready to handle requests"

    # Keep the container running
    wait
}

# Handle shutdown gracefully
cleanup() {
    log "Shutting down orchestrator service..."
    if [ ! -z "$API_SERVER_PID" ]; then
        kill $API_SERVER_PID 2>/dev/null || true
    fi
    log_success "Orchestrator service stopped"
    exit 0
}

trap cleanup SIGTERM SIGINT

# Start the service
main