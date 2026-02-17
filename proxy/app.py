#!/usr/bin/env python3
"""
Simple MeshCentral Proxy API with 3 main routes:
- /getDevices - Returns list of available devices
- /getScreen - Returns screenshot of chosen device
- /sendCommand - Sends command to chosen device
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import Response
from pydantic import BaseModel
from contextlib import asynccontextmanager
import websocket
import json
import base64
import os
import threading
import queue
import logging
import time
import uuid
import re
import shlex
from typing import Optional, Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
MESHCENTRAL_URL = os.getenv('DAISYCHAIN_URL', 'tee.up.railway.app')
MESHCENTRAL_USERNAME = os.getenv('MESHCENTRAL_USERNAME')
MESHCENTRAL_PASSWORD = os.getenv('MESHCENTRAL_PASSWORD')
PROXY_API_KEY = os.getenv('PROXY_API_KEY')

# Global WebSocket manager
ws_manager = None

class MeshCentralWebSocketManager:
    """Manages persistent WebSocket connection to MeshCentral"""

    def __init__(self, url: str, username: str, password: str):
        self.url = url if url.startswith('wss://') else f'wss://{url}/control.ashx'
        self.username = username
        self.password = password
        self.ws = None
        self.connected = False
        self.authenticated = False
        self._lock = threading.Lock()
        self.response_queues: Dict[str, queue.Queue] = {}
        self.devices = {}
        self.listener_thread = None
        self.should_run = True

    def _create_auth_header(self):
        """Create x-meshauth header with base64 encoded credentials"""
        username_b64 = base64.b64encode(self.username.encode()).decode()
        password_b64 = base64.b64encode(self.password.encode()).decode()
        return f"{username_b64},{password_b64}"

    def connect(self):
        """Establish WebSocket connection"""
        try:
            logger.info(f"Connecting to MeshCentral WebSocket: {self.url}")

            auth_header = self._create_auth_header()

            self.ws = websocket.WebSocketApp(
                self.url,
                header=[f"x-meshauth: {auth_header}"],
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
                on_open=self._on_open
            )

            # Start listener in background thread
            self.listener_thread = threading.Thread(target=self._run_forever, daemon=True)
            self.listener_thread.start()

            # Wait for connection
            for _ in range(100):
                if self.authenticated:
                    return True
                time.sleep(0.1)

            return self.connected

        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
            return False

    def _run_forever(self):
        """Run WebSocket in background"""
        while self.should_run:
            try:
                self.ws.run_forever()
                if self.should_run:
                    logger.info("WebSocket disconnected, reconnecting in 5s...")
                    time.sleep(5)
                    # Recreate WebSocket object for reconnection
                    auth_header = self._create_auth_header()
                    with self._lock:
                        self.ws = websocket.WebSocketApp(
                            self.url,
                            header=[f"x-meshauth: {auth_header}"],
                            on_message=self._on_message,
                            on_error=self._on_error,
                            on_close=self._on_close,
                            on_open=self._on_open
                        )
            except Exception as e:
                logger.error(f"WebSocket run error: {e}")
                time.sleep(5)

    def _on_open(self, ws):
        """Handle WebSocket connection established"""
        logger.info("WebSocket connection established")
        self.connected = True
        # Request device list
        ws.send(json.dumps({'action': 'nodes'}))

    def _on_message(self, ws, message):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            action = data.get('action', 'unknown')

            # Handle nodes list - means we're authenticated
            if action == 'nodes':
                if 'nodes' in data:
                    self.devices = data['nodes']
                    self.authenticated = True
                    logger.info(f"Authenticated! Received {len(self.devices)} device groups")

            # Handle authentication response
            elif action == 'authcookie':
                self.authenticated = True
                logger.info("WebSocket authenticated successfully")
                # Request device list
                self._send({'action': 'nodes'})

            # Handle close/error messages
            elif action == 'close':
                cause = data.get('cause', 'unknown')
                logger.error(f"MeshCentral closed connection: {data}")
                if cause == 'noauth':
                    logger.error("Authentication failed - check credentials")
                self.authenticated = False

            # Handle event updates (device status changes)
            elif action == 'event':
                event = data.get('event', {})
                if event.get('action') in ['addnode', 'changenode']:
                    # Refresh device list
                    self._send({'action': 'nodes'})

            # Route responses to waiting queues
            msg_id = data.get('responseid') or data.get('tag')
            if msg_id and msg_id in self.response_queues:
                self.response_queues[msg_id].put(data)

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message: {message}")
        except Exception as e:
            logger.error(f"Message handling error: {e}")

    def _on_error(self, ws, error):
        """Handle WebSocket errors"""
        logger.error(f"WebSocket error: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket connection closed"""
        logger.info(f"WebSocket closed: {close_status_code} - {close_msg}")
        self.connected = False
        self.authenticated = False

    def _send(self, data: Dict) -> bool:
        """Send message via WebSocket"""
        try:
            with self._lock:
                if self.ws and self.connected:
                    self.ws.send(json.dumps(data))
                    return True
            return False
        except Exception as e:
            logger.error(f"Send error: {e}")
            return False

    def send_and_wait(self, data: Dict, timeout: int = 10) -> Optional[Dict]:
        """Send message and wait for response"""
        if not self.connected or not self.authenticated:
            return None

        # Add unique message ID using MeshCentral's responseid system
        msg_id = str(uuid.uuid4())
        data['responseid'] = msg_id

        # Create response queue
        response_queue = queue.Queue()
        self.response_queues[msg_id] = response_queue

        # Send message
        if not self._send(data):
            self.response_queues.pop(msg_id, None)
            return None

        # Wait for response
        try:
            return response_queue.get(timeout=timeout)
        except queue.Empty:
            return None
        finally:
            self.response_queues.pop(msg_id, None)

    def get_devices_list(self) -> List[Dict]:
        """Get list of all devices in simple format"""
        devices_list = []

        for mesh_id, devices_in_mesh in self.devices.items():
            if isinstance(devices_in_mesh, list):
                for device in devices_in_mesh:
                    node_id = device.get('_id', '')
                    name = device.get('name', 'Unknown')
                    conn = device.get('conn', 0)
                    online = (conn & 1) != 0
                    os_desc = device.get('osdesc', 'Unknown OS')
                    ip = device.get('ip', 'N/A')

                    devices_list.append({
                        'id': node_id,
                        'name': name,
                        'online': online,
                        'os': os_desc,
                        'ip': ip
                    })

        return devices_list

    def execute_command(self, node_id: str, command: str) -> Optional[Dict]:
        """Execute shell command on device"""
        msg = {
            'action': 'runcommands',
            'nodeids': [node_id],
            'type': 0,  # 0=shell, 1=cmd, 2=powershell
            'cmds': command,
            'runAsUser': 0  # 0=run as root/agent, 1=run as logged-in user
        }
        return self.send_and_wait(msg, timeout=150)

    def get_screenshot(self, node_id: str) -> Optional[bytes]:
        """Request screenshot from device"""
        msg = {
            'action': 'msg',
            'nodeid': node_id,
            'type': 'screenshot'
        }
        response = self.send_and_wait(msg, timeout=150)

        if response and 'data' in response:
            try:
                return base64.b64decode(response['data'])
            except Exception as e:
                logger.error(f"Screenshot decode error: {e}")
        return None

    def disconnect(self):
        """Close WebSocket connection"""
        self.should_run = False
        with self._lock:
            if self.ws:
                self.ws.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    global ws_manager

    # Startup
    logger.info("=" * 60)
    logger.info("MeshCentral Proxy API v1.0.6")
    logger.info(f"MeshCentral URL: {MESHCENTRAL_URL}")
    logger.info("=" * 60)

    # Validate required env vars
    missing = []
    if not MESHCENTRAL_USERNAME:
        missing.append("MESHCENTRAL_USERNAME")
    if not MESHCENTRAL_PASSWORD:
        missing.append("MESHCENTRAL_PASSWORD")
    if not PROXY_API_KEY:
        missing.append("PROXY_API_KEY")
    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

    # Initialize WebSocket manager
    WS_URL = f'wss://{MESHCENTRAL_URL}/control.ashx' if not MESHCENTRAL_URL.startswith('wss://') else MESHCENTRAL_URL
    ws_manager = MeshCentralWebSocketManager(WS_URL, MESHCENTRAL_USERNAME, MESHCENTRAL_PASSWORD)

    # Connect in background
    threading.Thread(target=ws_manager.connect, daemon=True).start()

    # Wait for connection
    time.sleep(3)

    if ws_manager.connected and ws_manager.authenticated:
        logger.info("Successfully connected to MeshCentral")
    else:
        logger.error("Failed to connect to MeshCentral - check credentials")

    yield

    # Shutdown
    if ws_manager:
        ws_manager.disconnect()


