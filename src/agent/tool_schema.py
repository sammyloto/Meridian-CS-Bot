"""Map MCP tool definitions to OpenAI Chat Completions tool format."""

from __future__ import annotations

from typing import Any

from src.config.constants import OPENAI_TOOL_DESCRIPTION_MAX_CHARS


def mcp_tool_to_openai(mcp_tool: dict[str, Any]) -> dict[str, Any]:
    name = mcp_tool["name"]
    desc = (mcp_tool.get("description") or "").strip()
    schema = mcp_tool.get("inputSchema") or {"type": "object", "properties": {}}
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": desc[:OPENAI_TOOL_DESCRIPTION_MAX_CHARS],
            "parameters": schema,
        },
    }
