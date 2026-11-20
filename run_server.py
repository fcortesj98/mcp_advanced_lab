"""Start the HTTP MCP server.

Usage: python run_server.py
"""

from mcp_lab.config import SERVER_HOST, SERVER_PORT, WORKSPACE_DIR
from mcp_lab.server import create_server

if __name__ == "__main__":
    print(f"Starting HTTP MCP Server on http://{SERVER_HOST}:{SERVER_PORT}")
    print(f"Workspace roots: {WORKSPACE_DIR}")
    create_server(WORKSPACE_DIR).run(transport="http", host=SERVER_HOST, port=SERVER_PORT)
