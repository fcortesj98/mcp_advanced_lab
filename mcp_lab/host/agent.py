"""The LLM agent loop: ask the model, run any tools it calls, repeat."""

from openai import AsyncOpenAI

from mcp_lab.config import MAX_TOOL_ROUNDS

from .tool_bridge import ToolBridge


class Agent:
    """Keeps the conversation and lets the LLM use MCP through a ToolBridge."""

    def __init__(self, bridge: ToolBridge, model: str, llm: AsyncOpenAI | None = None):
        self.bridge = bridge
        self.model = model
        self.llm = llm or AsyncOpenAI()
        self.history: list[dict] = []

    def reset(self) -> None:
        self.history = []

    async def chat(self, user_message: str) -> str:
        self.history.append({"role": "user", "content": user_message})
        tools = await self.bridge.openai_tools()

        for _ in range(MAX_TOOL_ROUNDS):
            message = await self._complete(tools)
            if not message.tool_calls:
                return self._remember(message.content)

            # 1) record the model's request to call tools
            self.history.append(
                {
                    "role": "assistant",
                    "content": message.content or "",
                    "tool_calls": [
                        {
                            "id": call.id,
                            "type": "function",
                            "function": {
                                "name": call.function.name,
                                "arguments": call.function.arguments,
                            },
                        }
                        for call in message.tool_calls
                    ],
                }
            )
            # 2) run each tool on the MCP server and record the result
            for call in message.tool_calls:
                output = await self.bridge.execute(call.function.name, call.function.arguments)
                self.history.append({"role": "tool", "tool_call_id": call.id, "content": output})

        # Too many rounds: ask for a final answer without offering tools.
        return self._remember((await self._complete(tools=None)).content)

    async def _complete(self, tools: list[dict] | None):
        kwargs = {"model": self.model, "messages": self.history}
        if tools:
            kwargs.update(tools=tools, tool_choice="auto")
        response = await self.llm.chat.completions.create(**kwargs)
        return response.choices[0].message

    def _remember(self, text: str | None) -> str:
        text = text or "(no response)"
        self.history.append({"role": "assistant", "content": text})
        return text
