"""
DaisyChain Web App v3
Web interface with HTTP-to-WebSocket proxy for MeshCentral device control
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import websocket
import json
import base64
import os
import threading
import queue
import logging
import time
import uuid
from typing import Optional, Dict, List, Any
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DaisyChain Web Control",
    description="Web interface for MeshCentral device management",
    version="3.0.1"
)

# Configuration
MESHCENTRAL_URL = os.getenv('DAISYCHAIN_URL', 'tee.up.railway.app')
MESHCENTRAL_TOKEN = os.getenv('DAISYCHAIN_TOKEN')

if not MESHCENTRAL_URL.startswith('wss://') and not MESHCENTRAL_URL.startswith('ws://'):
    WS_URL = f'wss://{MESHCENTRAL_URL}/control.ashx'
else:
    WS_URL = MESHCENTRAL_URL

# Global WebSocket manager
class MeshCentralWebSocketManager:
    """Manages persistent WebSocket connection to MeshCentral"""

    def __init__(self, ws_url: str, login_token: str):
        self.ws_url = ws_url
        self.login_token = login_token
        self.ws = None
        self.connected = False
        self.authenticated = False
        self.response_queues: Dict[str, queue.Queue] = {}
        self.devices: Dict[str, Any] = {}
        self.listener_thread = None
        self.reconnect_thread = None
        self.should_run = True

    def connect(self):
        """Establish WebSocket connection"""
        try:
            logger.info(f"Connecting to MeshCentral WebSocket: {self.ws_url}")
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
                on_open=self._on_open
            )

            # Start listener in background thread
            self.listener_thread = threading.Thread(target=self._run_forever, daemon=True)
            self.listener_thread.start()

            # Wait for connection
            for _ in range(50):
                if self.connected:
                    break
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
                    self.ws = websocket.WebSocketApp(
                        self.ws_url,
                        on_message=self._on_message,
                        on_error=self._on_error,
                        on_close=self._on_close,
                        on_open=self._on_open
                    )
            except Exception as e:
                logger.error(f"WebSocket run error: {e}")
                time.sleep(5)
                # Recreate WebSocket object after error
                self.ws = websocket.WebSocketApp(
                    self.ws_url,
                    on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close,
                    on_open=self._on_open
                )

    def _on_open(self, ws):
        """Handle WebSocket connection established"""
        logger.info("WebSocket connection established")
        self.connected = True
        self._authenticate()

    def _on_message(self, ws, message):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            logger.info(f"Received: {data.get('action', 'unknown')}")

            # Handle authentication response
            if data.get('action') == 'authcookie':
                self.authenticated = True
                logger.info("WebSocket authenticated successfully")
                # Request device list
                self._send({'action': 'nodes'})

            # Handle close/error messages
            elif data.get('action') == 'close':
                logger.error(f"MeshCentral closed connection: {data}")
                self.authenticated = False

            # Handle node list
            elif data.get('action') == 'nodes':
                if 'nodes' in data:
                    self.devices = data['nodes']
                    logger.info(f"Received {len(self.devices)} devices")

            # Handle event updates (device status changes)
            elif data.get('action') == 'event':
                event = data.get('event', {})
                if event.get('action') == 'addnode' or event.get('action') == 'changenode':
                    node_id = event.get('nodeid')
                    if node_id:
                        self.devices[node_id] = event.get('node', {})

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

    def _authenticate(self):
        """Authenticate with MeshCentral using login token"""
        auth_msg = {
            'action': 'authcookie',
            'cookie': self.login_token
        }
        self._send(auth_msg)

    def _send(self, data: Dict) -> bool:
        """Send message via WebSocket"""
        try:
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

        # Add unique message ID
        msg_id = str(uuid.uuid4())
        data['tag'] = msg_id

        # Create response queue
        response_queue = queue.Queue()
        self.response_queues[msg_id] = response_queue

        # Send message
        if not self._send(data):
            del self.response_queues[msg_id]
            return None

        # Wait for response
        try:
            response = response_queue.get(timeout=timeout)
            del self.response_queues[msg_id]
            return response
        except queue.Empty:
            del self.response_queues[msg_id]
            return None

    def get_devices(self) -> Dict[str, Any]:
        """Get cached device list"""
        return self.devices

    def execute_command(self, node_id: str, command: str) -> Optional[Dict]:
        """Execute shell command on device"""
        msg = {
            'action': 'msg',
            'nodeid': node_id,
            'type': 'console',
            'value': command
        }
        return self.send_and_wait(msg, timeout=30)

    def get_screenshot(self, node_id: str) -> Optional[bytes]:
        """Request screenshot from device"""
        msg = {
            'action': 'msg',
            'nodeid': node_id,
            'type': 'screenshot'
        }
        response = self.send_and_wait(msg, timeout=30)

        if response and 'data' in response:
            # Decode base64 screenshot data
            try:
                return base64.b64decode(response['data'])
            except Exception as e:
                logger.error(f"Screenshot decode error: {e}")
        return None

    def disconnect(self):
        """Close WebSocket connection"""
        self.should_run = False
        if self.ws:
            self.ws.close()

# Initialize WebSocket manager
ws_manager = MeshCentralWebSocketManager(WS_URL, MESHCENTRAL_TOKEN)

# Request/Response models
class CommandRequest(BaseModel):
    node_id: str
    command: str

class MultiCommandRequest(BaseModel):
    node_ids: List[str]  # List of device IDs
    command: str

class ScreenshotRequest(BaseModel):
    node_id: str

# Startup/Shutdown events
@app.on_event("startup")
async def startup():
    """Connect to MeshCentral on startup"""
    logger.info("=" * 60)
    logger.info("DaisyChain Web App v3.0.0")
    logger.info(f"MeshCentral WebSocket: {WS_URL}")
    logger.info("=" * 60)

    if not MESHCENTRAL_TOKEN:
        logger.error("DAISYCHAIN_TOKEN not set!")
        return

    # Connect in background
    threading.Thread(target=ws_manager.connect, daemon=True).start()

    # Wait a bit for connection
    time.sleep(2)

    if ws_manager.connected:
        logger.info("Successfully connected to MeshCentral")
    else:
        logger.error("Failed to connect to MeshCentral")

@app.on_event("shutdown")
async def shutdown():
    """Disconnect on shutdown"""
    ws_manager.disconnect()

# Web UI endpoint
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve web UI"""
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>DaisyChain Device Control</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2em; margin-bottom: 10px; }
        .header p { opacity: 0.9; }
        .status {
            padding: 15px 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #dc3545;
            animation: pulse 2s infinite;
        }
        .status-dot.connected { background: #28a745; }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .content { padding: 30px; }
        .section {
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .section h2 {
            margin-bottom: 15px;
            color: #495057;
            font-size: 1.3em;
        }
        .device-list {
            display: grid;
            gap: 15px;
        }
        .device-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            border: 2px solid #e9ecef;
            transition: all 0.3s;
        }
        .device-card:hover {
            border-color: #667eea;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
        }
        .device-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .device-name {
            font-weight: 600;
            font-size: 1.1em;
            color: #212529;
        }
        .device-status {
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
        }
        .device-status.online {
            background: #d4edda;
            color: #155724;
        }
        .device-status.offline {
            background: #f8d7da;
            color: #721c24;
        }
        .device-info {
            color: #6c757d;
            font-size: 0.9em;
            margin-bottom: 15px;
        }
        .device-actions {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        button {
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
            font-size: 0.9em;
        }
        .btn-primary {
            background: #667eea;
            color: white;
        }
        .btn-primary:hover {
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }
        .btn-success {
            background: #28a745;
            color: white;
        }
        .btn-success:hover {
            background: #218838;
        }
        .btn-refresh {
            background: #17a2b8;
            color: white;
        }
        .btn-refresh:hover {
            background: #138496;
        }
        input[type="text"] {
            padding: 10px;
            border: 2px solid #e9ecef;
            border-radius: 6px;
            font-size: 0.9em;
            width: 100%;
            max-width: 400px;
        }
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }
        .command-form {
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
        }
        .output {
            margin-top: 15px;
            padding: 15px;
            background: #212529;
            color: #00ff00;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            white-space: pre-wrap;
            max-height: 300px;
            overflow-y: auto;
            display: none;
        }
        .output.visible { display: block; }
        .screenshot-container {
            margin-top: 15px;
            display: none;
        }
        .screenshot-container.visible { display: block; }
        .screenshot-container img {
            max-width: 100%;
            border-radius: 6px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .device-select {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .device-checkbox {
            width: 20px;
            height: 20px;
            cursor: pointer;
            accent-color: #667eea;
        }
        .multi-result {
            margin-bottom: 10px;
            padding: 10px;
            background: #343a40;
            border-left: 4px solid #667eea;
        }
        .multi-result .device-name {
            color: #00ff00;
            font-weight: bold;
        }
        .multi-result .command-output {
            color: #00ff00;
            margin-top: 5px;
        }
        .multi-result.error {
            border-left-color: #dc3545;
        }
        .multi-result.error .command-output {
            color: #ff6b6b;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>DaisyChain Device Control</h1>
            <p>Manage your MeshCentral devices</p>
        </div>

        <div class="status">
            <div class="status-indicator">
                <div class="status-dot" id="statusDot"></div>
                <span id="statusText">Connecting...</span>
            </div>
            <button class="btn-refresh" onclick="refreshDevices()">Refresh Devices</button>
        </div>

        <div class="content">
            <div class="section">
                <h2>Multi-Device Command</h2>
                <div style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <div class="command-form" style="margin-bottom: 15px;">
                        <input type="text" id="multiCommand" placeholder="Enter command to run on selected devices" style="flex: 1;">
                        <button class="btn-primary" onclick="runMultiCommand()" id="multiRunBtn" disabled>
                            Run on Selected (0)
                        </button>
                        <button class="btn-success" onclick="selectAll()">Select All</button>
                        <button class="btn-refresh" onclick="deselectAll()">Deselect All</button>
                    </div>
                    <div class="output" id="multiOutput"></div>
                </div>
            </div>

            <div class="section">
                <h2>Connected Devices</h2>
                <div class="device-list" id="deviceList">
                    <p>Loading devices...</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        async function checkStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();

                const statusDot = document.getElementById('statusDot');
                const statusText = document.getElementById('statusText');

                if (data.connected && data.authenticated) {
                    statusDot.classList.add('connected');
                    statusText.textContent = `Connected (${data.device_count} devices)`;
                } else if (data.connected) {
                    statusText.textContent = 'Connected (authenticating...)';
                } else {
                    statusDot.classList.remove('connected');
                    statusText.textContent = 'Disconnected';
                }
            } catch (error) {
                console.error('Status check failed:', error);
            }
        }

        async function refreshDevices() {
            try {
                const response = await fetch('/api/devices');
                const data = await response.json();

                const deviceList = document.getElementById('deviceList');

                if (!data.devices || Object.keys(data.devices).length === 0) {
                    deviceList.innerHTML = '<p>No devices found. Make sure MeshAgent is installed and running on your devices.</p>';
                    return;
                }

                deviceList.innerHTML = '';

                for (const [nodeId, device] of Object.entries(data.devices)) {
                    const card = createDeviceCard(nodeId, device);
                    deviceList.appendChild(card);
                }
            } catch (error) {
                console.error('Failed to load devices:', error);
                document.getElementById('deviceList').innerHTML = '<p>Error loading devices. Please try again.</p>';
            }
        }

        function createDeviceCard(nodeId, device) {
            const card = document.createElement('div');
            card.className = 'device-card';

            const name = device.name || 'Unknown Device';
            const conn = device.conn || 0;
            const isOnline = (conn & 1) !== 0;

            card.innerHTML = `
                <div class="device-header">
                    <div class="device-select">
                        <input type="checkbox" class="device-checkbox" id="select-${nodeId}"
                               data-node-id="${nodeId}" onchange="updateMultiButton()"
                               ${!isOnline ? 'disabled' : ''}>
                        <div class="device-name">${name}</div>
                    </div>
                    <div class="device-status ${isOnline ? 'online' : 'offline'}">
                        ${isOnline ? 'Online' : 'Offline'}
                    </div>
                </div>
                <div class="device-info">
                    ID: ${nodeId}<br>
                    ${device.osdesc || 'No OS info'}
                </div>
                <div class="command-form">
                    <input type="text" id="cmd-${nodeId}" placeholder="Enter command (e.g., whoami, ls)"
                           ${!isOnline ? 'disabled' : ''}>
                    <button class="btn-primary" onclick="sendCommand('${nodeId}')"
                            ${!isOnline ? 'disabled' : ''}>Execute</button>
                    <button class="btn-success" onclick="getScreenshot('${nodeId}')"
                            ${!isOnline ? 'disabled' : ''}>Screenshot</button>
                </div>
                <div class="output" id="output-${nodeId}"></div>
                <div class="screenshot-container" id="screenshot-${nodeId}"></div>
            `;

            return card;
        }

        function updateMultiButton() {
            const checkboxes = document.querySelectorAll('.device-checkbox:checked');
            const count = checkboxes.length;
            const btn = document.getElementById('multiRunBtn');
            btn.textContent = `Run on Selected (${count})`;
            btn.disabled = count === 0;
        }

        function selectAll() {
            const checkboxes = document.querySelectorAll('.device-checkbox:not(:disabled)');
            checkboxes.forEach(cb => cb.checked = true);
            updateMultiButton();
        }

        function deselectAll() {
            const checkboxes = document.querySelectorAll('.device-checkbox');
            checkboxes.forEach(cb => cb.checked = false);
            updateMultiButton();
        }

        async function runMultiCommand() {
            const command = document.getElementById('multiCommand').value.trim();
            if (!command) {
                alert('Please enter a command');
                return;
            }

            const checkboxes = document.querySelectorAll('.device-checkbox:checked');
            const nodeIds = Array.from(checkboxes).map(cb => cb.getAttribute('data-node-id'));

            if (nodeIds.length === 0) {
                alert('Please select at least one device');
                return;
            }

            const output = document.getElementById('multiOutput');
            output.textContent = `Running "${command}" on ${nodeIds.length} device(s)...`;
            output.classList.add('visible');

            try {
                const response = await fetch('/api/command/multi', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ node_ids: nodeIds, command: command })
                });

                const data = await response.json();

                if (data.success) {
                    output.innerHTML = '';
                    for (const [nodeId, result] of Object.entries(data.results)) {
                        const resultDiv = document.createElement('div');
                        resultDiv.className = `multi-result ${result.success ? '' : 'error'}`;

                        const deviceName = getDeviceName(nodeId);
                        resultDiv.innerHTML = `
                            <div class="device-name">${deviceName} (${nodeId})</div>
                            <div class="command-output">$ ${command}\n${result.output || result.error}</div>
                        `;
                        output.appendChild(resultDiv);
                    }
                } else {
                    output.textContent = `Error: ${data.error || 'Multi-command failed'}`;
                }
            } catch (error) {
                output.textContent = `Error: ${error.message}`;
            }
        }

        function getDeviceName(nodeId) {
            const checkbox = document.getElementById(`select-${nodeId}`);
            if (checkbox) {
                const card = checkbox.closest('.device-card');
                const nameEl = card.querySelector('.device-name');
                return nameEl ? nameEl.textContent.trim() : 'Unknown';
            }
            return 'Unknown';
        }

        async function sendCommand(nodeId) {
            const input = document.getElementById(`cmd-${nodeId}`);
            const output = document.getElementById(`output-${nodeId}`);
            const command = input.value.trim();

            if (!command) return;

            output.textContent = 'Executing command...';
            output.classList.add('visible');

            try {
                const response = await fetch('/api/command', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ node_id: nodeId, command: command })
                });

                const data = await response.json();

                if (data.success) {
                    output.textContent = `$ ${command}\n${data.output || 'Command sent successfully'}`;
                } else {
                    output.textContent = `Error: ${data.error || 'Command failed'}`;
                }
            } catch (error) {
                output.textContent = `Error: ${error.message}`;
            }
        }

        async function getScreenshot(nodeId) {
            const container = document.getElementById(`screenshot-${nodeId}`);
            container.innerHTML = '<p>Capturing screenshot... <span class="loading"></span></p>';
            container.classList.add('visible');

            try {
                const response = await fetch('/api/screenshot', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ node_id: nodeId })
                });

                if (response.ok) {
                    const blob = await response.blob();
                    const url = URL.createObjectURL(blob);
                    container.innerHTML = `<img src="${url}" alt="Screenshot">`;
                } else {
                    const data = await response.json();
                    container.innerHTML = `<p>Error: ${data.error || 'Screenshot failed'}</p>`;
                }
            } catch (error) {
                container.innerHTML = `<p>Error: ${error.message}</p>`;
            }
        }

        // Initialize
        checkStatus();
        refreshDevices();

        // Refresh status every 5 seconds
        setInterval(checkStatus, 5000);
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

