# MeshCentral Proxy API - Complete Guide

## Overview

Your proxy now has **exactly 3 routes** for MeshCentral control:

1. **`/getDevices`** - Returns list of available devices
2. **`/sendCommand`** - Sends command to chosen device
3. **`/getScreen`** - Returns screenshot of chosen device

**Base URL:** `https://heroic-healing-production.up.railway.app`
**API Key:** `387c7f2ef300cc48823b65da982ef77179d8cb18bbdc5acd1a237adc84f39cf4`

---

## Route 1: `/getDevices`

Get list of all connected MeshCentral devices.

### Request

```bash
GET /getDevices
Headers:
  X-API-Key: your-api-key
```

### Example

```bash
curl -H "X-API-Key: 387c7f2ef300cc48823b65da982ef77179d8cb18bbdc5acd1a237adc84f39cf4" \
  https://heroic-healing-production.up.railway.app/getDevices
```

### Response

```json
{
  "success": true,
  "count": 10,
  "devices": [
    {
      "id": "node//I0EArrXwS$Fed9O@0AlTR@tYhFA0323skZ8QUv6IDeGIYtdxiJ56SNB$b5tLkLY5",
      "name": "yogabook",
      "online": true,
      "os": "Microsoft Windows 11 Home - 24H2/26100",
      "ip": "70.172.93.38"
    },
    {
      "id": "node//fKfLAPuGDw76Jh$GxpEuvZEuj7sS89lFCfZAd1ut@P6BY2$Cbh5HFQZMKJCl4gkj",
      "name": "erik",
      "online": true,
      "os": "Ubuntu 24.04.3 LTS",
      "ip": "191.96.31.171"
    },
    ...
  ]
}
```

---

## Route 2: `/sendCommand`

Send a shell command to a specific device.

### Request

```bash
POST /sendCommand
Headers:
  X-API-Key: your-api-key
  Content-Type: application/json
Body:
  {
    "device_id": "node//...",
    "command": "your command here"
  }
```

### Example: Run `whoami`

```bash
curl -X POST \
  -H "X-API-Key: 387c7f2ef300cc48823b65da982ef77179d8cb18bbdc5acd1a237adc84f39cf4" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "node//I0EArrXwS$Fed9O@0AlTR@tYhFA0323skZ8QUv6IDeGIYtdxiJ56SNB$b5tLkLY5",
    "command": "whoami"
  }' \
  https://heroic-healing-production.up.railway.app/sendCommand
```

### Example: Check disk space on Ubuntu device

```bash
curl -X POST \
  -H "X-API-Key: 387c7f2ef300cc48823b65da982ef77179d8cb18bbdc5acd1a237adc84f39cf4" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "node//$gh3JSR2PBAQ3t$oNqQWuwGiBVTtCFKYxVT3SKQZU5zEZxYFNAL864LIWuR7IrTn",
    "command": "df -h"
  }' \
  https://heroic-healing-production.up.railway.app/sendCommand
```

### Response

```json
{
  "success": true,
  "device_id": "node//I0EArrXwS$Fed9O@0AlTR@tYhFA0323skZ8QUv6IDeGIYtdxiJ56SNB$b5tLkLY5",
  "command": "whoami",
  "output": "YOGABOOK\\jpalo\n",
  "raw_response": {
    "action": "runcommands",
    "result": "YOGABOOK\\jpalo\n",
    ...
  }
}
```

---

## Route 3: `/getScreen`

Capture a screenshot from a device.

### Request

```bash
POST /getScreen
Headers:
  X-API-Key: your-api-key
  Content-Type: application/json
Body:
  {
    "device_id": "node//..."
  }
```

### Example: Screenshot from Windows device

```bash
curl -X POST \
  -H "X-API-Key: 387c7f2ef300cc48823b65da982ef77179d8cb18bbdc5acd1a237adc84f39cf4" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "node//I0EArrXwS$Fed9O@0AlTR@tYhFA0323skZ8QUv6IDeGIYtdxiJ56SNB$b5tLkLY5"
  }' \
  https://heroic-healing-production.up.railway.app/getScreen \
  -o screenshot.png
```

### Response

Returns PNG image file directly. Save with `-o filename.png`.

---

## Your Device IDs

For quick reference when making API calls:

### Online Devices (can send commands immediately)

```bash
# yogabook (Windows 11)
YOGABOOK="node//I0EArrXwS$Fed9O@0AlTR@tYhFA0323skZ8QUv6IDeGIYtdxiJ56SNB$b5tLkLY5"

# erik (Ubuntu 24.04)
ERIK="node//fKfLAPuGDw76Jh$GxpEuvZEuj7sS89lFCfZAd1ut@P6BY2$Cbh5HFQZMKJCl4gkj"

# hugo (Ubuntu 24.04)
HUGO="node//$gh3JSR2PBAQ3t$oNqQWuwGiBVTtCFKYxVT3SKQZU5zEZxYFNAL864LIWuR7IrTn"

# nic (Ubuntu 22.04)
NIC="node//froyzjFZ2BrfrM1HOY63apKZet0Rl$KdRa$UAj7hr5cLujnvq9w5C6VAggbbLB$E"

# david (Ubuntu 24.04)
DAVID="node//4dpSLYZRj1nYgYkhiBAjtDHKJ@d4zlLqYRBBRBRwoN@Gaj38L8MwSH4baT2q79ia"
```

