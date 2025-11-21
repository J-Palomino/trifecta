#!/usr/bin/env python3
"""
MeshCentral API Client with proper x-meshauth header authentication
Based on MeshCentral WebSocket authentication protocol
"""

import websocket
import json
import base64
import time
import sys
from typing import Dict, List, Optional

class MeshCentralAuthClient:
    """MeshCentral WebSocket client with x-meshauth header"""

    def __init__(self, url: str, username: str, password: str, token: str = ""):
        """Initialize client with credentials"""
        self.url = url if url.startswith('wss://') else f'wss://{url}/control.ashx'
        self.username = username
        self.password = password
        self.token = token  # 2FA token if enabled, empty otherwise
        self.ws = None
        self.authenticated = False
        self.devices = {}
        self.responses = []

    def _create_auth_header(self):
        """Create x-meshauth header with base64 encoded credentials"""
        # Base64 encode each component
        username_b64 = base64.b64encode(self.username.encode()).decode()
        password_b64 = base64.b64encode(self.password.encode()).decode()
        token_b64 = base64.b64encode(self.token.encode()).decode() if self.token else ""

        # Format: username,password,token
        if token_b64:
            return f"{username_b64},{password_b64},{token_b64}"
        else:
            return f"{username_b64},{password_b64}"

    def connect(self):
        """Connect to MeshCentral with authentication header"""
        print(f"Connecting to {self.url}...")

        # Create authentication header
        auth_header = self._create_auth_header()

        # Create WebSocket with custom header
        self.ws = websocket.WebSocketApp(
            self.url,
            header=[f"x-meshauth: {auth_header}"],
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=self._on_open
        )

        # Run in background
        import threading
        wst = threading.Thread(target=self.ws.run_forever)
        wst.daemon = True
        wst.start()

        # Wait for connection and authentication
        for i in range(100):  # Wait up to 10 seconds
            if self.authenticated:
                return True
            if i == 50:  # After 5 seconds, print status
                print("Still connecting...")
            time.sleep(0.1)

        return False

    def _on_open(self, ws):
        """Handle connection opened"""
        print("WebSocket connected")
        # With x-meshauth, we should already be authenticated
        # Request device list
        ws.send(json.dumps({'action': 'nodes'}))

    def _on_message(self, ws, message):
        """Handle incoming messages"""
        try:
            data = json.loads(message)
            action = data.get('action', 'unknown')

            print(f"[DEBUG] Received: {action}")

            # If we receive nodes, we're authenticated
            if action == 'nodes':
                if 'nodes' in data:
                    self.devices = data['nodes']
                    self.authenticated = True
                    print(f"Authenticated! Received {len(self.devices)} devices")
                    print(f"[DEBUG] Devices data type: {type(self.devices)}")
                    if self.devices:
                        first_key = list(self.devices.keys())[0]
                        print(f"[DEBUG] First device key: {first_key}")
                        print(f"[DEBUG] First device value type: {type(self.devices[first_key])}")
                        print(f"[DEBUG] First device value: {self.devices[first_key]}")

            elif action == 'close':
                cause = data.get('cause', 'unknown')
                msg = data.get('msg', '')
                print(f"ERROR: Connection closed - {cause}: {msg}")
                if cause == 'noauth':
                    print("\nAuthentication failed!")
                    print("Possible reasons:")
                    print("- Incorrect username or password")
                    print("- 2FA required but not provided")
                    print("- Account disabled")

            elif action == 'authcookie':
                # Server accepted authentication
                print("Authentication accepted")
                self.authenticated = True
                # Request devices
                ws.send(json.dumps({'action': 'nodes'}))

            elif action == 'runcommands':
                self.responses.append(data)

            elif action == 'event':
                # Device status updates
                event = data.get('event', {})
                if event.get('action') in ['addnode', 'changenode']:
                    node_id = event.get('nodeid')
                    if node_id:
                        self.devices[node_id] = event.get('node', {})

        except Exception as e:
            print(f"Message error: {e}")

    def _on_error(self, ws, error):
        """Handle errors"""
        print(f"WebSocket error: {error}")

    def _on_close(self, ws, close_status, close_msg):
        """Handle connection closed"""
        print(f"WebSocket closed: {close_status}")
        self.authenticated = False

    def list_devices(self) -> List[Dict]:
        """List all connected devices"""
        devices_list = []

        for mesh_id, devices_in_mesh in self.devices.items():
            # MeshCentral groups devices by mesh
            # devices_in_mesh can be a list of devices or a single device dict
            if isinstance(devices_in_mesh, list):
                # List of devices in this mesh
                for device in devices_in_mesh:
                    node_id = device.get('_id', 'Unknown')
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
                        'ip': ip,
                        'conn': conn
                    })
            elif isinstance(devices_in_mesh, dict):
                # Single device
                node_id = devices_in_mesh.get('_id', mesh_id)
                name = devices_in_mesh.get('name', 'Unknown')
                conn = devices_in_mesh.get('conn', 0)
                online = (conn & 1) != 0
                os_desc = devices_in_mesh.get('osdesc', 'Unknown OS')
                ip = devices_in_mesh.get('ip', 'N/A')

                devices_list.append({
                    'id': node_id,
                    'name': name,
                    'online': online,
                    'os': os_desc,
                    'ip': ip,
                    'conn': conn
                })

        return devices_list

    def send_command(self, node_id: str, command: str, timeout: int = 10) -> Optional[Dict]:
        """Send command to device and wait for response"""
        if not self.authenticated:
            print("ERROR: Not authenticated")
            return None

        # Clear previous responses
        self.responses = []

        # Send command
        msg = {
            'action': 'runcommands',
            'nodeids': [node_id],
            'type': 0,  # 0=shell, 1=cmd, 2=powershell
            'cmds': command,
            'runAsUser': 1
        }

        print(f"[DEBUG] Sending command: {command}")
        self.ws.send(json.dumps(msg))

        # Wait for response
        for _ in range(timeout * 10):
            if self.responses:
                return self.responses[0]
            time.sleep(0.1)

        return None

    def disconnect(self):
        """Close connection"""
        if self.ws:
            self.ws.close()