# API Endpoints
@app.get("/api/status")
async def get_status():
    """Get connection status"""
    return {
        "connected": ws_manager.connected,
        "authenticated": ws_manager.authenticated,
        "device_count": len(ws_manager.devices)
    }

@app.get("/api/devices")
async def list_devices():
    """Get list of all devices"""
    return {
        "success": True,
        "devices": ws_manager.get_devices()
    }

@app.post("/api/command")
async def execute_command(request: CommandRequest):
    """Execute shell command on device"""
    if not ws_manager.authenticated:
        raise HTTPException(status_code=503, detail="Not connected to MeshCentral")

    result = ws_manager.execute_command(request.node_id, request.command)

    if result:
        return {
            "success": True,
            "output": result.get('value', ''),
            "response": result
        }
    else:
        return {
            "success": False,
            "error": "Command timeout or failed"
        }

@app.post("/api/command/multi")
async def execute_multi_command(request: MultiCommandRequest):
    """Execute same command on multiple devices"""
    if not ws_manager.authenticated:
        raise HTTPException(status_code=503, detail="Not connected to MeshCentral")

    results = {}
    for node_id in request.node_ids:
        result = ws_manager.execute_command(node_id, request.command)
        if result:
            results[node_id] = {
                "success": True,
                "output": result.get('value', ''),
                "response": result
            }
        else:
            results[node_id] = {
                "success": False,
                "error": "Command timeout or failed"
            }

    return {
        "success": True,
        "command": request.command,
        "total_devices": len(request.node_ids),
        "results": results
    }

@app.post("/api/screenshot")
async def get_screenshot(request: ScreenshotRequest):
    """Capture screenshot from device"""
    if not ws_manager.authenticated:
        raise HTTPException(status_code=503, detail="Not connected to MeshCentral")

    screenshot_data = ws_manager.get_screenshot(request.node_id)

    if screenshot_data:
        from fastapi.responses import Response
        return Response(content=screenshot_data, media_type="image/png")
    else:
        raise HTTPException(status_code=500, detail="Screenshot capture failed")

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy" if ws_manager.authenticated else "degraded",
        "connected": ws_manager.connected,
        "authenticated": ws_manager.authenticated,
        "version": "3.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
