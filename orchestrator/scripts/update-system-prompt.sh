#!/bin/bash
# ABOUTME: Manual system prompt update script for orchestrator container
# ABOUTME: Allows updating cached system prompt without container restart

set -e

APP_HOME="/app"
CACHE_DIR="/app/cache"
SYSTEM_PROMPT_FILE="${CACHE_DIR}/system_prompt.txt"
SYSTEM_PROMPT_METADATA="${CACHE_DIR}/system_prompt_metadata.json"
BACKUP_DIR="${CACHE_DIR}/backups"
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

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Function to backup current system prompt
backup_current_prompt() {
    if [ -f "$SYSTEM_PROMPT_FILE" ]; then
        BACKUP_TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
        BACKUP_FILE="${BACKUP_DIR}/system_prompt_backup_${BACKUP_TIMESTAMP}.txt"
        BACKUP_METADATA="${BACKUP_DIR}/system_prompt_metadata_${BACKUP_TIMESTAMP}.json"

        cp "$SYSTEM_PROMPT_FILE" "$BACKUP_FILE"

        if [ -f "$SYSTEM_PROMPT_METADATA" ]; then
            cp "$SYSTEM_PROMPT_METADATA" "$BACKUP_METADATA"
        fi

        log_success "Current system prompt backed up to: $(basename "$BACKUP_FILE")"
        return 0
    else
        log_warning "No existing system prompt to backup"
        return 1
    fi
}

# Function to regenerate system prompt
regenerate_system_prompt() {
    log "Regenerating system prompt..."

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

try:
    # Import context manager directly from the file
    from context_manager import ContextManager

    context_manager = ContextManager('/app/system-prompt-generator')
    result = context_manager.generate_system_prompt()

    # Save system prompt to cache
    with open('$SYSTEM_PROMPT_FILE', 'w', encoding='utf-8') as f:
        f.write(result['system_prompt'])

    # Save metadata
    metadata = {
        'generated_at': datetime.now().isoformat(),
        'length': len(result['system_prompt']),
        'metadata': result.get('metadata', {}),
        'update_type': 'manual_update'
    }

    with open('$SYSTEM_PROMPT_METADATA', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print('System prompt regenerated successfully')
    print(f'New prompt length: {len(result[\"system_prompt\"])} characters')
except Exception as e:
    print(f'Error regenerating system prompt: {str(e)}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"; then
        log_success "System prompt regenerated and cached"
        return 0
    else
        log_error "Failed to regenerate system prompt"
        return 1
    fi
}

# Function to show current system prompt info
show_current_info() {
    if [ -f "$SYSTEM_PROMPT_METADATA" ]; then
        log "Current system prompt information:"
        cat "$SYSTEM_PROMPT_METADATA" | python3 -m json.tool
    else
        log_warning "No system prompt metadata found"
    fi

    if [ -f "$SYSTEM_PROMPT_FILE" ]; then
        PROMPT_SIZE=$(wc -c < "$SYSTEM_PROMPT_FILE")
        log "System prompt file size: $PROMPT_SIZE bytes"
    else
        log_warning "No system prompt file found"
    fi
}

# Function to list backups
list_backups() {
    log "Available system prompt backups:"
    if ls "$BACKUP_DIR"/system_prompt_backup_*.txt >/dev/null 2>&1; then
        for backup in "$BACKUP_DIR"/system_prompt_backup_*.txt; do
            TIMESTAMP=$(basename "$backup" | sed 's/system_prompt_backup_\(.*\)\.txt/\1/')
            SIZE=$(wc -c < "$backup")
            echo "  - $(basename "$backup") (${SIZE} bytes, created: $(echo "$TIMESTAMP" | sed 's/_/ /'))"
        done
    else
        log_warning "No backups found"
    fi
}

# Function to restore from backup
restore_from_backup() {
    local backup_timestamp="$1"

    if [ -z "$backup_timestamp" ]; then
        log_error "Please specify backup timestamp (e.g., 20240903_143022)"
        list_backups
        return 1
    fi

    RESTORE_FILE="${BACKUP_DIR}/system_prompt_backup_${backup_timestamp}.txt"
    RESTORE_METADATA="${BACKUP_DIR}/system_prompt_metadata_${backup_timestamp}.json"

    if [ -f "$RESTORE_FILE" ]; then
        # Backup current before restoring
        backup_current_prompt

        # Restore files
        cp "$RESTORE_FILE" "$SYSTEM_PROMPT_FILE"

        if [ -f "$RESTORE_METADATA" ]; then
            cp "$RESTORE_METADATA" "$SYSTEM_PROMPT_METADATA"
        fi

        log_success "System prompt restored from backup: $backup_timestamp"
    else
        log_error "Backup file not found: $RESTORE_FILE"
        list_backups
        return 1
    fi
}

# Show usage
show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  update          Update system prompt (default)"
    echo "  info            Show current system prompt information"
    echo "  list-backups    List available backups"
    echo "  restore [timestamp] Restore from backup (e.g., 20240903_143022)"
    echo "  help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                        # Update system prompt"
    echo "  $0 update                 # Update system prompt"
    echo "  $0 info                   # Show current prompt info"
    echo "  $0 list-backups           # List all backups"
    echo "  $0 restore 20240903_143022 # Restore specific backup"
}

# Main function
main() {
    local command="${1:-update}"

    case "$command" in
        "update")
            log "🔄 Manual System Prompt Update"
            log "============================="

            # Backup current prompt
            backup_current_prompt

            # Regenerate system prompt
            if regenerate_system_prompt; then
                show_current_info
                log_success "System prompt update completed"
            else
                log_error "System prompt update failed"
                exit 1
            fi
            ;;

        "info")
            log "📊 System Prompt Information"
            log "==========================="
            show_current_info
            ;;

        "list-backups")
            log "📚 System Prompt Backups"
            log "======================="
            list_backups
            ;;

        "restore")
            log "🔄 System Prompt Restore"
            log "======================="
            restore_from_backup "$2"
            ;;

        "help")
            show_usage
            ;;

        *)
            log_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"