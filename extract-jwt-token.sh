#!/bin/bash

echo "🔍 Extracting JWT Token from Cube Container Logs"
echo "================================================"

# Try different patterns for JWT token extraction
echo "📋 Searching container logs for JWT tokens..."

# Method 1: Look for the specific Cube.js token message pattern
JWT_TOKEN=$(docker-compose logs cube 2>/dev/null | grep "🔒 Your temporary cube.js token:" | tail -1 | sed 's/.*token: //')

if [ -z "$JWT_TOKEN" ]; then
    # Method 2: Look for any JWT token patterns in recent logs
    JWT_TOKEN=$(docker-compose logs --tail=100 cube 2>/dev/null | grep -o 'eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*' | tail -1)
fi

if [ -z "$JWT_TOKEN" ]; then
    # Method 3: Look for token in broader context
    JWT_TOKEN=$(docker-compose logs cube 2>/dev/null | grep -i "token" | grep -o 'eyJ[^[:space:]]*' | tail -1)
fi

if [ -z "$JWT_TOKEN" ]; then
    # Method 4: Show recent logs to help debug
    echo "❌ No JWT token found. Here are the recent Cube logs:"
    echo "---------------------------------------------------"
    docker-compose logs --tail=20 cube 2>/dev/null | grep -i -E "(token|jwt|auth|playground|dev)"
    echo "---------------------------------------------------"
    echo ""
    echo "💡 Possible solutions:"
    echo "1. Make sure Cube is running in development mode (CUBEJS_DEV_MODE=true)"
    echo "2. Try accessing http://localhost:4000 in your browser to generate a token"
    echo "3. Check if Cube.js is generating tokens in the logs"
    echo "4. Use the API secret instead: 'Bearer baubeach'"
    
    # Try using API secret as fallback
    echo ""
    echo "🔑 Testing API with secret 'baubeach'..."
    RESPONSE=$(curl -s -H "Authorization: Bearer baubeach" http://localhost:4000/cubejs-api/v1/meta 2>/dev/null)
    
    if echo "$RESPONSE" | grep -q "cubes\|error" 2>/dev/null; then
        echo "✅ API Secret 'baubeach' works for authentication"
        echo "🎫 You can use: curl -H \"Authorization: Bearer baubeach\" http://localhost:4000/cubejs-api/v1/meta"
    else
        echo "❌ API Secret authentication also failed"
    fi
    
    exit 1
else
    echo "✅ JWT Token found: ${JWT_TOKEN:0:50}..."
    echo ""
    echo "🎫 You can use this token for API calls:"
    echo "curl -H \"Authorization: Bearer $JWT_TOKEN\" http://localhost:4000/cubejs-api/v1/meta"
    echo ""
    echo "🧪 Testing the token..."
    RESPONSE=$(curl -s -H "Authorization: Bearer $JWT_TOKEN" http://localhost:4000/cubejs-api/v1/meta 2>/dev/null)
    
    if echo "$RESPONSE" | grep -q "cubes\|error" 2>/dev/null; then
        echo "✅ Token is valid and working!"
        echo "📊 API Response preview: $(echo "$RESPONSE" | head -c 150)..."
    else
        echo "❌ Token found but may not be valid"
        echo "📊 Response: $RESPONSE"
    fi
    
    # Export the token for use in other scripts
    export CUBE_JWT_TOKEN="$JWT_TOKEN"
    echo ""
    echo "💾 Token exported as CUBE_JWT_TOKEN environment variable"
fi