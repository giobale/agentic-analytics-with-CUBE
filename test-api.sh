#!/bin/bash

echo "🔍 Quick API Test Script"
echo "======================="

# Check if cube is running
echo "📊 Checking Cube.js health..."
HEALTH=$(curl -s http://localhost:4000/readyz 2>/dev/null)
echo "Health: $HEALTH"

if [[ "$HEALTH" != *"HEALTH"* ]]; then
    echo "❌ Cube.js is not running or not healthy"
    exit 1
fi

echo ""
echo "🎫 Testing authentication methods..."

# Method 1: Try with API Secret from .env
echo "1️⃣ Testing with API Secret 'baubeach'..."
RESPONSE1=$(curl -s -H "Authorization: Bearer baubeach" http://localhost:4000/cubejs-api/v1/meta 2>/dev/null)
if echo "$RESPONSE1" | grep -q "cubes\|error" 2>/dev/null; then
    if echo "$RESPONSE1" | grep -q "error"; then
        echo "❌ API Secret failed: $(echo "$RESPONSE1" | head -c 100)..."
    else
        echo "✅ API Secret works!"
        echo "📊 Response: $(echo "$RESPONSE1" | head -c 200)..."
        exit 0
    fi
else
    echo "❌ Unexpected response: $(echo "$RESPONSE1" | head -c 100)..."
fi

# Method 2: Extract JWT token from logs
echo ""
echo "2️⃣ Extracting JWT token from container logs..."
JWT_TOKEN=$(docker-compose logs cube 2>/dev/null | grep "🔒 Your temporary cube.js token:" | tail -1 | sed 's/.*token: //')

if [ -n "$JWT_TOKEN" ]; then
    echo "✅ JWT Token found: ${JWT_TOKEN:0:50}..."
    echo "🧪 Testing JWT token..."
    
    RESPONSE2=$(curl -s -H "Authorization: Bearer $JWT_TOKEN" http://localhost:4000/cubejs-api/v1/meta 2>/dev/null)
    if echo "$RESPONSE2" | grep -q "cubes" 2>/dev/null; then
        echo "✅ JWT Token works!"
        echo "📊 Response: $(echo "$RESPONSE2" | head -c 200)..."
        exit 0
    else
        echo "❌ JWT Token failed: $(echo "$RESPONSE2" | head -c 100)..."
    fi
else
    echo "❌ No JWT token found in logs"
fi

# Method 3: Try no auth (development mode)
echo ""
echo "3️⃣ Testing without authentication (dev mode)..."
RESPONSE3=$(curl -s http://localhost:4000/cubejs-api/v1/meta 2>/dev/null)
if echo "$RESPONSE3" | grep -q "cubes" 2>/dev/null; then
    echo "✅ No-auth works in development mode!"
    echo "📊 Response: $(echo "$RESPONSE3" | head -c 200)..."
    exit 0
else
    echo "❌ No-auth failed: $(echo "$RESPONSE3" | head -c 100)..."
fi

echo ""
echo "❌ All authentication methods failed"
echo "💡 Suggestions:"
echo "1. Check if Cube.js is properly configured for development mode"
echo "2. Verify CUBEJS_API_SECRET environment variable"
echo "3. Ensure containers are properly networked"
echo "4. Check container logs: docker-compose logs cube"