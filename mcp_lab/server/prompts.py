"""MCP prompts: reusable prompt templates with arguments."""

from fastmcp import FastMCP


def register_prompts(mcp: FastMCP) -> None:
    """Attach the code-review prompt templates to the server."""

    @mcp.prompt()
    def review_code(filename: str) -> str:
        """Generate a prompt to review code from a file."""
        return f"""Please review the code in file '{filename}' and provide:

1. A summary of what the code does
2. Potential bugs or issues
3. Security concerns
4. Suggestions for improvements
5. Code quality assessment

Focus on readability, maintainability, and best practices."""

    @mcp.prompt()
    def analyze_security(filename: str) -> str:
        """Generate a prompt to analyze security of a file."""
        return f"""Perform a security analysis of '{filename}' focusing on:

1. Input validation and sanitization
2. Authentication and authorization checks
3. Potential injection vulnerabilities
4. Data exposure risks
5. Error handling security

Provide specific line numbers and remediation suggestions."""
