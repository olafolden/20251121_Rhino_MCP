"""
Simple HTTP Server Test for Rhino
Creates a point when you visit localhost:8080

INSTRUCTIONS FOR USE:
1. Open Rhino 8
2. Type 'EditPythonScript' in command line
3. Copy this entire file into the Python editor
4. Click Run button (play icon)
5. Open browser and visit: http://localhost:8080
6. You should see a point appear at origin in Rhino!

To stop: Press Esc key multiple times
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
