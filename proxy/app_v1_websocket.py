"""
DaisyChain HTTP Proxy Service
Provides REST API access to MeshCentral WebSocket interface
"""

from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import websocket
import json
import base64
import os
import threading
import queue
import logging
from typing import Optional, Dict
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DaisyChain Proxy API",
    description="HTTP REST API for MeshCentral device control",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration from environment
DAISYCHAIN_URL = os.getenv('DAISYCHAIN_URL', 'tee.up.railway.app')
DAISYCHAIN_TOKEN = os.getenv('DAISYCHAIN_TOKEN')
PROXY_API_KEY = os.getenv('PROXY_API_KEY', 'change-me-in-production')

class MeshCentralConnection:
    """Manages persistent WebSocket connection to MeshCentral"""

    def __init__(self, url: str, token: str):
        self.url = url
        self.token = token
        self.ws = None
        self.connected = False
        self.response_queue = queue.Queue()
        self.pending_requests: Dict[str, queue.Queue] = {}
        self.lock = threading.Lock()

    def connect(self):
        """Establish WebSocket connection and authenticate"""
        try:
            self.ws = websocket.create_connection(
                f'wss://{self.url}/control.ashx',
                timeout=10
            )

            # Authenticate
            auth_msg = {
                'action': 'authToken',
                'token': self.token
            }
            self.ws.send(json.dumps(auth_msg))

            # Wait for auth response
            response = json.loads(self.ws.recv())

            if response.get('result') == 'ok':
                self.connected = True
                logger.info("Connected to MeshCentral successfully")

                # Start listener thread
                threading.Thread(target=self._listen, daemon=True).start()
                return True
            else:
                logger.error(f"Authentication failed: {response}")
                return False

        except Exception as e:
            logger.error(f"Connection failed: {e}")
            self.connected = False
            return False

    def _listen(self):
        """Listen for responses from MeshCentral"""
        while self.connected:
            try:
                msg = self.ws.recv()
                data = json.loads(msg)

                # Route response to appropriate queue
                request_id = data.get('tag')
                if request_id and request_id in self.pending_requests:
                    self.pending_requests[request_id].put(data)
                else:
                    # General response queue
                    self.response_queue.put(data)

            except websocket.WebSocketConnectionClosedException:
                logger.warning("WebSocket connection closed")
                self.connected = False
                break
            except Exception as e:
                logger.error(f"Error in listener: {e}")
                break

    def send_command(self, device_id: str, command: str, timeout: int = 30) -> dict:
        """Send shell command to device"""
        if not self.connected:
            raise Exception("Not connected to MeshCentral")

        request_id = f"cmd_{int(time.time() * 1000)}"
        response_queue = queue.Queue()

        with self.lock:
            self.pending_requests[request_id] = response_queue

        try:
            msg = {
                'action': 'msg',
                'nodeid': device_id,
                'type': 'runcommands',
                'cmds': command,
                'tag': request_id
            }
            self.ws.send(json.dumps(msg))

            # Wait for response
            response = response_queue.get(timeout=timeout)
            return response

        except queue.Empty:
            raise TimeoutError(f"No response from device after {timeout}s")
        finally:
            with self.lock:
                self.pending_requests.pop(request_id, None)

    def get_screenshot(self, device_id: str, timeout: int = 30) -> Optional[bytes]:
        """Get screenshot from device"""
        if not self.connected:
            raise Exception("Not connected to MeshCentral")

        request_id = f"screenshot_{int(time.time() * 1000)}"
        response_queue = queue.Queue()

        with self.lock:
            self.pending_requests[request_id] = response_queue

        try:
            msg = {
                'action': 'msg',
                'nodeid': device_id,
                'type': 'screenshot',
                'tag': request_id
            }
            self.ws.send(json.dumps(msg))

            response = response_queue.get(timeout=timeout)

            if 'data' in response:
                return base64.b64decode(response['data'])
            return None

        except queue.Empty:
            raise TimeoutError(f"No response from device after {timeout}s")
        finally:
            with self.lock:
                self.pending_requests.pop(request_id, None)

    def list_devices(self, timeout: int = 10) -> dict:
        """Get list of all devices"""
        if not self.connected:
            raise Exception("Not connected to MeshCentral")

        msg = {'action': 'nodes'}
        self.ws.send(json.dumps(msg))

        try:
            response = self.response_queue.get(timeout=timeout)
            return response
        except queue.Empty:
            raise TimeoutError("No response from server")

# Global connection instance
meshcentral = MeshCentralConnection(DAISYCHAIN_URL, DAISYCHAIN_TOKEN)

@app.on_event("startup")
async def startup():
    """Connect to MeshCentral on startup"""
    logger.info("Starting DaisyChain Proxy...")

    if not DAISYCHAIN_TOKEN:
        logger.error("DAISYCHAIN_TOKEN not set!")
        return

    success = meshcentral.connect()
    if not success:
        logger.error("Failed to connect to MeshCentral")

# API Key authentication
def verify_api_key(x_api_key: str = Header(...)):
    """Verify API key from header"""
    if x_api_key != PROXY_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key

# Request/Response Models
class CommandRequest(BaseModel):
    device_id: str
    command: str
    timeout: int = 30

class ScreenshotRequest(BaseModel):
    device_id: str
    timeout: int = 30

# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "DaisyChain Proxy API",
        "status": "running",
        "connected": meshcentral.connected,
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy" if meshcentral.connected else "unhealthy",
        "meshcentral_connected": meshcentral.connected,
        "meshcentral_url": DAISYCHAIN_URL
    }

@app.post("/api/command")
async def send_command(
    req: CommandRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Send shell command to device

    Returns command output and execution result
    """
    try:
        result = meshcentral.send_command(
            req.device_id,
            req.command,
            req.timeout
        )
        return {
            "success": True,
            "device_id": req.device_id,
            "command": req.command,
            "result": result
        }
    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))
    except Exception as e:
        logger.error(f"Command execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/screenshot")
async def get_screenshot(
    req: ScreenshotRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Get screenshot from device

    Returns base64-encoded PNG image
    """
    try:
        screenshot = meshcentral.get_screenshot(req.device_id, req.timeout)

        if screenshot:
            return {
                "success": True,
                "device_id": req.device_id,
                "screenshot": base64.b64encode(screenshot).decode(),
                "format": "png"
            }
        else:
            raise HTTPException(status_code=404, detail="No screenshot received")

    except TimeoutError as e:
        raise HTTPException(status_code=504, detail=str(e))
    except Exception as e:
        logger.error(f"Screenshot failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/devices")
async def list_devices(api_key: str = Depends(verify_api_key)):
    """
    List all connected devices

    Returns list of devices with their IDs and status
    """
    try:
        devices = meshcentral.list_devices()
        return {
            "success": True,
            "devices": devices
        }
    except Exception as e:
        logger.error(f"Failed to list devices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/info")
async def get_info(api_key: str = Depends(verify_api_key)):
    """Get proxy configuration info"""
    return {
        "daisychain_url": DAISYCHAIN_URL,
        "connected": meshcentral.connected,
        "api_version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
