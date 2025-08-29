#!/bin/bash
set -e

# Create log directory
mkdir -p /var/log/mysql
chown -R mysql:mysql /var/log/mysql

# Start MySQL in the background
echo "Starting MySQL server..."
mysqld --user=mysql --daemonize --pid-file=/var/run/mysqld/mysqld.pid

# Wait for MySQL to be ready
echo "Waiting for MySQL to be ready..."
while ! mysqladmin ping -h localhost --silent; do
    sleep 1
done

echo "MySQL is ready!"

# Start the CSV import service in the background
echo "Starting CSV import service..."
python3 /mysql-container/scripts/csv-import-service.py &

# Keep the container running by following process status
echo "Services started successfully!"
echo "CSV Import Service is monitoring for CSV files in /var/lib/mysql-files/csv-data/"

# Keep container alive by monitoring the CSV service
while true; do
    if ! pgrep -f "csv-import-service.py" > /dev/null; then
        echo "CSV import service stopped. Restarting..."
        python3 /mysql-container/scripts/csv-import-service.py &
    fi
    sleep 30
done