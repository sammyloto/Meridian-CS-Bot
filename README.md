---
title: Meridian CS Bot
emoji: 🛒
colorFrom: gray
colorTo: blue
sdk: streamlit
app_file: app.py
pinned: false
license: mit
---

# Meridian Customer Support Chatbot

Streamlit chatbot that answers Meridian Electronics customer questions using **OpenAI tool calling** and the **`order-mcp`** MCP server (inventory, auth, orders).

## Features

- **Product discovery:** `list_products`, `search_products`, `get_product` (with deterministic category icons and description / “More info” lines when MCP text allows)
- **Authentication:** sidebar **email + PIN** → MCP `verify_customer_pin` (no secrets in chat history); optional in-chat tool path still supported by the agent
- **Orders:** `list_orders`, `get_order`, `create_order` (scoped to `verified_customer_id` when the session is verified)

## Architecture

Flow: **Streamlit** (`app.py` → `src/ui/streamlit_app.py`) loads settings, bootstraps **`OrderMCPClient`** + OpenAI tool definitions (`src/ui/bootstrap.py`), and runs **`run_agent_turn`** (`src/agent/chat_agent.py`). The agent calls **OpenAI** with MCP-backed tools; each **`tools/call`** goes through **`src/mcp/client.py`**. Product tool text is enriched (icons, description/link formatting) before it is returned to the model; the final assistant reply can be augmented with icons using recent tool bodies. Session **`verified_customer_id`** (set from sidebar verify) constrains order tools via **`apply_verified_customer_scope`** in `src/agent/tool_policy.py`. Errors surface as **`MCPError`**, **`MCPConnectionError`**, **`MCPClientError`**, or **`LLMProviderError`** (`src/exceptions.py`) and are formatted in **`src/ui/error_presenter.py`**.

```mermaid
flowchart LR
  subgraph ui [Streamlit]
    App[app.py]
    UI[streamlit_app]
  end
  subgraph core [src]
    Boot[ui.bootstrap]
    Agent[agent.chat_agent]
    MCP[mcp.client]
  end
  LLM[OpenAI API]
  Host[order-mcp]
  App --> UI
  UI --> Boot
  UI --> Agent
  Boot --> MCP
  Agent --> LLM
  Agent --> MCP
  MCP --> Host
```

Full detail: [documentation/ARCHITECTURE.md](documentation/ARCHITECTURE.md).

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
streamlit run app.py
```

Copy [.env.example](.env.example) for variable names and defaults. Use Hugging Face **Space secrets** for `OPENAI_API_KEY` in deployment.

## Code layout

| Path | Role |
|------|------|
| `app.py` | Streamlit entrypoint |
| `src/config/` | Settings, prompts, constants, icons |
| `src/mcp/` | MCP JSON-RPC client |
| `src/agent/` | Tool schema, policy, chat loop, product formatting |
| `src/ui/` | Streamlit UI, bootstrap, error copy |
| `src/exceptions.py` | Typed errors by layer |

## Docs

| Doc | Purpose |
|-----|---------|
| [PROJECT_BRIEF.md](documentation/PROJECT_BRIEF.md) | Goals and constraints (local; see .gitignore) |
| [ARCHITECTURE.md](documentation/ARCHITECTURE.md) | Components and data flow |
| [MCP_TOOLS.md](documentation/MCP_TOOLS.md) | Tool reference and guardrails |
| [HF_DEPLOY.md](documentation/HF_DEPLOY.md) | Hugging Face Spaces deployment (local; see .gitignore) |
| [DEMO_SCRIPT.md](documentation/DEMO_SCRIPT.md) | Live demo scenarios (local; see .gitignore) |
| [VIDEO_SUBMISSION.md](documentation/VIDEO_SUBMISSION.md) | Video checklists (local; see .gitignore) |

Tracked in git: **ARCHITECTURE.md** and **MCP_TOOLS.md**. The other four paths exist for local/HF workflows but are listed in `.gitignore` and are not committed.

## Tests

```bash
pytest -q
```

## Default configuration

| Variable | Required | Default (if unset) |
|----------|----------|-------------------|
| `OPENAI_API_KEY` | Yes | — |
| `MCP_SERVER_URL` | No | `https://order-mcp-74afyau24q-uc.a.run.app/mcp` |
| `OPENAI_MODEL` | No | `gpt-4o-mini` |

## License

MIT
