"""Shared settings for the server, the GUI client and the AI host.

Every value can be overridden with an environment variable, so nothing
has to be edited in code to run the lab on a different machine.
"""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# --- MCP server -------------------------------------------------------------
SERVER_HOST = os.getenv("MCP_SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8000"))
SERVER_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"
MCP_ENDPOINT = "/mcp"  # FastMCP serves streamable HTTP on this path

# The "roots" boundary: the server may only touch files inside this folder.
WORKSPACE_DIR = Path(os.getenv("MCP_WORKSPACE", PROJECT_ROOT / "workspace")).resolve()

# --- Gradio apps --------------------------------------------------------------
UI_HOST = os.getenv("UI_HOST", "127.0.0.1")
GUI_CLIENT_PORT = int(os.getenv("GUI_CLIENT_PORT", "7861"))
HOST_APP_PORT = int(os.getenv("HOST_APP_PORT", "7862"))

# --- LLM (AI host only) -------------------------------------------------------
# The OpenAI SDK also reads OPENAI_API_KEY and OPENAI_BASE_URL on its own.
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-6-luna")
MAX_TOOL_ROUNDS = int(os.getenv("MAX_TOOL_ROUNDS", "5"))
