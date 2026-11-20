"""The HTTP MCP server, assembled from its tools, resources and prompts."""

import logging
from pathlib import Path

from fastmcp import FastMCP

from .prompts import register_prompts
from .resources import register_resources
from .roots import Workspace
from .tools import register_tools

logging.getLogger("fastmcp").setLevel(logging.WARNING)


def create_server(workspace_dir: Path) -> FastMCP:
    """Build a FastMCP server whose file access is limited to workspace_dir."""
    mcp = FastMCP("HTTP File Server")
    workspace = Workspace(workspace_dir)

    register_tools(mcp, workspace)
    register_resources(mcp, workspace)
    register_prompts(mcp)
    return mcp


__all__ = ["Workspace", "create_server"]
