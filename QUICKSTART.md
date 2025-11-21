# Quick Start Guide - Rhino MCP Server

**Goal**: Get Claude talking to your Rhino 8 window in ~60 minutes

## Before You Start

Make sure you have:
- ✅ Rhino 8 installed and can open it
- ✅ WSL2 installed (you're using it now!)
- ✅ Claude Desktop installed
- ✅ This folder open: `C:\20251121_Rhino_MCP`

## The 5 Phases (with Checkpoints!)

### 📍 Phase 1: Simple HTTP Test (10 min)
**Goal**: Make sure Rhino can run a web server

**Steps**:
1. Open Rhino 8
2. In Rhino, type: `EditPythonScript` and press Enter
3. Open the file: `phase1_simple_http_test.py` from this folder
4. Copy ALL the code from that file
5. Paste it into Rhino's Python editor
6. Click the ▶ (Run/Play) button
7. You should see: "Starting HTTP server on localhost:8080"

**Test It**:
- Open your web browser (Chrome, Edge, Firefox - any browser)
- Go to: `http://localhost:8080`
- Browser should say: "Point created at origin!"
- Look at Rhino - you should see a point at 0,0,0!

**✅ Checkpoint 1**: If you see the point in Rhino, Phase 1 is DONE!

**Stop the server**: Press `Esc` key a few times in Rhino

---

### 📍 Phase 2: Full HTTP Server (15 min)
**Goal**: Build a real server that can create boxes and spheres

**Steps**:
1. In Rhino's Python editor, click File → New (to start fresh)
2. Open the file: `phase2_rhino_http_server.py` from this folder
3. Copy ALL the code
4. Paste it into Rhino's Python editor
5. Click File → Save As, save it as `rhino_http_server.py`
6. Click the ▶ (Run/Play) button
7. You should see: "✅ Server is running! Waiting for commands..."

**Test It from WSL2**:
Open your WSL2 terminal and run these commands:

```bash
# Test 1: Ping Rhino
curl -X POST http://$(hostname).local:8080 \
  -H "Content-Type: application/json" \
  -d '{"action": "ping"}'

# Expected response: {"status": "ok", "message": "Rhino server is running!"}

# Test 2: Create a box
curl -X POST http://$(hostname).local:8080 \
  -H "Content-Type: application/json" \
  -d '{"action": "create_box", "params": {"x": 10, "y": 10, "z": 0, "width": 20, "height": 15, "depth": 10}}'

# Expected: A box appears in Rhino!
```

**✅ Checkpoint 2**: If the box appears in Rhino, Phase 2 is DONE!

**Leave the server running** for the next phases!

---

### 📍 Phase 3: MCP Server (10 min)
**Goal**: Create the bridge between Claude and Rhino

**Steps in WSL2**:

```bash
# 1. Create project folder
mkdir -p ~/rhino-mcp-http
cd ~/rhino-mcp-http

# 2. Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install required packages
pip install mcp fastmcp requests

# 4. Copy the MCP server file
cp /mnt/c/20251121_Rhino_MCP/phase3_rhino_mcp_server.py ~/rhino-mcp-http/rhino_mcp_server.py

# 5. Test that it starts (it will just wait for input)
python rhino_mcp_server.py
# Press Ctrl+C to stop it - that's normal!
```

**✅ Checkpoint 3**: If the MCP server started without errors, Phase 3 is DONE!

---

### 📍 Phase 4: Configure Claude (5 min)
**Goal**: Tell Claude Desktop about your new MCP server

**Steps**:

1. **Find the config file**:
   - Press `Win + R` (Windows Run dialog)
   - Type: `%APPDATA%\Claude`
   - Press Enter
   - You should see: `claude_desktop_config.json`

2. **Edit the config**:
   - Right-click `claude_desktop_config.json`
   - Open with Notepad
   - If the file is empty or only has `{}`, replace everything with this:

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

   - If the file already has stuff in it, add the `"rhino-active"` part inside the `"mcpServers"` section

3. **Save and close** Notepad

4. **Restart Claude Desktop**:
   - Close Claude Desktop COMPLETELY (check system tray!)
   - Reopen Claude Desktop
   - Look for the 🔨 hammer icon - that means MCP tools loaded!

**✅ Checkpoint 4**: If you see the 🔨 icon, Phase 4 is DONE!

---

### 📍 Phase 5: TEST IT! (5 min)
**Goal**: Make Claude create geometry in Rhino!

**Before testing**:
- Make sure Rhino is open
- Make sure the HTTP server is running in Rhino (you should see "✅ Server is running!" in Rhino's Python editor)

**Test in Claude Desktop**:

**Test 1 - Ping**:
Type in Claude:
```
Can you ping Rhino to see if it's running?
```
Expected: ✅ Rhino is running and ready!

**Test 2 - Create Box**:
Type in Claude:
```
Create a box at position (10, 10, 0) with dimensions 20 × 15 × 10
```
Expected: A box appears in Rhino!

**Test 3 - Create Sphere**:
Type in Claude:
```
Create a sphere at (30, 0, 0) with radius 8
```
Expected: A sphere appears in Rhino!

**Test 4 - Multiple Objects**:
Type in Claude:
```
Create three boxes in a row:
- First at (0, 0, 0), size 10×10×10
- Second at (15, 0, 0), size 10×10×10
- Third at (30, 0, 0), size 10×10×10
```
Expected: Three boxes appear in Rhino!

**✅ Checkpoint 5**: If all geometry appears, YOU'RE DONE! 🎉

---

## Troubleshooting

### "Cannot connect to Rhino"
- Is Rhino running?
- Is the HTTP server script running in Rhino?
- Try visiting http://localhost:8080 in your browser - does it work?

### "Port 8080 already in use"
- Close any other programs that might be using port 8080
- Or change the port in both scripts (Rhino server AND MCP server)

### MCP tools not showing in Claude (no 🔨 icon)
- Check that `claude_desktop_config.json` is saved correctly
- Make sure the JSON is valid (no extra commas, brackets match)
- Try completely closing Claude Desktop and reopening

### Geometry not appearing in Rhino
- Is the HTTP server still running? Check Rhino's Python editor window
- Type `ZoomExtents` in Rhino to see all geometry
- Check Rhino's command line for any error messages

---

## What to Do After Success

Once everything works:
1. Update `context-revised.md` with your completion times
2. Note any issues you encountered
3. Try asking Claude to create more complex geometry!
4. Explore the `context.md` file for ideas on extending the system

---

## Getting Help

- Check `context.md` Section 8 (Troubleshooting) for detailed help
- Review `context-revised.md` for implementation notes
- All the code has comments explaining what it does!

---

**Ready to start? Open Rhino 8 and begin Phase 1!** 🚀
