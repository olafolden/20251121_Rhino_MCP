#!/bin/bash

#########################################################
# Test Script for Rhino HTTP Server (Phase 2)
# This script tests if the Rhino HTTP server is working
#
# Usage: bash test_rhino_server.sh
#
# Prerequisites:
# - Rhino 8 must be running
# - phase2_rhino_http_server.py must be running in Rhino
#########################################################

echo "=========================================="
echo "  Testing Rhino HTTP Server"
echo "=========================================="
echo ""

# Get Windows hostname for WSL2
WINDOWS_HOST=$(hostname).local
RHINO_URL="http://${WINDOWS_HOST}:8080"

echo "Target: $RHINO_URL"
echo ""

# Test 1: Ping
echo "Test 1: Ping Rhino server..."
echo "---"
RESPONSE=$(curl -s -X POST "$RHINO_URL" \
  -H "Content-Type: application/json" \
  -d '{"action": "ping"}' 2>&1)

if [[ $RESPONSE == *"Rhino server is running"* ]]; then
    echo "✅ PASS: Rhino server is responsive"
    echo "Response: $RESPONSE"
else
    echo "❌ FAIL: Cannot connect to Rhino server"
    echo "Response: $RESPONSE"
    echo ""
    echo "Troubleshooting:"
    echo "1. Is Rhino running?"
    echo "2. Is the HTTP server script running in Rhino?"
    echo "3. Do you see '✅ Server is running!' in Rhino?"
    echo ""
    echo "Try opening this in a browser: http://localhost:8080"
    exit 1
fi
echo ""

# Test 2: Create Box
echo "Test 2: Create a box at (10, 10, 0)..."
echo "---"
RESPONSE=$(curl -s -X POST "$RHINO_URL" \
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
  }' 2>&1)

if [[ $RESPONSE == *"success"* ]]; then
    echo "✅ PASS: Box created successfully"
    echo "Response: $RESPONSE"
    echo ""
    echo "👀 Check Rhino - you should see a box at position (10, 10, 0)!"
else
    echo "❌ FAIL: Could not create box"
    echo "Response: $RESPONSE"
    exit 1
fi
echo ""

# Test 3: Create Sphere
echo "Test 3: Create a sphere at (30, 0, 0)..."
echo "---"
RESPONSE=$(curl -s -X POST "$RHINO_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "create_sphere",
    "params": {
      "x": 30,
      "y": 0,
      "z": 0,
      "radius": 8
    }
  }' 2>&1)

if [[ $RESPONSE == *"success"* ]]; then
    echo "✅ PASS: Sphere created successfully"
    echo "Response: $RESPONSE"
    echo ""
    echo "👀 Check Rhino - you should see a sphere at position (30, 0, 0)!"
else
    echo "❌ FAIL: Could not create sphere"
    echo "Response: $RESPONSE"
    exit 1
fi
echo ""

echo "=========================================="
echo "  ✅ All Tests Passed!"
echo "=========================================="
echo ""
echo "Your Rhino HTTP server is working correctly!"
echo "You can now proceed to Phase 3 (MCP Server setup)"
echo ""
echo "In Rhino, type 'ZoomExtents' to see all geometry"
echo ""
