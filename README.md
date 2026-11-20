# Advanced MCP Applications: Streamable HTTP, Roots and Sampling

A small client-server project built on the **Model Context Protocol (MCP)**. A FastMCP server runs as a standalone HTTP service, and two different apps connect to it over **streamable HTTP**:

- **GUI client**: a Gradio app where you discover and call the server's tools, resources and prompts by hand.
- **AI host**: a Gradio chat where an LLM decides which MCP tools to call for you.

The project covers three MCP ideas:

| Concept | What it does here |
|---|---|
| **Streamable HTTP** | The server runs on its own (`http://127.0.0.1:8000/mcp`), not as a subprocess, so many clients can connect to it. |
| **Roots** | All file access stays inside `workspace/`. Paths like `/etc/passwd` or `../secret` are rejected. |
| **Sampling** | `analyze_code` shows the `sampling/createMessage` request a server would send to ask the client's LLM for help. This is a demo of the concept only. |

## Project structure

```
mcp_advanced_lab/
├── run_server.py          # start the MCP server
├── run_client.py          # start the GUI client
├── run_host.py            # start the AI host
├── workspace/             # the only folder the server can read/write (roots)
└── mcp_lab/
    ├── config.py          # ports, URLs, workspace path, model (overridable by env vars)
    ├── cli.py             # shared command-line arguments
    ├── server/            # FastMCP server
    │   ├── roots.py       #   Workspace: blocks paths outside the root
    │   ├── tools.py       #   read_file, write_file, list_files, analyze_code
    │   ├── resources.py   #   file://workspace/{filename}
    │   └── prompts.py     #   review_code, analyze_security
    ├── client/            # protocol only (no UI, no LLM)
    │   ├── base.py        #   MCPHTTPClient: connect, list/call tools, resources, prompts
    │   └── formatting.py  #   turns MCP results into readable text
    ├── gui/app.py         # Gradio GUI client
    └── host/              # LLM host
        ├── tool_bridge.py #   MCP tools -> OpenAI functions (+ synthetic resource/prompt tools)
        ├── agent.py       #   chat loop: LLM -> tool calls -> LLM
        └── app.py         #   Gradio chat UI
```

The GUI client and the AI host both use the same `MCPHTTPClient`, so the MCP protocol code is written only once.

## Setup

Requires Python 3.11+.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The AI host uses the OpenAI SDK. In the IBM Skills Network lab environment it works without extra setup. Anywhere else, set your credentials and a model you have access to:

```bash
export OPENAI_API_KEY=sk-...
export LLM_MODEL=gpt-4o-mini            # default: gpt-6-luna (lab model)
# export OPENAI_BASE_URL=...            # optional, for an OpenAI-compatible endpoint
```

## Usage

Run each component in its own terminal, from the project folder.

**1. Start the server**

```bash
python run_server.py
# Starting HTTP MCP Server on http://127.0.0.1:8000
```

**2a. GUI client** → http://127.0.0.1:7861

```bash
python run_client.py http://127.0.0.1:8000 workspace
```

Things to try:
- **Tools tab**: List Tools, choose `list_files`, args `{"directory": "."}`, then Call Tool.
- **Roots check**: `read_file` with `{"filepath": "/etc/passwd"}` returns *Access denied*.
- **Resources tab**: read `file://workspace/test.txt`.
- **Prompts tab**: `review_code` with `{"filename": "test.txt"}`.

**2b. AI host** → http://127.0.0.1:7862

```bash
python run_host.py http://127.0.0.1:8000 workspace
```

Example messages:
- `Create a file called hello.txt with the message: Hello from HTTP MCP!`
- `Read the file /etc/passwd` (the LLM explains that the file is outside the workspace)
- `What resources are available? Then read one of them.`
- `Show me the available prompts, then get the review_code prompt for test.txt`
- `Use analyze_code to analyze this code: def add(a, b): return a + b`

Both arguments are optional: by default the apps use `http://127.0.0.1:8000` and the local `workspace/` folder.

### Configuration

| Variable | Default | Purpose |
|---|---|---|
| `MCP_SERVER_HOST` / `MCP_SERVER_PORT` | `127.0.0.1` / `8000` | Where the server listens |
| `MCP_WORKSPACE` | `./workspace` | Roots folder the server is limited to |
| `GUI_CLIENT_PORT` / `HOST_APP_PORT` | `7861` / `7862` | Gradio ports |
| `LLM_MODEL` | `gpt-6-luna` | Model used by the AI host |
| `MAX_TOOL_ROUNDS` | `5` | Maximum tool-call rounds per chat message |

## Acknowledgements

Built as part of the IBM RAG and Agentic AI Professional Certificate, offered by IBM through Coursera. The certificate covers LangChain, LangGraph, RAG pipelines, vector databases, multimodal AI, and agentic frameworks such as CrewAI, AG2, BeeAI, and the Model Context Protocol. Model access is provided by IBM watsonx.ai.
