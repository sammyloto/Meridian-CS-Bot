"""Wiring MCP client and OpenAI tool definitions (framework-agnostic)."""

from __future__ import annotations

from typing import Any

from src.agent.tool_schema import mcp_tool_to_openai
from src.mcp.client import OrderMCPClient


def create_mcp_client_and_openai_tools(mcp_url: str) -> tuple[OrderMCPClient, list[dict[str, Any]]]:
    """
    Connect to MCP and build OpenAI tool specs.
    Raises MCPConnectionError or MCPClientError on failure.
    """
    client = OrderMCPClient(mcp_url)
    client.connect()
    raw_tools = client.list_tools()
    openai_tools = [mcp_tool_to_openai(t) for t in raw_tools]
    return client, openai_tools
