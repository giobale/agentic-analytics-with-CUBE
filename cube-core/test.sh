#!/bin/bash

# ABOUTME: Basic health check script for CUBE service
# ABOUTME: Tests database connection and API readiness

echo "🧪 Testing CUBE service..."

# Test database connection
echo "📊 Testing database connection..."
mysql -h${CUBEJS_DB_HOST:-localhost} -P${CUBEJS_DB_PORT:-3306} -u${CUBEJS_DB_USER:-root} -p${CUBEJS_DB_PASS:-password} -e "SELECT 1;" ${CUBEJS_DB_NAME:-test} 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Database connection successful"
else
    echo "❌ Database connection failed"
    exit 1
fi

# Test CUBE API
echo "🔌 Testing CUBE API..."
curl -f http://localhost:4000/readyz 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ CUBE API is ready"
else
    echo "❌ CUBE API is not ready"
    exit 1
fi

echo "🎉 All tests passed!"