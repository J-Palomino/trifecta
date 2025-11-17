# DaisyChain HTTP Proxy API

HTTP REST API for controlling computers via DaisyChain/MeshCentral.

## Features

- Send shell commands to remote devices
- Get screenshots from devices
- List all connected devices
- API key authentication
- CORS enabled for web applications

## Environment Variables

Set these in Railway dashboard:

```bash
DAISYCHAIN_URL=tee.up.railway.app
DAISYCHAIN_TOKEN=<your_login_token>
PROXY_API_KEY=<your_custom_api_key>
```

## API Endpoints

### Health Check
```bash
GET /health
```

### Send Command
```bash
POST /api/command
Headers: X-API-Key: <your_api_key>
Body: {
  "device_id": "node//abc123...",
  "command": "ls -la",
  "timeout": 30
}
```

### Get Screenshot
```bash
POST /api/screenshot
Headers: X-API-Key: <your_api_key>
Body: {
  "device_id": "node//abc123...",
  "timeout": 30
}
```

### List Devices
```bash
GET /api/devices
Headers: X-API-Key: <your_api_key>
```

## Usage Example (Python)

```python
import requests
import base64

API_URL = "https://your-proxy.railway.app"
API_KEY = "your_api_key"

headers = {"X-API-Key": API_KEY}

# Send command
response = requests.post(
    f"{API_URL}/api/command",
    json={
        "device_id": "node//your_device_id",
        "command": "whoami"
    },
    headers=headers
)
print(response.json())

# Get screenshot
response = requests.post(
    f"{API_URL}/api/screenshot",
    json={"device_id": "node//your_device_id"},
    headers=headers
)

screenshot_b64 = response.json()["screenshot"]
with open("screenshot.png", "wb") as f:
    f.write(base64.b64decode(screenshot_b64))
```

## Deployment

1. Create new service in Railway
2. Point to `proxy/` directory
3. Set environment variables
4. Deploy

## Local Development

```bash
cd proxy
pip install -r requirements.txt
export DAISYCHAIN_URL=tee.up.railway.app
export DAISYCHAIN_TOKEN=your_token
export PROXY_API_KEY=test_key
python -m uvicorn app:app --reload
```

Access API docs at: http://localhost:8000/docs
