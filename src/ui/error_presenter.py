"""Map internal exceptions to safe user-visible strings."""

from __future__ import annotations

from src.exceptions import LLMProviderError, MCPConnectionError, MCPError, MeridianBotError


def format_mcp_startup_error(exc: BaseException) -> str:
    """Message shown when MCP bootstrap (connect / list_tools) fails."""
    if isinstance(exc, MCPConnectionError):
        return f"Could not reach MCP server: {exc}"
    if isinstance(exc, MCPError):
        return f"Could not reach MCP server: {exc}"
    return f"MCP startup failed: {exc}"


def format_chat_turn_error(exc: BaseException) -> str:
    """Message shown when a single chat turn fails after user input."""
    if isinstance(exc, LLMProviderError):
        return f"The assistant service hit an error: `{exc}`"
    if isinstance(exc, MeridianBotError):
        return f"Something went wrong: `{exc}`"
    return f"Something went wrong: `{exc}`"
