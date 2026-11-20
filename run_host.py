"""Start the LLM-powered AI host (chat UI that uses the MCP server).

Usage: python run_host.py [server_url] [roots_dir]
Example: python run_host.py http://127.0.0.1:8000 workspace
"""

from mcp_lab.cli import parse_args
from mcp_lab.client import MCPHTTPClient
from mcp_lab.config import HOST_APP_PORT, LLM_MODEL, UI_HOST
from mcp_lab.host import Agent, HostGUI, ToolBridge

if __name__ == "__main__":
    args = parse_args("MCP AI host")
    client = MCPHTTPClient(args.server_url, args.roots_dir)
    agent = Agent(ToolBridge(client), model=LLM_MODEL)
    HostGUI(client, agent).build().queue().launch(server_name=UI_HOST, server_port=HOST_APP_PORT)
