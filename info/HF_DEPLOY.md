# Hugging Face Spaces deployment

## Prerequisites

- Hugging Face account
- OpenAI API key (or adapt code for another provider)

## Create a Space

1. New Space → SDK **Streamlit**
2. Connect this GitHub repo (or push a copy)
3. Set **App file** to `app.py` (matches repo layout)

## Repository layout for HF

- `app.py` — Streamlit entrypoint
- `requirements.txt` — Python dependencies
- `README.md` — includes YAML **frontmatter** for Space metadata (`sdk: streamlit`, `app_file: app.py`)

## Secrets (Space settings → Repository secrets)

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key |
| `MCP_SERVER_URL` | No | Defaults to assessment MCP URL if unset |
| `OPENAI_MODEL` | No | Default `gpt-4o-mini` |

Do **not** commit keys. Use HF secrets only.

## Cold starts

Spaces may sleep when idle. First request after sleep can take **30–60+ seconds**. For live demos, open the Space once beforehand or mention cold start in the presentation.

## Local run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...
streamlit run app.py
```

Optional: copy `.env.example` to `.env` and use `python-dotenv` if you add it; the stock app reads `os.environ` only.

## Troubleshooting

- **MCP errors:** Check Cloud Run MCP is reachable from HF egress (it should be over public HTTPS).
- **Empty replies:** Verify model name and API key; check Streamlit logs in Space "Logs" tab.