app = FastAPI(
    title="MeshCentral Proxy API",
    description="Simple API for MeshCentral device control",
    version="1.0.6",
    lifespan=lifespan
)


# Request/Response models
class CommandRequest(BaseModel):
    device_id: str
    command: str

class ScreenshotRequest(BaseModel):
    device_id: str


def verify_api_key(x_api_key: str = Header(None)):
    """Verify API key from header"""
    if x_api_key != PROXY_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key


# API Endpoints

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy" if (ws_manager and ws_manager.authenticated) else "degraded",
        "connected": ws_manager.connected if ws_manager else False,
        "authenticated": ws_manager.authenticated if ws_manager else False,
        "version": "1.0.6"
    }


@app.get("/getDevices")
async def get_devices(x_api_key: str = Header(None)):
    """Get list of all available devices"""
    verify_api_key(x_api_key)

    if ws_manager is None or not ws_manager.authenticated:
        raise HTTPException(status_code=503, detail="Not connected to MeshCentral")

    devices = ws_manager.get_devices_list()

    return {
        "success": True,
        "count": len(devices),
        "devices": devices
    }


@app.post("/sendCommand")
async def send_command(request: CommandRequest, x_api_key: str = Header(None)):
    """Send command to a device"""
    verify_api_key(x_api_key)

    if ws_manager is None or not ws_manager.authenticated:
        raise HTTPException(status_code=503, detail="Not connected to MeshCentral")

    result = ws_manager.execute_command(request.device_id, request.command)

    if result:
        return {
            "success": True,
            "device_id": request.device_id,
            "command": request.command,
            "output": result.get('result', result.get('value', '')),
            "raw_response": result
        }
    else:
        return {
            "success": False,
            "error": "Command timeout or failed"
        }


