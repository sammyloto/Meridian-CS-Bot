# Video submission pack

Use this file when completing the **record-videos** deliverable: scripts, checklist, and where to paste your **Space URL** and screenshots.

## Video 1 — Kickoff (submit by start + 30 min)

Record **3–5 minutes** covering:

1. **Business problem:** Meridian’s support load; need for self-service on catalog, orders, and light auth without DB access from the LLM.
2. **Plan:** MCP discovery → Streamlit vertical slice → error handling → HF deploy.
3. **Cuts if time runs out:** no Next.js; minimal tests; defer advanced observability.

## Video 2 — Mid-point (submit by start + 1 hr 45 min)

Record **3–5 minutes** covering:

1. **Built so far:** Streamlit UI, MCP client, agent loop with OpenAI tools.
2. **Decisions:** GPT-4o-mini (cost/latency), Streamlit + HF for shareable demo, session-bound `customer_id` after PIN verify.
3. **AI code fixes:** structured tool calls, timeouts, tool-first system prompt.
4. **Challenges:** MCP Accept headers, `unit_price` from `get_product`, HF cold start.

## Video 3 — Final (3–10 min)

1. **Hook:** problem + MCP as safe integration layer + low-cost model.
2. **Live demo:** follow [DEMO_SCRIPT.md](DEMO_SCRIPT.md) (browse → detail → auth → history → optional order).
3. **Code walk:** `app.py` → `agent.py` → `mcp_client.py` → `prompts.py` / `settings.py`.
4. **Honest recap:** strengths, limits (PIN auth, no human handoff), next steps (OAuth, tests, audit logs).
5. **Recommendation:** pilot vs wait — be explicit.

---

## Checklist before recording Video 3

- [ ] Space URL is live (paste below)
- [ ] Warm up Space once to avoid cold-start failure
- [ ] Test credentials ready for `verify_customer_pin`
- [ ] Browser zoom readable for code + demo

## Deployed chatbot URL

Paste your Hugging Face Space URL here after deploy:

`_________________________________________________`

## Screenshots

Capture and attach (or store under [docs/screenshots/](../docs/screenshots/) if your course allows):

1. Chat showing **product search** with real SKUs from MCP
2. **Verified customer** sidebar + order list
3. **Order detail** or **create_order** confirmation (optional)

---

## Notes

- Recording software: QuickTime (macOS), OBS, or Loom.
- Keep **API keys** out of the frame; blur if needed.
