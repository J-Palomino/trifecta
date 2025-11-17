"""
DaisyChain HTTP Proxy Service v2
Hybrid approach: REST API + WebSocket for MeshCentral device control
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import websocket
import json
import base64
import os
import threading
import queue
import logging
from typing import Optional, Dict, List
import time
from urllib.parse import urljoin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DaisyChain Proxy API v2",
    description="Hybrid REST+WebSocket API for MeshCentral device control",
    version="2.0.1"
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
MESHCENTRAL_URL = os.getenv('DAISYCHAIN_URL', 'tee.up.railway.app')
MESHCENTRAL_TOKEN = os.getenv('DAISYCHAIN_TOKEN')
PROXY_API_KEY = os.getenv('PROXY_API_KEY', 'change-me-in-production')

# Ensure URL has protocol
if not MESHCENTRAL_URL.startswith('http'):
    MESHCENTRAL_BASE = f'https://{MESHCENTRAL_URL}'
else:
    MESHCENTRAL_BASE = MESHCENTRAL_URL

class MeshCentralClient:
    """
    Hybrid MeshCentral client using REST API with cookie authentication
    and WebSocket for real-time features
    """

    def __init__(self, base_url: str, login_token: str):
        self.base_url = base_url.rstrip('/')
        self.login_token = login_token
        self.session = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            verify=True
        )
        self.cookies = {}
        self.authenticated = False

    async def authenticate(self):
        """Authenticate using login token and get session cookie"""
        try:
            # MeshCentral login token authentication
            url = f"{self.base_url}/logintoken"

            response = await self.session.post(
                url,
                data={'loginToken': self.login_token},
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )

            if response.status_code == 200:
                # Store cookies for subsequent requests
                self.cookies = dict(response.cookies)
                self.authenticated = True
                logger.info("Successfully authenticated with MeshCentral")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False

    async def get_nodes(self) -> Dict:
        """Get list of all nodes/devices"""
        if not self.authenticated:
            await self.authenticate()

        try:
            # MeshCentral uses /meshes endpoint to get device groups
            # Then /nodes to get devices
            url = f"{self.base_url}/meshes.ashx"

            response = await self.session.get(
                url,
                cookies=self.cookies
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get nodes: {response.status_code}")
                return {"error": "Failed to retrieve nodes"}

        except Exception as e:
            logger.error(f"Error getting nodes: {e}")
            return {"error": str(e)}

    async def execute_command(self, node_id: str, command: str) -> Dict:
        """
        Execute command on device using MeshCentral's messenger protocol
        This requires WebSocket connection for interactive commands
        """
        # For now, return info that this needs WebSocket implementation
        return {
            "status": "pending_websocket_implementation",
            "message": "Command execution requires WebSocket connection",
            "node_id": node_id,
            "command": command
        }

    async def get_screenshot(self, node_id: str) -> Optional[bytes]:
        """Get screenshot from device"""
        # Screenshot also requires WebSocket for most MeshCentral setups
        return None

    async def close(self):
        """Close the HTTP session"""
        await self.session.aclose()


# Global client instance
mesh_client = MeshCentralClient(MESHCENTRAL_BASE, MESHCENTRAL_TOKEN)

@app.on_event("startup")
async def startup():
    """Authenticate on startup"""
    logger.info("=" * 60)
    logger.info(f"DaisyChain Proxy v2.0.1 (REST API + WebSocket Hybrid)")
    logger.info(f"MeshCentral URL: {MESHCENTRAL_BASE}")
    logger.info("=" * 60)

    if not MESHCENTRAL_TOKEN:
        logger.error("DAISYCHAIN_TOKEN not set!")
        return

    success = await mesh_client.authenticate()
    if not success:
        logger.error("Failed to authenticate with MeshCentral")
    else:
        logger.info("Proxy ready and authenticated")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    await mesh_client.close()

# API Key authentication
def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
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
        "service": "DaisyChain Proxy API v2",
        "status": "running",
        "authenticated": mesh_client.authenticated,
        "version": "2.0.1",
        "approach": "Hybrid REST+WebSocket"
    }

@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy" if mesh_client.authenticated else "unhealthy",
        "meshcentral_url": MESHCENTRAL_BASE,
        "authenticated": mesh_client.authenticated,
        "api_version": "2.0.1"
    }

@app.get("/api/devices", dependencies=[Depends(verify_api_key)])
async def list_devices():
    """
    List all connected devices

    Returns list of devices with their IDs and status
    """
    try:
        devices = await mesh_client.get_nodes()
        return {
            "success": True,
            "devices": devices
        }
    except Exception as e:
        logger.error(f"Failed to list devices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/command", dependencies=[Depends(verify_api_key)])
async def send_command(req: CommandRequest):
    """
    Send shell command to device

    Note: This version uses REST API where possible,
    WebSocket implementation coming for interactive commands
    """
    try:
        result = await mesh_client.execute_command(
            req.device_id,
            req.command
        )
        return {
            "success": True,
            "device_id": req.device_id,
            "command": req.command,
            "result": result
        }
    except Exception as e:
        logger.error(f"Command execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/screenshot", dependencies=[Depends(verify_api_key)])
async def get_screenshot(req: ScreenshotRequest):
    """
    Get screenshot from device

    Note: Screenshot requires WebSocket in most MeshCentral setups
    """
    try:
        screenshot = await mesh_client.get_screenshot(req.device_id)

        if screenshot:
            return {
                "success": True,
                "device_id": req.device_id,
                "screenshot": base64.b64encode(screenshot).decode(),
                "format": "png"
            }
        else:
            return {
                "success": False,
                "message": "Screenshot feature requires WebSocket implementation",
                "device_id": req.device_id
            }

    except Exception as e:
        logger.error(f"Screenshot failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/info", dependencies=[Depends(verify_api_key)])
async def get_info():
    """Get proxy configuration info"""
    return {
        "meshcentral_url": MESHCENTRAL_BASE,
        "authenticated": mesh_client.authenticated,
        "api_version": "2.0.0",
        "features": {
            "device_listing": "REST API",
            "commands": "Pending WebSocket",
            "screenshots": "Pending WebSocket"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
