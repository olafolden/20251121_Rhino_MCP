"""
Rhino HTTP Server for MCP Integration
Receives geometry commands via HTTP and creates geometry in active document

INSTRUCTIONS FOR USE:
1. Open Rhino 8
2. Type 'EditPythonScript' in command line
3. Copy this entire file into the Python editor
4. Save it as 'rhino_http_server.py' (File → Save As)
5. Click Run button (play icon)
6. You should see: "✅ Server is running! Waiting for commands..."

To stop: Press Esc key multiple times

Author: Olaf Olden
Date: 2025-11-22
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
