"""
Simple HTTP Server Test for Rhino (FIXED - Non-Blocking Version)
Creates a point when you visit localhost:8080

PROBLEM FIXED: Original version froze Rhino's UI because the server blocked the main thread.
SOLUTION: Server now runs in a separate thread, keeping Rhino responsive!

INSTRUCTIONS FOR USE:
1. Open Rhino 8
2. Type 'EditPythonScript' in command line
3. Copy this entire file into the Python editor
4. Click Run button (play icon)
5. Open browser and visit: http://localhost:8080
6. You should see a point appear at origin in Rhino!
7. Rhino will stay responsive! You can rotate, zoom, etc.

To stop: Close the Python editor window
"""

import rhinoscriptsyntax as rs
import BaseHTTPServer
import threading
import time

# Global variable to control server
server_running = True

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


def run_server():
    """
    Run the HTTP server in a separate thread
    This keeps Rhino's UI responsive!
    """
    global server_running
    try:
        server = BaseHTTPServer.HTTPServer(('localhost', 8080), SimpleHandler)
        print("✅ Server thread started successfully!")

        # Serve requests until server_running is False
        while server_running:
            server.handle_request()  # Handle one request at a time

    except Exception as e:
        print("❌ Server error: " + str(e))


# Start the server
print("=" * 60)
print("  RHINO HTTP SERVER TEST (Non-Blocking)")
print("=" * 60)
print("Starting HTTP server on localhost:8080")
print("Open your browser and go to: http://localhost:8080")
print("")
print("✨ Rhino will stay responsive!")
print("   You can rotate, zoom, and use Rhino normally")
print("")
print("To stop: Close this Python editor window")
print("=" * 60)

# Create and start server thread
server_thread = threading.Thread(target=run_server)
server_thread.daemon = True  # Thread will stop when script stops
server_thread.start()

print("✅ Server is running in background!")
print("   Try visiting http://localhost:8080 in your browser")
print("")
print("Server status: ACTIVE")
