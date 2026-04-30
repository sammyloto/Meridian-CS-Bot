# Meridian Customer Support Chatbot — Project brief

## Business problem

Meridian Electronics sells computer products (monitors, keyboards, printers, networking, accessories). Support is currently **phone and email only**, which is slow, expensive, and does not scale for repetitive questions.

Leadership wants a **low-cost LLM chatbot** that can:

- Check **product availability** and details
- Help customers **place orders**
- Look up **order history**
- **Authenticate** returning customers with a simple email + PIN flow

The internal team exposes business logic as **MCP (Model Context Protocol)** so the chatbot never talks to the database directly.

## Technical constraints (assessment)

| Constraint | Decision |
|------------|----------|
| LLM | Cost-effective tier: e.g. **GPT-4o-mini**, Gemini Flash, or Claude Haiku |
| UI | **Streamlit** (fast prototype) |
| Deployment | **Hugging Face Spaces** (minimum); secrets for API keys |
| Integration | **Streamable HTTP** MCP client to `order-mcp` |

## MCP server

- **URL:** `https://order-mcp-74afyau24q-uc.a.run.app/mcp`
- **Transport:** HTTP POST with `Content-Type: application/json` and `Accept: application/json, text/event-stream`
- **Handshake:** `initialize` → `notifications/initialized` → `tools/list` / `tools/call`

## Success criteria

1. **Working chat** that uses MCP tools for factual inventory and order data (no invented SKUs or prices).
2. **Clean structure** suitable for security review (`mcp_client`, `agent`, `prompts`, `app`).
3. **Deployable** HF Space with documented environment variables.
4. **Demo-ready** scenarios documented in [DEMO_SCRIPT.md](DEMO_SCRIPT.md).

## Out of scope (time-box)

- Next.js / full custom frontend
- Production-grade auth (OAuth, MFA)
- Full observability stack

See also: [ARCHITECTURE.md](ARCHITECTURE.md), [MCP_TOOLS.md](MCP_TOOLS.md), [HF_DEPLOY.md](HF_DEPLOY.md), [VIDEO_SUBMISSION.md](VIDEO_SUBMISSION.md).
