"""MCP tools: actions the client (or an LLM) can ask the server to perform."""

from fastmcp import FastMCP

from .roots import Workspace


def register_tools(mcp: FastMCP, workspace: Workspace) -> None:
    """Attach the file tools and the sampling demo tool to the server."""

    @mcp.tool()
    def read_file(filepath: str) -> str:
        """Read a file from the workspace directory."""
        try:
            path = workspace.resolve(filepath)
            if not path.is_file():
                return f"Error: File not found: {filepath}"
            return path.read_text()
        except PermissionError as e:
            return f"Error: {e}"
        except Exception as e:
            return f"Error reading file: {e}"

    @mcp.tool()
    def write_file(filepath: str, content: str) -> str:
        """Write content to a file in the workspace directory."""
        try:
            path = workspace.resolve(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            return f"Successfully wrote {len(content)} characters to {filepath}"
        except PermissionError as e:
            return f"Error: {e}"
        except Exception as e:
            return f"Error writing file: {e}"

    @mcp.tool()
    def list_files(directory: str = ".") -> str:
        """List files in a directory within the workspace."""
        try:
            path = workspace.resolve(directory)
            if not path.exists():
                return f"Error: Directory not found: {directory}"
            if not path.is_dir():
                return f"Error: Not a directory: {directory}"

            lines = []
            for item in sorted(path.iterdir()):
                kind = "DIR" if item.is_dir() else "FILE"
                size = item.stat().st_size if item.is_file() else 0
                lines.append(f"{kind}: {workspace.relative(item)} ({size} bytes)")
            return "\n".join(lines) or "Directory is empty"
        except PermissionError as e:
            return f"Error: {e}"
        except Exception as e:
            return f"Error listing directory: {e}"

    @mcp.tool()
    def analyze_code(code: str, focus: str = "quality") -> str:
        """Analyze code focusing on the specified aspect.

        Sampling demo: a full implementation would send a
        sampling/createMessage request back to the client so the client's
        LLM does the analysis. Here we only describe that request.
        """
        preview = code[:50].replace("\n", "\\n")
        return (
            "[SAMPLING TRIGGER]\n"
            "This tool would send a sampling/createMessage request to the client:\n\n"
            "{\n"
            "  'method': 'sampling/createMessage',\n"
            "  'params': {\n"
            "    'messages': [{'role': 'user', 'content': {\n"
            "      'type': 'text',\n"
            f"      'text': 'Analyze this code for {focus}:\\n{preview}...'\n"
            "    }}],\n"
            "    'maxTokens': 500\n"
            "  }\n"
            "}\n\n"
            "The client would:\n"
            "1. Show an approval dialog to the user\n"
            "2. If approved, call its LLM with the prompt\n"
            "3. Return the LLM response to the server\n"
            "4. The server would use that response to finish the analysis\n\n"
            "Note: full bidirectional sampling needs the low-level MCP SDK.\n"
            "This simplified version demonstrates the concept."
        )
