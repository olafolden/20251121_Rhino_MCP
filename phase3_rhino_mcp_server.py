"""
MCP Server for Rhino HTTP Integration
Connects Claude to an active Rhino instance via HTTP

This MCP server sends commands to a Rhino HTTP server running
inside an active Rhino application window.

INSTRUCTIONS FOR USE:
1. Copy this file to: ~/rhino-mcp-http/rhino_mcp_server.py in WSL2
2. Make sure you have installed: pip install mcp fastmcp requests
3. Run: python rhino_mcp_server.py
4. The server will wait for MCP protocol messages from Claude

Author: Olaf Olden
Date: 2025-11-22
"""

import requests
from fastmcp import FastMCP
import json
import os

# Initialize MCP server
mcp = FastMCP(name="Rhino Active Instance")

# Rhino HTTP server endpoint (WSL2 to Windows)
# Note: This uses the Windows host machine from WSL2
def get_rhino_url():
    """Get the Rhino HTTP server URL, accounting for WSL2 networking"""
    # Try to get Windows host IP from WSL2
    try:
        import subprocess
        hostname = subprocess.check_output(['hostname']).decode().strip()
        return f"http://{hostname}.local:8080"
    except:
        # Fallback to common patterns
        return "http://localhost:8080"

RHINO_URL = get_rhino_url()


def call_rhino(action, params=None):
    """
    Send a command to the Rhino HTTP server

    Args:
        action (str): Action name (e.g., 'create_box')
        params (dict): Parameters for the action

    Returns:
        dict: Response from Rhino server
    """
    if params is None:
        params = {}

    payload = {
        "action": action,
        "params": params
    }

    try:
        response = requests.post(
            RHINO_URL,
            json=payload,
            timeout=10,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {
                "status": "error",
                "message": f"HTTP {response.status_code}: {response.text}"
            }

    except requests.exceptions.ConnectionError:
        return {
            "status": "error",
            "message": "Cannot connect to Rhino. Is the HTTP server running?"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }


@mcp.tool()
def ping_rhino() -> str:
    """
    Check if Rhino HTTP server is running and responsive.

    Returns:
        str: Status message
    """
    result = call_rhino("ping")

    if result.get("status") == "ok":
        return "✅ Rhino is running and ready!"
    else:
        return f"❌ Error: {result.get('message', 'Unknown error')}"


@mcp.tool()
def create_box(
    x: float = 0.0,
    y: float = 0.0,
    z: float = 0.0,
    width: float = 10.0,
    height: float = 10.0,
    depth: float = 10.0
) -> str:
    """
    Create a box in the active Rhino document.

    Args:
        x: X coordinate of base corner (default: 0)
        y: Y coordinate of base corner (default: 0)
        z: Z coordinate of base corner (default: 0)
        width: Width of box in X direction (default: 10)
        height: Height of box in Y direction (default: 10)
        depth: Depth of box in Z direction (default: 10)

    Returns:
        str: Confirmation message with geometry details
    """
    params = {
        "x": x,
        "y": y,
        "z": z,
        "width": width,
        "height": height,
        "depth": depth
    }

    result = call_rhino("create_box", params)

    if result.get("status") == "success":
        pos = result.get("position", [x, y, z])
        dims = result.get("dimensions", [width, height, depth])
        return (
            f"✅ Box created in Rhino!\n"
            f"Position: ({pos[0]}, {pos[1]}, {pos[2]})\n"
            f"Dimensions: {dims[0]} × {dims[1]} × {dims[2]}"
        )
    else:
        return f"❌ Error: {result.get('message', 'Unknown error')}"


@mcp.tool()
def create_sphere(
    x: float = 0.0,
    y: float = 0.0,
    z: float = 0.0,
    radius: float = 5.0
) -> str:
    """
    Create a sphere in the active Rhino document.

    Args:
        x: X coordinate of center (default: 0)
        y: Y coordinate of center (default: 0)
        z: Z coordinate of center (default: 0)
        radius: Radius of sphere (default: 5)

    Returns:
        str: Confirmation message with geometry details
    """
    params = {
        "x": x,
        "y": y,
        "z": z,
        "radius": radius
    }

    result = call_rhino("create_sphere", params)

    if result.get("status") == "success":
        center = result.get("center", [x, y, z])
        r = result.get("radius", radius)
        return (
            f"✅ Sphere created in Rhino!\n"
            f"Center: ({center[0]}, {center[1]}, {center[2]})\n"
            f"Radius: {r}"
        )
    else:
        return f"❌ Error: {result.get('message', 'Unknown error')}"


# Run the MCP server
if __name__ == "__main__":
    mcp.run()
