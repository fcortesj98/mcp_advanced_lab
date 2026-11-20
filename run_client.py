"""Start the Gradio GUI client (manual access to tools, resources and prompts).

Usage: python run_client.py [server_url] [roots_dir]
Example: python run_client.py http://127.0.0.1:8000 workspace
"""

from mcp_lab.cli import parse_args
from mcp_lab.client import MCPHTTPClient
from mcp_lab.config import GUI_CLIENT_PORT, UI_HOST
from mcp_lab.gui import ClientGUI

if __name__ == "__main__":
    args = parse_args("MCP GUI client")
    client = MCPHTTPClient(args.server_url, args.roots_dir)
    ClientGUI(client).build().queue().launch(server_name=UI_HOST, server_port=GUI_CLIENT_PORT)
