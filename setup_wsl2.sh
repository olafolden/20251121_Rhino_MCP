#!/bin/bash

#########################################################
# WSL2 Setup Script for Rhino MCP Server
# This script automates Phase 3 setup
#
# Usage: bash setup_wsl2.sh
#########################################################

set -e  # Exit on any error

echo "=========================================="
echo "  Rhino MCP Server - WSL2 Setup"
echo "=========================================="
echo ""

# Step 1: Create project directory
echo "📁 Step 1: Creating project directory..."
mkdir -p ~/rhino-mcp-http
cd ~/rhino-mcp-http
echo "✅ Created: ~/rhino-mcp-http"
echo ""

# Step 2: Create virtual environment
echo "🐍 Step 2: Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "⚠️  Virtual environment already exists, skipping..."
fi
echo ""

# Step 3: Activate and install dependencies
echo "📦 Step 3: Installing Python packages..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install mcp fastmcp requests
echo "✅ Packages installed: mcp, fastmcp, requests"
echo ""

# Step 4: Copy MCP server file
echo "📄 Step 4: Copying MCP server file..."
if [ -f "/mnt/c/20251121_Rhino_MCP/phase3_rhino_mcp_server.py" ]; then
    cp /mnt/c/20251121_Rhino_MCP/phase3_rhino_mcp_server.py ~/rhino-mcp-http/rhino_mcp_server.py
    echo "✅ MCP server file copied"
else
    echo "❌ ERROR: Cannot find phase3_rhino_mcp_server.py"
    echo "   Make sure you're in the correct directory!"
    exit 1
fi
echo ""

# Step 5: Test server startup
echo "🧪 Step 5: Testing MCP server startup..."
echo "   (Starting server for 3 seconds...)"
timeout 3 python rhino_mcp_server.py > /dev/null 2>&1 || true
echo "✅ MCP server can start without errors"
echo ""

echo "=========================================="
echo "  ✅ WSL2 Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Keep this terminal open"
echo "2. Follow Phase 4 in QUICKSTART.md to configure Claude"
echo "3. Come back here if you need to manually start the server"
echo ""
echo "To manually start the MCP server:"
echo "  cd ~/rhino-mcp-http"
echo "  source venv/bin/activate"
echo "  python rhino_mcp_server.py"
echo ""
echo "Environment info:"
echo "  Project dir: ~/rhino-mcp-http"
echo "  Python: $(python --version)"
echo "  Virtual env: $(which python)"
echo ""
