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

- **Product discovery:** `list_products`, `search_products`, `get_product`
- **Authentication:** `verify_customer_pin` (email + 4-digit PIN)
- **Orders:** `list_orders`, `get_order`, `create_order` (scoped to verified customer when available)

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
streamlit run app.py
```

Copy [.env.example](.env.example) for reference. The app reads **`OPENAI_API_KEY`** from the environment (use HF Space secrets in production).

## Code layout

| Path | Role |
|------|------|
| `app.py` | Streamlit entrypoint |
| `src/config/` | Settings, prompts, constants |
| `src/mcp/` | MCP JSON-RPC client |
| `src/agent/` | Tool schema, policy, OpenAI tool loop |
| `src/ui/` | Streamlit app, bootstrap, user-facing errors |
| `src/exceptions.py` | Typed errors by layer |

## Docs

| Doc | Purpose |
|-----|---------|
| [PROJECT_BRIEF.md](info/PROJECT_BRIEF.md) | Goals and constraints |
| [ARCHITECTURE.md](info/ARCHITECTURE.md) | Components and data flow |
| [MCP_TOOLS.md](info/MCP_TOOLS.md) | Tool reference and guardrails |
| [HF_DEPLOY.md](info/HF_DEPLOY.md) | Hugging Face Spaces deployment |
| [DEMO_SCRIPT.md](info/DEMO_SCRIPT.md) | Live demo scenarios |
| [VIDEO_SUBMISSION.md](info/VIDEO_SUBMISSION.md) | Video checklists and submission notes |

## Tests

```bash
pytest -q
```

## Default configuration

| Variable | Default |
|----------|---------|
| `MCP_SERVER_URL` | `https://order-mcp-74afyau24q-uc.a.run.app/mcp` |
| `OPENAI_MODEL` | `gpt-4o-mini` |

## License

MIT
