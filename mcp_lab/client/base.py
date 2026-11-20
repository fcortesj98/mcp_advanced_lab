"""A thin MCP client that talks to the server over streamable HTTP.

It holds the protocol logic only (no UI and no LLM), so both the GUI
client and the AI host reuse it unchanged.
"""

import asyncio
import logging
from contextlib import AsyncExitStack
from pathlib import Path

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import ListRootsResult, Root

from mcp_lab.config import MCP_ENDPOINT

logging.getLogger("mcp").setLevel(logging.WARNING)


class MCPHTTPClient:
    """Connects to an MCP server and wraps the protocol calls we need."""

    def __init__(self, server_url: str, roots_dir: str):
        self.server_url = server_url.rstrip("/")
        self.roots_dir = Path(roots_dir).resolve()
        self.session: ClientSession | None = None
        self._exit_stack = AsyncExitStack()
        self._connect_lock = asyncio.Lock()

    # --- connection ----------------------------------------------------------

    async def connect(self) -> None:
        """Open the HTTP session once; later calls are no-ops."""
        async with self._connect_lock:
            if self.session is not None:
                return

            read, write, _ = await self._exit_stack.enter_async_context(
                streamablehttp_client(self.server_url + MCP_ENDPOINT)
            )
            self.session = await self._exit_stack.enter_async_context(
                ClientSession(read, write, list_roots_callback=self._list_roots)
            )
            await self.session.initialize()

    async def _list_roots(self, _context) -> ListRootsResult:
        """Answer a server's roots/list request with our allowed folder."""
        return ListRootsResult(roots=[Root(uri=self.roots_dir.as_uri(), name="Workspace")])

    async def cleanup(self) -> None:
        """Close the HTTP session."""
        await self._exit_stack.aclose()
        self.session = None

    # --- tools -----------------------------------------------------------------

    async def list_tools(self):
        await self.connect()
        return (await self.session.list_tools()).tools

    async def call_tool(self, name: str, arguments: dict):
        await self.connect()
        return await self.session.call_tool(name, arguments)

    # --- resources -------------------------------------------------------------

    async def list_resources(self):
        """List resource templates (e.g. file://workspace/{filename})."""
        await self.connect()
        return (await self.session.list_resource_templates()).resourceTemplates

    async def read_resource(self, uri: str):
        await self.connect()
        return await self.session.read_resource(uri)

    # --- prompts ---------------------------------------------------------------

    async def list_prompts(self):
        await self.connect()
        return (await self.session.list_prompts()).prompts

    async def get_prompt(self, name: str, arguments: dict):
        await self.connect()
        return await self.session.get_prompt(name, arguments)
