"""Command-line arguments shared by the GUI client and the AI host."""

import argparse

from mcp_lab.config import SERVER_URL, WORKSPACE_DIR


def parse_args(description: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "server_url", nargs="?", default=SERVER_URL, help=f"MCP server URL (default: {SERVER_URL})"
    )
    parser.add_argument(
        "roots_dir", nargs="?", default=str(WORKSPACE_DIR), help="Workspace roots directory"
    )
    return parser.parse_args()