---

## Common Use Cases

### 1. Check which devices are online

```bash
curl -H "X-API-Key: 387c7f2ef300cc48823b65da982ef77179d8cb18bbdc5acd1a237adc84f39cf4" \
  https://heroic-healing-production.up.railway.app/getDevices \
  | jq '.devices[] | select(.online==true) | .name'
```

### 2. Run command on all Ubuntu devices

```bash
# First get all Ubuntu device IDs
curl -H "X-API-Key: 387c7f2ef300cc48823b65da982ef77179d8cb18bbdc5acd1a237adc84f39cf4" \
  https://heroic-healing-production.up.railway.app/getDevices \
  | jq -r '.devices[] | select(.os | contains("Ubuntu")) | .id' \
  > ubuntu_devices.txt

# Then loop through and send command to each
while read device_id; do
  echo "Running command on $device_id"
  curl -X POST \
    -H "X-API-Key: 387c7f2ef300cc48823b65da982ef77179d8cb18bbdc5acd1a237adc84f39cf4" \
    -H "Content-Type: application/json" \
    -d "{\"device_id\":\"$device_id\",\"command\":\"uptime\"}" \
    https://heroic-healing-production.up.railway.app/sendCommand
done < ubuntu_devices.txt
```

### 3. Monitor a device

```bash
# Continuous monitoring script
DEVICE_ID="node//I0EArrXwS$Fed9O@0AlTR@tYhFA0323skZ8QUv6IDeGIYtdxiJ56SNB$b5tLkLY5"
API_KEY="387c7f2ef300cc48823b65da982ef77179d8cb18bbdc5acd1a237adc84f39cf4"

while true; do
  echo "=== $(date) ==="
  curl -X POST \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"device_id\":\"$DEVICE_ID\",\"command\":\"top -bn1 | head -20\"}" \
    https://heroic-healing-production.up.railway.app/sendCommand \
    | jq -r '.output'
  sleep 5
done
```

### 4. Take periodic screenshots

```bash
DEVICE_ID="node//I0EArrXwS$Fed9O@0AlTR@tYhFA0323skZ8QUv6IDeGIYtdxiJ56SNB$b5tLkLY5"
API_KEY="387c7f2ef300cc48823b65da982ef77179d8cb18bbdc5acd1a237adc84f39cf4"

for i in {1..10}; do
  timestamp=$(date +%Y%m%d_%H%M%S)
  curl -X POST \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"device_id\":\"$DEVICE_ID\"}" \
    https://heroic-healing-production.up.railway.app/getScreen \
    -o "screenshot_${timestamp}.png"
  echo "Captured screenshot_${timestamp}.png"
  sleep 60  # Wait 1 minute
done
```

---

## Python Example

```python
import requests

API_KEY = "387c7f2ef300cc48823b65da982ef77179d8cb18bbdc5acd1a237adc84f39cf4"
BASE_URL = "https://heroic-healing-production.up.railway.app"
HEADERS = {"X-API-Key": API_KEY}

# Get devices
response = requests.get(f"{BASE_URL}/getDevices", headers=HEADERS)
devices = response.json()['devices']

# Find online devices
online_devices = [d for d in devices if d['online']]
print(f"Found {len(online_devices)} online devices:")
for device in online_devices:
    print(f"  - {device['name']} ({device['os']})")

# Send command to first online device
if online_devices:
    device_id = online_devices[0]['id']
    command_response = requests.post(
        f"{BASE_URL}/sendCommand",
        headers={**HEADERS, "Content-Type": "application/json"},
        json={
            "device_id": device_id,
            "command": "whoami"
        }
    )
    result = command_response.json()
    print(f"\nCommand output: {result['output']}")

    # Get screenshot
    screenshot_response = requests.post(
        f"{BASE_URL}/getScreen",
        headers={**HEADERS, "Content-Type": "application/json"},
        json={"device_id": device_id}
    )
    with open("device_screenshot.png", "wb") as f:
        f.write(screenshot_response.content)
    print("Screenshot saved to device_screenshot.png")
```

---

## Error Handling

### 403 Forbidden
```json
{"detail": "Invalid API key"}
```
**Solution:** Check your `X-API-Key` header

### 503 Service Unavailable
```json
{"detail": "Not connected to MeshCentral"}
```
**Solution:** Wait a moment for proxy to reconnect, or check Railway logs

### Command timeout
```json
{
  "success": false,
  "error": "Command timeout or failed"
}
```
**Solution:** Device may be offline or command took too long (>30s timeout)

---

## Testing

Run the test script:

```bash
bash test-proxy-api.sh
```

Or test individual endpoints:

```bash
# Health check
curl https://heroic-healing-production.up.railway.app/health

# Get devices
curl -H "X-API-Key: 387c7f2ef300cc48823b65da982ef77179d8cb18bbdc5acd1a237adc84f39cf4" \
  https://heroic-healing-production.up.railway.app/getDevices | jq
```

---

## Summary

You now have a simple REST API with 3 endpoints to:
1. **List all devices** - `/getDevices`
2. **Send commands** - `/sendCommand`
3. **Capture screenshots** - `/getScreen`

All accessible via curl or any HTTP client!