@app.post("/getScreen")
async def get_screen(request: ScreenshotRequest, x_api_key: str = Header(None)):
    """Get screenshot from a device"""
    verify_api_key(x_api_key)

    if ws_manager is None or not ws_manager.authenticated:
        raise HTTPException(status_code=503, detail="Not connected to MeshCentral")

    screenshot_data = ws_manager.get_screenshot(request.device_id)

    if screenshot_data:
        return Response(content=screenshot_data, media_type="image/png")
    else:
        raise HTTPException(status_code=500, detail="Screenshot capture failed")


class SaveJsonRequest(BaseModel):
    device_id: str
    path: str  # Directory path on remote device
    data: Dict[str, Any]  # JSON data to save


@app.post("/saveJson")
async def save_json(request: SaveJsonRequest, x_api_key: str = Header(None)):
    """Save JSON data as a timestamped file on a device"""
    verify_api_key(x_api_key)

    if ws_manager is None or not ws_manager.authenticated:
        raise HTTPException(status_code=503, detail="Not connected to MeshCentral")

    # Validate path: only allow safe directory characters, no traversal
    if not re.match(r'^[a-zA-Z0-9/_.\-]+$', request.path) or '..' in request.path:
        raise HTTPException(status_code=400, detail="Invalid path: only alphanumeric, /, _, -, . allowed")

    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"data_{timestamp}.json"
    safe_dir = shlex.quote(request.path.rstrip('/'))
    filepath = f"{request.path.rstrip('/')}/{filename}"
    safe_filepath = shlex.quote(filepath)

    # Base64 encode JSON to avoid any shell interpretation
    json_b64 = base64.b64encode(json.dumps(request.data).encode()).decode()
    command = f"mkdir -p {safe_dir} && echo {shlex.quote(json_b64)} | base64 -d > {safe_filepath}"

    result = ws_manager.execute_command(request.device_id, command)

    if result:
        return {
            "success": True,
            "device_id": request.device_id,
            "filepath": filepath,
            "filename": filename,
            "timestamp": timestamp
        }
    else:
        return {
            "success": False,
            "error": "Failed to save JSON file"
        }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
