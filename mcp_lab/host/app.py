"""Gradio chat UI for the LLM-powered MCP host."""

import gradio as gr

from mcp_lab.client import MCPHTTPClient

from .agent import Agent


class HostGUI:
    """A chat window in front of an Agent."""

    def __init__(self, client: MCPHTTPClient, agent: Agent):
        self.client = client
        self.agent = agent

    async def send(self, message: str, history: list):
        if not message.strip():
            return history
        try:
            reply = await self.agent.chat(message)
        except Exception as e:
            reply = f"Error: {e}"
        return history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": reply},
        ]

    def clear(self):
        self.agent.reset()
        return []

    def build(self) -> gr.Blocks:
        with gr.Blocks(title="MCP HTTP AI Host") as ui:
            gr.Markdown(
                "# MCP HTTP AI Host\n"
                "Chat with an LLM that can use the MCP server's tools, resources and prompts.\n\n"
                f"**Server:** {self.client.server_url}  \n"
                f"**Workspace Roots:** {self.client.roots_dir}  \n"
                f"**Model:** {self.agent.model}"
            )
            chatbot = gr.Chatbot(label="Conversation", height=500, type="messages")
            with gr.Row():
                msg = gr.Textbox(
                    label="Your message", placeholder="Ask me to use MCP tools...", scale=4
                )
                clear_btn = gr.Button("Clear", scale=1)

            msg.submit(self.send, inputs=[msg, chatbot], outputs=chatbot).then(
                lambda: "", outputs=msg
            )
            clear_btn.click(self.clear, outputs=chatbot)
        return ui
