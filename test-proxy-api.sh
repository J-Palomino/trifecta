#!/bin/bash
# Test the three main proxy API routes

# Configuration
PROXY_URL="https://heroic-healing-production.up.railway.app"
API_KEY="387c7f2ef300cc48823b65da982ef77179d8cb18bbdc5acd1a237adc84f39cf4"

echo "=========================================="
echo "Testing MeshCentral Proxy API"
echo "=========================================="
echo ""

# Test 1: Get Devices
echo "1. Testing /getDevices endpoint"
echo "-------------------------------------------"
curl -s -H "X-API-Key: $API_KEY" "$PROXY_URL/getDevices" | python -m json.tool
echo ""
echo ""

# Test 2: Send Command
echo "2. Testing /sendCommand endpoint"
echo "-------------------------------------------"
echo "Sending 'whoami' command to yogabook..."
curl -s -X POST \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "node//I0EArrXwS$Fed9O@0AlTR@tYhFA0323skZ8QUv6IDeGIYtdxiJ56SNB$b5tLkLY5",
    "command": "whoami"
  }' \
  "$PROXY_URL/sendCommand" | python -m json.tool
echo ""
echo ""

# Test 3: Get Screenshot
echo "3. Testing /getScreen endpoint"
echo "-------------------------------------------"
echo "Requesting screenshot from yogabook..."
curl -s -X POST \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "node//I0EArrXwS$Fed9O@0AlTR@tYhFA0323skZ8QUv6IDeGIYtdxiJ56SNB$b5tLkLY5"
  }' \
  "$PROXY_URL/getScreen" \
  -o screenshot.png

if [ -f screenshot.png ]; then
  SIZE=$(wc -c < screenshot.png)
  echo "Screenshot saved to screenshot.png (${SIZE} bytes)"
else
  echo "Failed to capture screenshot"
fi

echo ""
echo "=========================================="
echo "Tests Complete!"
echo "=========================================="
