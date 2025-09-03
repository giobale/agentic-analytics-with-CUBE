#!/bin/bash

echo "🧪 Cube.js Container Testing Script"
echo "=================================="

echo ""
echo "📋 Environment Variables:"
echo "CUBEJS_DB_HOST: $CUBEJS_DB_HOST"
echo "CUBEJS_DB_PORT: $CUBEJS_DB_PORT"
echo "CUBEJS_DB_NAME: $CUBEJS_DB_NAME"
echo "CUBEJS_DB_USER: $CUBEJS_DB_USER"
echo "CUBEJS_DEV_MODE: $CUBEJS_DEV_MODE"
echo "CUBEJS_API_SECRET: $(if [ -n "$CUBEJS_API_SECRET" ]; then echo "SET"; else echo "NOT SET"; fi)"

echo ""
echo "🔌 Testing MySQL Connection:"
echo "mysql -h $CUBEJS_DB_HOST -P $CUBEJS_DB_PORT -u $CUBEJS_DB_USER -p$CUBEJS_DB_PASS -e 'SELECT 1;'"
mysql -h $CUBEJS_DB_HOST -P $CUBEJS_DB_PORT -u $CUBEJS_DB_USER -p$CUBEJS_DB_PASS -e 'SELECT 1;' 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ MySQL connection successful"
else
    echo "❌ MySQL connection failed"
fi

echo ""
echo "🗄️  Listing Tables:"
mysql -h $CUBEJS_DB_HOST -P $CUBEJS_DB_PORT -u $CUBEJS_DB_USER -p$CUBEJS_DB_PASS -e 'USE ticketshopdb; SHOW TABLES;' 2>/dev/null

echo ""
echo "🏥 Testing Cube Health:"
curl -f http://localhost:4000/readyz 2>/dev/null
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Cube health check passed"
else
    echo "❌ Cube health check failed"
fi

echo ""
echo "🔍 Testing Cube Meta API:"

# Check for saved JWT token file
JWT_TOKEN=""
if [ -f "/tmp/cube-jwt-token" ]; then
    JWT_TOKEN=$(cat /tmp/cube-jwt-token 2>/dev/null)
    if [ -n "$JWT_TOKEN" ]; then
        echo "✅ Found JWT token in saved file!"
        
        # Test the JWT token
        echo "🎫 Testing with JWT token..."
        JWT_RESPONSE=$(curl -s -H "Authorization: Bearer $JWT_TOKEN" http://localhost:4000/cubejs-api/v1/meta)
        
        if echo "$JWT_RESPONSE" | grep -q "error\|Error"; then
            echo "❌ JWT authentication failed"
            echo "Response: $(echo "$JWT_RESPONSE" | head -c 300)"
        else
            echo "✅ JWT authentication successful!"
            # Count cubes in response
            CUBE_COUNT=$(echo "$JWT_RESPONSE" | grep -o '"name":' | wc -l)
            echo "📊 Found $CUBE_COUNT cubes in the semantic layer"
            echo "Response preview: $(echo "$JWT_RESPONSE" | head -c 200)..."
        fi
    else
        echo "❌ JWT token file is empty"
    fi
else
    echo "❌ No JWT token file found at /tmp/cube-jwt-token"
    echo "💡 Try restarting the container to generate a new token"
fi

echo ""
echo "✨ Testing completed!"