def main():
    """Main entry point"""

    # Configuration
    MESHCENTRAL_URL = "tee.up.railway.app"
    USERNAME = "~t:TZMNhwY5oV5o9DVy"
    PASSWORD = "42NJjOQa58FBvQ2c0rTY"
    TWO_FACTOR_TOKEN = ""  # Leave empty if not using 2FA

    print("=" * 60)
    print("MeshCentral API Client (x-meshauth Authentication)")
    print("=" * 60)
    print(f"URL: {MESHCENTRAL_URL}")
    print(f"Username: {USERNAME}")
    print()

    # Create client
    client = MeshCentralAuthClient(MESHCENTRAL_URL, USERNAME, PASSWORD, TWO_FACTOR_TOKEN)

    # Connect
    if not client.connect():
        print("Failed to connect to MeshCentral")
        print("\nTroubleshooting:")
        print("1. Verify MeshCentral is running at https://tee.up.railway.app")
        print("2. Check username and password are correct")
        print("3. If 2FA is enabled, provide the token")
        sys.exit(1)

    # Wait a moment for device list
    time.sleep(2)

    # List devices
    print("\n" + "=" * 60)
    print("Connected Devices")
    print("=" * 60)

    devices = client.list_devices()

    if not devices:
        print("No devices found")
        print("\nDevices will appear here once MeshAgent is installed on computers.")
    else:
        for i, device in enumerate(devices, 1):
            status = "ONLINE" if device['online'] else "OFFLINE"
            print(f"\n{i}. {device['name']}")
            print(f"   ID: {device['id']}")
            print(f"   Status: {status}")
            print(f"   OS: {device['os']}")
            print(f"   IP: {device['ip']}")

    # Interactive command mode
    if devices:
        print("\n" + "=" * 60)
        print("Send Command to Device")
        print("=" * 60)

        # Filter online devices
        online_devices = [d for d in devices if d['online']]

        if not online_devices:
            print("No online devices available")
        else:
            print("\nOnline devices:")
            for i, device in enumerate(online_devices, 1):
                print(f"{i}. {device['name']} ({device['id']})")

            try:
                choice = int(input("\nSelect device number (or 0 to exit): "))
                if choice > 0 and choice <= len(online_devices):
                    selected = online_devices[choice - 1]
                    command = input("Enter command to run: ")

                    print(f"\nSending command to {selected['name']}...")
                    result = client.send_command(selected['id'], command)

                    if result:
                        print("\nCommand Result:")
                        print("-" * 60)
                        print(json.dumps(result, indent=2))
                    else:
                        print("No response received (timeout)")
            except (ValueError, KeyboardInterrupt):
                print("\nExiting...")

    # Disconnect
    client.disconnect()
    print("\nDisconnected")


if __name__ == '__main__':
    main()
