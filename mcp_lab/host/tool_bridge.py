"""Bridge between MCP and OpenAI function calling.

The LLM can only call "functions", so this module:
  1. converts every real MCP tool into an OpenAI function schema, and
  2. adds four *synthetic* functions so the LLM can also reach MCP
     resources and prompts (which are not tools in MCP).
"""

import json

from mcp_lab.client import MCPHTTPClient
from mcp_lab.client.formatting import (
    content_to_text,
    format_prompt_result,
    format_prompts,
    format_resources,
)


def _function(name: str, description: str, properties: dict | None = None, required=None) -> dict:
    """Build one OpenAI function-calling schema."""
    parameters = {"type": "object", "properties": properties or {}}
    if required:
        parameters["required"] = required
    return {
        "type": "function",
        "function": {"name": name, "description": description, "parameters": parameters},
    }


SYNTHETIC_TOOLS = [
    _function("mcp_list_resources", "List all available resources from the MCP server"),
    _function(
        "mcp_read_resource",
        "Read a specific resource by URI from the MCP server",
        {
            "uri": {
                "type": "string",
                "description": "Resource URI, e.g. 'file://workspace/test.txt' (a bare filename also works)",
            }
        },
        required=["uri"],
    ),
    _function("mcp_list_prompts", "List all available prompt templates from the MCP server"),
    _function(
        "mcp_get_prompt",
        "Get a rendered prompt template from the MCP server",
        {
            "name": {"type": "string", "description": "The name of the prompt template"},
            "arguments": {"type": "object", "description": "Arguments for the prompt template"},
        },
        required=["name"],
    ),
]


class ToolBridge:
    """Lists tools for the LLM and executes the calls it makes."""

    def __init__(self, client: MCPHTTPClient):
        self.client = client

    async def openai_tools(self) -> list[dict]:
        """Real MCP tools + synthetic resource/prompt tools, in OpenAI format."""
        real_tools = []
        for tool in await self.client.list_tools():
            schema = tool.inputSchema or {}
            real_tools.append(
                _function(
                    tool.name,
                    tool.description or f"Execute {tool.name}",
                    schema.get("properties"),
                    schema.get("required"),
                )
            )
        return real_tools + SYNTHETIC_TOOLS

    async def execute(self, name: str, arguments_json: str) -> str:
        """Run one tool call from the LLM and return its result as text."""
        try:
            args = json.loads(arguments_json or "{}")
            handler = self._synthetic_handlers().get(name)
            if handler:
                return await handler(args)

            result = await self.client.call_tool(name, args)
            return content_to_text(result.content) or "No response"
        except Exception as e:
            return f"Error executing {name}: {e}"

    # --- synthetic tool handlers ---------------------------------------------------

    def _synthetic_handlers(self) -> dict:
        return {
            "mcp_list_resources": self._list_resources,
            "mcp_read_resource": self._read_resource,
            "mcp_list_prompts": self._list_prompts,
            "mcp_get_prompt": self._get_prompt,
        }

    async def _list_resources(self, _args: dict) -> str:
        return "Available resources:\n" + format_resources(await self.client.list_resources())

    async def _read_resource(self, args: dict) -> str:
        uri = args.get("uri", "")
        if not uri:
            return "Error: URI is required"
        if "://" not in uri:  # a bare filename -> match it to the workspace template
            uri = f"file://workspace/{uri}"
        result = await self.client.read_resource(uri)
        return content_to_text(result.contents) or "No content"

    async def _list_prompts(self, _args: dict) -> str:
        return "Available prompts:\n" + format_prompts(await self.client.list_prompts())

    async def _get_prompt(self, args: dict) -> str:
        name = args.get("name")
        if not name:
            return "Error: Prompt name is required"
        result = await self.client.get_prompt(name, args.get("arguments") or {})
        return format_prompt_result(result)
