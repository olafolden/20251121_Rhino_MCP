# MCP Server for Active Rhino Instance (HTTP Approach)

**Goal**: Create geometry in your active Rhino window using Claude via MCP
**Method**: HTTP server running inside Rhino
**Time**: 45-60 minutes
**Experience Level**: Familiar with Rhino Python

---

## Table of Contents

1. [Understanding the Architecture](#understanding-the-architecture)
2. [Prerequisites](#prerequisites)
3. [Phase 1: Test Rhino's HTTP Capability](#phase-1-test-rhinos-http-capability)
4. [Phase 2: Build the Rhino HTTP Server](#phase-2-build-the-rhino-http-server)
5. [Phase 3: Create the MCP Server](#phase-3-create-the-mcp-server)
6. [Phase 4: Configure Claude Desktop](#phase-4-configure-claude-desktop)
7. [Phase 5: Test Everything](#phase-5-test-everything)
8. [Troubleshooting](#troubleshooting)
9. [Understanding What You Built](#understanding-what-you-built)
10. [Next Steps](#next-steps)

---

## Understanding the Architecture

### The Big Picture

You want Claude to create geometry in your **active Rhino window** - the one you can see and interact with. Here's how we'll make that happen:

```
┌─────────┐         ┌─────────────┐         ┌──────────────────┐
│  Claude │ ──────→ │ MCP Server  │ ──────→ │  Rhino (Active)  │
│ Desktop │         │  (Python)   │  HTTP   │  + HTTP Server   │
└─────────┘         └─────────────┘         └──────────────────┘
                                                      │
                                                      ↓
                                                 Your Document
                                                  (Geometry!)
```

**Key Insight**: Unlike Rhino Compute (which is headless), we're running a web server **inside** your active Rhino instance. This lets us directly add geometry to the document you're looking at.

### How It Works

1. **Rhino Side**: You run a Python script in Rhino that starts a mini web server
2. **The Server**: Listens on `localhost:8080` for commands
3. **MCP Side**: Your MCP server sends HTTP requests with commands like "create_box"
4. **Result**: Rhino receives the command and creates geometry in your active document

### Why HTTP?

- **Real-time**: Instant communication (no file polling delays)
- **Standard**: Uses familiar web protocols
- **Bidirectional**: Can send responses back to confirm success
- **Debuggable**: Easy to test with a web browser

---

## Prerequisites

### System Requirements

- ✅ Windows with Rhino 8 installed
- ✅ WSL2 installed and configured
- ✅ Python 3.10+ in WSL2
- ✅ Rhino Python experience (you've run scripts before)

### Knowledge Check

Before starting, make sure you understand:
- [ ] How to open Rhino's Python editor (`EditPythonScript` command)
- [ ] How to run a script in Rhino
- [ ] Basic HTTP concepts (GET/POST requests)

**New to HTTP?** That's okay! Think of it like sending a letter:
- **GET**: "Can I have the information at this address?"
- **POST**: "Here's some data I'm sending you"

---

## Phase 1: Test Rhino's HTTP Capability

**Goal**: Verify that Rhino can run a web server and create geometry in response to HTTP requests.

**Time**: 10 minutes

### 1.1 Open Rhino and Python Editor

1. **Launch Rhino 8**
2. **Open Python editor**: Type `EditPythonScript` in command line, press Enter
3. **Create new script**: File → New

### 1.2 Copy the Test Script

Paste this into the Python editor:

```python
"""
Simple HTTP Server Test for Rhino
Creates a point when you visit localhost:8080
"""

import rhinoscriptsyntax as rs
import BaseHTTPServer
import json

class SimpleHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """
    Handles incoming HTTP requests
    """
    
    def do_GET(self):
        """Handle GET requests (like visiting in a browser)"""
        print("Received GET request!")
        
        # Create a point at origin
        point_id = rs.AddPoint([0, 0, 0])
        
        # Send response back to browser
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write("Point created at origin!")
        
        print("Point created with ID: " + str(point_id))
    
    def log_message(self, format, *args):
        """Override to customize logging"""
        print("HTTP: " + format % args)

# Start the server
print("=" * 50)
print("Starting HTTP server on localhost:8080")
print("Open your browser and go to: http://localhost:8080")
print("Press Ctrl+C in Rhino to stop the server")
print("=" * 50)

try:
    server = BaseHTTPServer.HTTPServer(('localhost', 8080), SimpleHandler)
    server.serve_forever()
except KeyboardInterrupt:
    print("\nServer stopped.")
```

### 1.3 Run the Test

**In Rhino**:
1. Click the "Run" button (▶) in the Python editor
2. Look at Rhino's command line - you should see:
   ```
   Starting HTTP server on localhost:8080
   Open your browser and go to: http://localhost:8080
   ```

**In Your Browser**:
1. Open any web browser
2. Navigate to: `http://localhost:8080`

### 1.4 What Should Happen

✅ **Expected Results**:
- Browser shows: "Point created at origin!"
- A point appears at (0,0,0) in your Rhino viewport
- Rhino's command line shows: "Received GET request!" and "Point created with ID: ..."

❌ **If It Doesn't Work**:
- Check if you see any error messages in Rhino's command line
- Make sure port 8080 isn't already in use
- Try closing and reopening Rhino

### 1.5 Stop the Server

**In Rhino**: 
- Press `Esc` key several times, or
- Close the Python editor window

The script will stop and the server will shut down.

---

## Checkpoint: Understanding What Just Happened

**Before moving forward, let's make sure you understand this test:**

**Question 1**: When you visited `http://localhost:8080` in your browser, what was the browser doing?
<details>
<summary>Click to check your understanding</summary>
The browser sent an HTTP GET request to the server running inside Rhino. Think of it like knocking on a door and asking "Hey, are you there?"
</details>

**Question 2**: Why did the point appear in Rhino and not somewhere else?
<details>
<summary>Click to check your understanding</summary>
Because the server is running **inside** the Rhino process. When the handler calls `rs.AddPoint()`, it's calling Rhino's API directly in the active document.
</details>

**Question 3**: What would happen if you refreshed the browser page?
<details>
<summary>Try it!</summary>
Another point would be created at the same location. Each HTTP request triggers the `do_GET()` function again.
</details>

---

## Phase 2: Build the Rhino HTTP Server

**Goal**: Create a production-ready HTTP server in Rhino that can handle multiple geometry commands.

**Time**: 15 minutes

### 2.1 Understanding the Full Server

Now we'll build a server that can:
- ✅ Handle POST requests (for sending data)
- ✅ Parse JSON commands
- ✅ Create boxes (not just points)
- ✅ Send proper responses back
- ✅ Handle errors gracefully

### 2.2 Create the Full Server Script

**In Rhino**: Create a new Python script (File → New)

**Save it as**: `rhino_http_server.py` (so you can reuse it)

```python
"""
Rhino HTTP Server for MCP Integration
Receives geometry commands via HTTP and creates geometry in active document

Author: Your Name
Date: 2024
"""

import rhinoscriptsyntax as rs
import Rhino
import BaseHTTPServer
import json
import traceback


class RhinoGeometryHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """
    Handles HTTP requests and translates them to Rhino geometry commands
    """
    
    def do_POST(self):
        """
        Handle POST requests containing JSON commands
        
        Expected JSON format:
        {
            "action": "create_box",
            "params": {
                "x": 0,
                "y": 0,
                "z": 0,
                "width": 10,
                "height": 10,
                "depth": 10
            }
        }
        """
        try:
            # Read the request body
            content_length = int(self.headers.getheader('content-length', 0))
            body = self.rfile.read(content_length)
            
            # Parse JSON
            command = json.loads(body)
            print("\n" + "=" * 50)
            print("Received command: " + str(command))
            
            # Route to appropriate handler
            action = command.get('action', '')
            params = command.get('params', {})
            
            if action == 'create_box':
                result = self.create_box(params)
            elif action == 'create_sphere':
                result = self.create_sphere(params)
            elif action == 'ping':
                result = {'status': 'ok', 'message': 'Rhino server is running!'}
            else:
                result = {'status': 'error', 'message': 'Unknown action: ' + action}
            
            # Send response
            self.send_json_response(result)
            print("Response sent: " + str(result))
            print("=" * 50)
            
        except Exception as e:
            error_msg = "Error processing request: " + str(e)
            print("ERROR: " + error_msg)
            print(traceback.format_exc())
            self.send_json_response({
                'status': 'error',
                'message': error_msg
            }, status_code=500)
    
    def create_box(self, params):
        """
        Create a box in the active Rhino document
        
        Args:
            params (dict): Dictionary with x, y, z, width, height, depth
        
        Returns:
            dict: Result with status and message
        """
        try:
            # Extract parameters with defaults
            x = params.get('x', 0.0)
            y = params.get('y', 0.0)
            z = params.get('z', 0.0)
            width = params.get('width', 10.0)
            height = params.get('height', 10.0)
            depth = params.get('depth', 10.0)
            
            # Create base plane at specified location
            base_point = Rhino.Geometry.Point3d(x, y, z)
            plane = Rhino.Geometry.Plane(base_point, Rhino.Geometry.Vector3d.ZAxis)
            
            # Create interval for each dimension
            x_interval = Rhino.Geometry.Interval(0, width)
            y_interval = Rhino.Geometry.Interval(0, height)
            z_interval = Rhino.Geometry.Interval(0, depth)
            
            # Create the box
            box = Rhino.Geometry.Box(plane, x_interval, y_interval, z_interval)
            
            # Add to document
            box_id = rs.coercebrep(rs.AddBox(box.GetCorners()))
            
            # Redraw viewport to show new geometry
            rs.Redraw()
            
            return {
                'status': 'success',
                'message': 'Box created successfully',
                'geometry_id': str(box_id),
                'position': [x, y, z],
                'dimensions': [width, height, depth]
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': 'Failed to create box: ' + str(e)
            }
    
    def create_sphere(self, params):
        """
        Create a sphere in the active Rhino document
        
        Args:
            params (dict): Dictionary with x, y, z, radius
        
        Returns:
            dict: Result with status and message
        """
        try:
            x = params.get('x', 0.0)
            y = params.get('y', 0.0)
            z = params.get('z', 0.0)
            radius = params.get('radius', 5.0)
            
            # Create sphere
            center = [x, y, z]
            sphere_id = rs.AddSphere(center, radius)
            
            # Redraw viewport
            rs.Redraw()
            
            return {
                'status': 'success',
                'message': 'Sphere created successfully',
                'geometry_id': str(sphere_id),
                'center': center,
                'radius': radius
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': 'Failed to create sphere: ' + str(e)
            }
    
    def send_json_response(self, data, status_code=200):
        """Send JSON response back to client"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')  # For CORS
        self.end_headers()
        self.wfile.write(json.dumps(data))
    
    def log_message(self, format, *args):
        """Custom logging to Rhino console"""
        print("HTTP: " + format % args)


def start_server(port=8080):
    """
    Start the HTTP server
    
    Args:
        port (int): Port number to listen on
    """
    print("\n" + "=" * 70)
    print("  RHINO HTTP SERVER FOR MCP")
    print("=" * 70)
    print("Status: Starting server...")
    print("Listening on: http://localhost:" + str(port))
    print("\nAvailable commands:")
    print("  - create_box: Creates a box with specified dimensions")
    print("  - create_sphere: Creates a sphere with specified radius")
    print("  - ping: Check if server is running")
    print("\nTo stop: Press Esc multiple times or close this window")
    print("=" * 70 + "\n")
    
    try:
        server = BaseHTTPServer.HTTPServer(('localhost', port), RhinoGeometryHandler)
        print("✅ Server is running! Waiting for commands...\n")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("Server stopped by user")
        print("=" * 70)
    except Exception as e:
        print("\n❌ ERROR: " + str(e))
        print(traceback.format_exc())


# Run the server when script is executed
if __name__ == "__main__":
    start_server(port=8080)
```

### 2.3 Test the New Server

**Step 1**: Run the script in Rhino
- You should see the welcome message with available commands

**Step 2**: Test with curl from WSL2

Open WSL2 terminal and test:

```bash
# Test ping
curl -X POST http://$(hostname).local:8080 \
  -H "Content-Type: application/json" \
  -d '{"action": "ping"}'

# Test create_box
curl -X POST http://$(hostname).local:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "action": "create_box",
    "params": {
      "x": 10,
      "y": 10,
      "z": 0,
      "width": 20,
      "height": 15,
      "depth": 10
    }
  }'
```

**Expected Results**:
- Ping should return: `{"status": "ok", "message": "Rhino server is running!"}`
- create_box should create a box in Rhino AND return JSON with geometry_id

---

## Checkpoint: Understanding the Server Architecture

**Question 1**: Why do we use POST instead of GET for creating geometry?
<details>
<summary>Think about it, then click</summary>
POST is for sending data to the server. We need to send parameters (x, y, z, dimensions). GET is typically for retrieving information, not for actions that change state.
</details>

**Question 2**: What does `rs.Redraw()` do and why is it important?
<details>
<summary>Click to check</summary>
`rs.Redraw()` refreshes the Rhino viewport so you can immediately see the newly created geometry. Without it, you might have to manually refresh the view.
</details>

**Question 3**: What happens if you send an invalid action name?
<details>
<summary>Try it!</summary>
The server returns an error message: `{"status": "error", "message": "Unknown action: ..."}`. This is graceful error handling - the server doesn't crash, it tells you what went wrong.
</details>

---

## Phase 3: Create the MCP Server

**Goal**: Build a Python MCP server in WSL2 that talks to your Rhino HTTP server.

**Time**: 10 minutes

### 3.1 Setup WSL2 Environment

```bash
# Create project directory
mkdir -p ~/rhino-mcp-http
cd ~/rhino-mcp-http

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install mcp fastmcp requests
```

### 3.2 Create the MCP Server Script

Create file: `rhino_mcp_server.py`

```python
"""
MCP Server for Rhino HTTP Integration
Connects Claude to an active Rhino instance via HTTP

This MCP server sends commands to a Rhino HTTP server running
inside an active Rhino application window.
"""

import requests
from fastmcp import FastMCP
import json

# Initialize MCP server
mcp = FastMCP(name="Rhino Active Instance")

# Rhino HTTP server endpoint (WSL2 to Windows)
# Note: $(hostname).local resolves to Windows host from WSL2
RHINO_URL = "http://$(hostname).local:8080"


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
```

### 3.3 Test MCP Server Manually

Before connecting to Claude, test that the MCP server can reach Rhino:

```bash
# Make sure you're in the virtual environment
cd ~/rhino-mcp-http
source venv/bin/activate

# Start the MCP server (it will wait for input)
python rhino_mcp_server.py
```

The server should start and wait for MCP protocol messages. You can stop it with `Ctrl+C`.

---

## Phase 4: Configure Claude Desktop

**Goal**: Connect Claude Desktop to your MCP server

**Time**: 5 minutes

### 4.1 Locate Claude Config File

**On Windows**, navigate to:
```
C:\Users\YourUsername\AppData\Roaming\Claude\claude_desktop_config.json
```

### 4.2 Edit Configuration

Open the file in Notepad and add this configuration:

```json
{
  "mcpServers": {
    "rhino-active": {
      "command": "wsl",
      "args": [
        "-e",
        "bash",
        "-c",
        "cd ~/rhino-mcp-http && source venv/bin/activate && python rhino_mcp_server.py"
      ]
    }
  }
}
```

**Important**: If you already have other MCP servers configured, just add the `"rhino-active"` block inside the existing `"mcpServers"` object.

### 4.3 Restart Claude Desktop

1. **Close** Claude Desktop completely (check system tray)
2. **Reopen** Claude Desktop
3. **Look for** the 🔨 icon indicating MCP tools are loaded

---

## Phase 5: Test Everything

**Goal**: Create geometry in Rhino using Claude!

**Time**: 5 minutes

### 5.1 Start Rhino HTTP Server

**In Rhino**:
1. Open the `rhino_http_server.py` script
2. Click Run
3. Verify you see: "✅ Server is running! Waiting for commands..."

### 5.2 Test in Claude Desktop

**Test 1 - Check Connection**:
```
Can you ping Rhino to see if it's running?
```

Expected: ✅ Rhino is running and ready!

**Test 2 - Create a Box**:
```
Create a box at position (10, 10, 0) with dimensions 20 × 15 × 10
```

Expected: Box appears in your Rhino viewport!

**Test 3 - Create a Sphere**:
```
Create a sphere at (30, 0, 0) with radius 8
```

Expected: Sphere appears in Rhino!

**Test 4 - Complex Request**:
```
Create three boxes in a row: 
- First at (0, 0, 0), size 10×10×10
- Second at (15, 0, 0), size 10×10×10  
- Third at (30, 0, 0), size 10×10×10
```

Expected: Three boxes appear in Rhino!

---

## Troubleshooting

### ❌ "Cannot connect to Rhino"

**Checklist**:
1. Is Rhino running?
2. Is the Python script running in Rhino? (Check for server startup message)
3. Can you access `http://localhost:8080` from Windows browser?

**Test from WSL2**:
```bash
# This should work if networking is configured correctly
curl http://$(hostname).local:8080
```

**If curl fails**:
```bash
# Try finding Windows host IP
ip route | grep default

# Then test with that IP
curl http://<WINDOWS_IP>:8080
```

**Fix**: Update `RHINO_URL` in `rhino_mcp_server.py` with the correct IP address.

---

### ❌ MCP Tools Not Showing in Claude

**Checklist**:
1. Is `claude_desktop_config.json` saved?
2. Is the JSON valid? (Use https://jsonlint.com to validate)
3. Did you restart Claude Desktop?

**Debug**:
```bash
# Test MCP server manually
cd ~/rhino-mcp-http
source venv/bin/activate
python rhino_mcp_server.py
# Should start without errors
```

---

### ❌ Geometry Not Appearing in Rhino

**Checklist**:
1. Is the Rhino HTTP server script still running?
2. Are you looking at the correct viewport?
3. Try typing `ZoomExtents` in Rhino to see all geometry

**Debug**:
- Check Rhino's command line for error messages
- Look at the server output in the Python editor window

---

### ❌ "Port 8080 already in use"

**Fix**:
1. Close any other programs using port 8080
2. Or change the port:
   - In `rhino_http_server.py`: Change `start_server(port=8080)` to `start_server(port=8081)`
   - In `rhino_mcp_server.py`: Change `RHINO_URL` to use port 8081

---

## Understanding What You Built

### Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                         WINDOWS                               │
│                                                               │
│  ┌─────────────────┐                                         │
│  │  Claude Desktop │                                         │
│  │                 │                                         │
│  │  [MCP Client]   │                                         │
│  └────────┬────────┘                                         │
│           │                                                   │
│           │ stdio (via WSL)                                  │
│           ↓                                                   │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                    WSL2                              │    │
│  │                                                      │    │
│  │  ┌────────────────────────────────────┐            │    │
│  │  │  MCP Server (Python)                │            │    │
│  │  │  - Receives tool calls from Claude  │            │    │
│  │  │  - Translates to HTTP requests      │            │    │
│  │  └──────────────┬─────────────────────┘            │    │
│  │                 │                                    │    │
│  └─────────────────┼────────────────────────────────────┘    │
│                    │                                         │
│                    │ HTTP (localhost:8080)                   │
│                    ↓                                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Rhino 8 (Active Window)                             │   │
│  │                                                       │   │
│  │  ┌──────────────────────────────────────┐            │   │
│  │  │  HTTP Server (Python Script)         │            │   │
│  │  │  - Receives JSON commands            │            │   │
│  │  │  - Calls rhinoscriptsyntax           │            │   │
│  │  └──────────────┬───────────────────────┘            │   │
│  │                 │                                     │   │
│  │                 ↓                                     │   │
│  │  ┌──────────────────────────────────────┐            │   │
│  │  │  Active Document                      │            │   │
│  │  │  [Your geometry appears here! 📦]    │            │   │
│  │  └──────────────────────────────────────┘            │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

### Key Concepts

**1. HTTP Server in Rhino**
- Runs in the **same process** as Rhino
- Has direct access to `rhinoscriptsyntax` API
- Can modify the active document immediately

**2. MCP Protocol**
- Standard way for Claude to call external tools
- Uses stdio (standard input/output) for communication
- Tools are just decorated Python functions

**3. Cross-Process Communication**
- WSL2 → Windows via network (HTTP)
- Rhino's Python → Rhino API via direct function calls
- Claude → MCP via stdio

**4. Why This Works**
- The HTTP server is **inside** Rhino's process space
- When it calls `rs.AddBox()`, it's calling the **real** Rhino API
- Changes happen in the **actual document** you're looking at

---

## Next Steps

### 1. Add More Geometry Tools

Extend the Rhino HTTP server with new geometry types:

```python
def create_cylinder(self, params):
    """Create a cylinder"""
    base = params.get('base', [0, 0, 0])
    height = params.get('height', 10)
    radius = params.get('radius', 5)
    
    # Implementation here
    ...
```

Then add corresponding MCP tool:

```python
@mcp.tool()
def create_cylinder(x, y, z, radius, height):
    """Create a cylinder in Rhino"""
    ...
```

### 2. Add Object Manipulation

Not just creation - add tools to:
- Move objects
- Rotate objects
- Scale objects
- Delete objects
- Change properties (color, layer, etc.)

### 3. Add Query Tools

Get information from Rhino:
- List all objects in document
- Get object properties
- Calculate areas/volumes
- Get bounding boxes

### 4. Improve Error Handling

- Add validation for parameters
- Return more detailed error messages
- Add logging to file
- Handle Rhino document not ready

### 5. Add Authentication

For production use:
- Add API key requirement
- Implement request signing
- Add rate limiting

### 6. Auto-start Server

Make the server start automatically when Rhino opens:
- Use Rhino's startup scripts feature
- Or create a Rhino plugin

---

## Learning Resources

### Understanding HTTP Servers
- **Real Python**: [Building an HTTP Server](https://realpython.com/python-http-server/)
- **MDN Web Docs**: [HTTP Overview](https://developer.mozilla.org/en-US/docs/Web/HTTP)

### Rhino Python Scripting
- **Rhino Python Primer**: https://www.rhino3d.com/download/IronPython/5.0/RhinoPython101
- **RhinoScriptSyntax Documentation**: https://developer.rhino3d.com/api/RhinoScriptSyntax/

### MCP Protocol
- **Official Docs**: https://modelcontextprotocol.io/
- **FastMCP Guide**: https://gofastmcp.com/
- **Examples**: https://github.com/anthropics/mcp

---

## Frequently Asked Questions

### Q: Can I use this from multiple Claude conversations at once?

A: Yes! The HTTP server can handle multiple requests. However, all geometry goes to the **same** Rhino document.

### Q: What if I close Rhino?

A: The HTTP server stops. You'll need to restart the Python script when you reopen Rhino.

### Q: Can I run this on Mac?

A: Not directly. Rhino for Mac doesn't support the same Python scripting. You'd need to adapt the approach significantly.

### Q: Does this work with Grasshopper?

A: Not yet, but you could extend it! Add a handler that creates/modifies Grasshopper definitions.

### Q: Can Claude see what's already in my Rhino document?

A: Not with this basic setup. You'd need to add query tools that return information about existing geometry.

### Q: Is this approach secure?

A: For local development: yes. For production: no. The HTTP server has no authentication and accepts commands from localhost.

---

## Conclusion

Congratulations! You've built a complete system that lets Claude Desktop create geometry in your active Rhino window. 

**What you learned**:
- ✅ How to run an HTTP server inside Rhino
- ✅ How to create MCP tools in Python
- ✅ How to connect WSL2 to Windows applications
- ✅ How to handle JSON commands and responses
- ✅ How to integrate AI with CAD software

**The power of what you built**:
- Claude can now "draw" in Rhino for you
- You can describe geometry in natural language
- Complex sequences of commands become simple conversations
- The foundation is extensible to any Rhino API functionality

**Next challenge**: What will you build with this? Think about:
- Parametric design assistants
- Automated modeling workflows
- Natural language CAD commands
- AI-powered design iteration

---

**Happy building!** 🚀

*Remember: The best way to learn is to experiment. Try modifying the code, add new features, and see what breaks. That's how you develop deep understanding.*