#!/bin/bash

# DaisyChain Proxy Test Script
# Usage: ./test-proxy.sh <PROXY_URL>

PROXY_URL="${1:-https://your-proxy-url.railway.app}"
API_KEY="387c7f2ef300cc48823b65da982ef77179d8cb18bbdc5acd1a237adc84f39cf4"

echo "Testing DaisyChain Proxy at: $PROXY_URL"
echo "=========================================="
echo ""

# Test 1: Root endpoint
echo "Test 1: Root endpoint (GET /)"
curl -s "$PROXY_URL/" | python3 -m json.tool 2>/dev/null || curl -s "$PROXY_URL/"
echo -e "\n"

# Test 2: Health check
echo "Test 2: Health check (GET /health)"
curl -s "$PROXY_URL/health" | python3 -m json.tool 2>/dev/null || curl -s "$PROXY_URL/health"
echo -e "\n"

# Test 3: API info (requires API key)
echo "Test 3: API info (GET /api/info)"
curl -s -H "X-API-Key: $API_KEY" "$PROXY_URL/api/info" | python3 -m json.tool 2>/dev/null || curl -s -H "X-API-Key: $API_KEY" "$PROXY_URL/api/info"
echo -e "\n"

# Test 4: List devices (requires API key)
echo "Test 4: List devices (GET /api/devices)"
curl -s -H "X-API-Key: $API_KEY" "$PROXY_URL/api/devices" | python3 -m json.tool 2>/dev/null || curl -s -H "X-API-Key: $API_KEY" "$PROXY_URL/api/devices"
echo -e "\n"

# Test 5: Invalid API key
echo "Test 5: Invalid API key test (should return 403)"
curl -s -w "\nHTTP Status: %{http_code}\n" -H "X-API-Key: invalid_key" "$PROXY_URL/api/devices"
echo -e "\n"

echo "=========================================="
echo "Tests complete!"
echo ""
echo "To send a command to a device, use:"
echo "curl -X POST -H 'X-API-Key: $API_KEY' -H 'Content-Type: application/json' \\"
echo "  -d '{\"device_id\":\"node//YOUR_DEVICE_ID\",\"command\":\"whoami\"}' \\"
echo "  $PROXY_URL/api/command"
