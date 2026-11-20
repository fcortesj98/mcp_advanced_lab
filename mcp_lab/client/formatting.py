"""Turn MCP protocol objects into plain text.

Shared by the GUI client and the AI host so both show results the same way.
"""


def content_to_text(items) -> str:
    """Join the text parts of a tool result or resource contents list."""
    texts = [item.text for item in items if hasattr(item, "text")]
    return "\n".join(texts)


def format_tools(tools) -> str:
    return "\n".join(f"• {t.name}: {t.description}" for t in tools) or "No tools available"


def format_resources(templates) -> str:
    lines = []
    for r in templates:
        line = f"• {r.uriTemplate}"
        if r.name:
            line += f" ({r.name})"
        if r.description:
            line += f": {r.description}"
        lines.append(line)
    return "\n".join(lines) or "No resources available"


def format_prompts(prompts) -> str:
    lines = []
    for p in prompts:
        line = f"• {p.name}: {p.description}"
        if p.arguments:
            line += f" (args: {', '.join(a.name for a in p.arguments)})"
        lines.append(line)
    return "\n".join(lines) or "No prompts available"


def format_prompt_result(result) -> str:
    """Render a GetPromptResult as 'role: text' lines."""
    lines = [f"--- Prompt: {result.description} ---", ""]
    for msg in result.messages:
        text = getattr(msg.content, "text", str(msg.content))
        lines.append(f"{msg.role}: {text}")
    return "\n".join(lines)
