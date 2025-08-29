#!/bin/bash
set -e

# Start the CSV import service in the background after MySQL is ready
start_csv_service() {
    echo "Starting CSV import background service..."
    
    # Wait for MySQL to be fully ready
    while ! mysqladmin ping -h localhost -u root -p"$MYSQL_ROOT_PASSWORD" --silent 2>/dev/null; do
        echo "Waiting for MySQL to be ready for CSV import..."
        sleep 5
    done
    
    echo "MySQL is ready! Starting CSV import service..."
    python3 /mysql-container/scripts/csv-import-service.py
}

# Start CSV service in background
start_csv_service &

# Execute the original MySQL entrypoint
exec /usr/local/bin/docker-entrypoint.sh "$@"