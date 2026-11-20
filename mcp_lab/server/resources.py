"""MCP resources: read-only data the client can fetch by URI."""

from fastmcp import FastMCP

from .roots import Workspace

WORKSPACE_FILE_URI = "file://workspace/{filename}"


def register_resources(mcp: FastMCP, workspace: Workspace) -> None:
    """Expose every workspace file as file://workspace/<filename>."""

    @mcp.resource(WORKSPACE_FILE_URI)
    def get_workspace_file(filename: str) -> str:
        """Read a file from the workspace as a resource."""
        path = workspace.resolve(filename)  # raises PermissionError outside roots
        if not path.is_file():
            raise ValueError(f"File not found: {filename}")
        return path.read_text()
