# Rhino 8 MCP Server

Connect Claude AI to your active Rhino 8 window for AI-assisted 3D modeling!

## What This Does

This project lets you talk to Claude in natural language and have it create 3D geometry in your Rhino window.

**Example**:
- You: "Claude, create a box at position (10, 10, 0) with dimensions 20×15×10"
- Claude: *Creates the box in your Rhino viewport*

## Quick Start

1. **Read this first**: Open `context.md` for the complete step-by-step guide
2. **Track progress**: Open `context-revised.md` to follow your implementation progress
3. **Start Phase 1**: Open Rhino 8 and follow Phase 1 instructions in context-revised.md

## Project Files

| File | Purpose |
|------|---------|
| `context.md` | Complete implementation guide with all code |
| `context-revised.md` | Progress tracker with checkpoints |
| `README.md` | This file - quick overview |

## Requirements

- Windows 10/11
- Rhino 8 installed
- WSL2 installed and configured
- Python 3.10+ in WSL2
- Claude Desktop

## Implementation Phases

1. ✅ **Setup** - GitHub repo created
2. 📍 **Phase 1** (10 min) - Test Rhino HTTP capability
3. **Phase 2** (15 min) - Build full Rhino HTTP server
4. **Phase 3** (10 min) - Create MCP server in WSL2
5. **Phase 4** (5 min) - Configure Claude Desktop
6. **Phase 5** (5 min) - End-to-end testing

**Total Time**: ~60 minutes

## Architecture

```
Claude Desktop → MCP Server (WSL2) → HTTP Server (Rhino) → Your 3D Model
```

## Getting Help

- Check `context.md` Section 8 (Troubleshooting)
- Review `context-revised.md` for common issues
- Check Phase-specific notes in context-revised.md

## Next Steps

👉 **Open `context-revised.md` and start Phase 1!**

---

*Generated with Claude Code*
