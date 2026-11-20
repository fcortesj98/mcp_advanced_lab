"""Gradio GUI for calling MCP tools, resources and prompts by hand."""

import json

import gradio as gr

from mcp_lab.client import MCPHTTPClient
from mcp_lab.client.formatting import (
    content_to_text,
    format_prompt_result,
    format_prompts,
    format_resources,
    format_tools,
)


def _parse_json(text: str) -> dict:
    return json.loads(text) if text and text.strip() else {}


class ClientGUI:
    """Button handlers plus the Gradio layout, on top of an MCPHTTPClient."""

    def __init__(self, client: MCPHTTPClient):
        self.client = client

    # --- handlers --------------------------------------------------------------

    async def list_tools(self):
        tools = await self.client.list_tools()
        return format_tools(tools), gr.update(choices=[t.name for t in tools])

    async def call_tool(self, name: str, args_json: str) -> str:
        if not name:
            return "Error: Please select a tool from the dropdown first"
        try:
            result = await self.client.call_tool(name, _parse_json(args_json))
            return content_to_text(result.content) or "No response"
        except json.JSONDecodeError:
            return "Error: Invalid JSON format"
        except Exception as e:
            return f"Error: {e}"

    async def list_resources(self) -> str:
        return format_resources(await self.client.list_resources())

    async def read_resource(self, uri: str) -> str:
        if not uri:
            return "Error: Please enter a resource URI"
        try:
            result = await self.client.read_resource(uri)
            return content_to_text(result.contents) or "No content"
        except Exception as e:
            return f"Error: {e}"

    async def list_prompts(self):
        prompts = await self.client.list_prompts()
        return format_prompts(prompts), gr.update(choices=[p.name for p in prompts])

    async def get_prompt(self, name: str, args_json: str) -> str:
        if not name:
            return "Error: Please select a prompt from the dropdown first"
        try:
            result = await self.client.get_prompt(name, _parse_json(args_json))
            return format_prompt_result(result)
        except json.JSONDecodeError:
            return "Error: Invalid JSON format"
        except Exception as e:
            return f"Error: {e}"

    # --- layout ----------------------------------------------------------------

    def build(self) -> gr.Blocks:
        with gr.Blocks(title="MCP HTTP Client") as ui:
            gr.Markdown("# MCP HTTP Client - Remote Server Access")
            gr.Markdown(
                f"**Server:** {self.client.server_url}  \n"
                f"**Workspace Roots:** {self.client.roots_dir}\n\n"
                "All file operations are restricted to the workspace roots directory."
            )
            with gr.Tabs():
                self._tools_tab()
                self._resources_tab()
                self._prompts_tab()
        return ui

    def _tools_tab(self):
        with gr.Tab("Tools"):
            with gr.Row():
                with gr.Column():
                    list_btn = gr.Button("List Tools", variant="primary")
                    listing = gr.Textbox(label="Available Tools", lines=5)
                with gr.Column():
                    dropdown = gr.Dropdown(label="Select Tool", choices=[], interactive=True)
                    args = gr.Textbox(
                        label="Arguments (JSON)", placeholder='{"filepath": "test.txt"}', lines=3
                    )
                    call_btn = gr.Button("Call Tool", variant="primary")
                    result = gr.Textbox(label="Tool Result", lines=8)

            list_btn.click(self.list_tools, outputs=[listing, dropdown])
            call_btn.click(self.call_tool, inputs=[dropdown, args], outputs=result)

    def _resources_tab(self):
        with gr.Tab("Resources"):
            with gr.Row():
                with gr.Column():
                    list_btn = gr.Button("List Resource Templates", variant="primary")
                    listing = gr.Textbox(label="Available Resources", lines=5)
                with gr.Column():
                    uri = gr.Textbox(label="Resource URI", placeholder="file://workspace/README.md")
                    read_btn = gr.Button("Read Resource", variant="primary")
                    content = gr.Textbox(label="Resource Content", lines=10)

            list_btn.click(self.list_resources, outputs=listing)
            read_btn.click(self.read_resource, inputs=uri, outputs=content)

    def _prompts_tab(self):
        with gr.Tab("Prompts"):
            with gr.Row():
                with gr.Column():
                    list_btn = gr.Button("List Prompts", variant="primary")
                    listing = gr.Textbox(label="Available Prompts", lines=5)
                with gr.Column():
                    dropdown = gr.Dropdown(label="Select Prompt", choices=[], interactive=True)
                    args = gr.Textbox(
                        label="Arguments (JSON)", placeholder='{"filename": "example.py"}', lines=2
                    )
                    get_btn = gr.Button("Get Prompt", variant="primary")
                    result = gr.Textbox(label="Prompt Messages", lines=10)

            list_btn.click(self.list_prompts, outputs=[listing, dropdown])
            get_btn.click(self.get_prompt, inputs=[dropdown, args], outputs=result)
