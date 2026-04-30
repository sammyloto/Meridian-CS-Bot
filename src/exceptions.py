"""Domain exceptions for clear error boundaries between layers."""


class MeridianBotError(Exception):
    """Base class for recoverable application errors."""


class MCPError(MeridianBotError):
    """MCP layer failure (transport or protocol)."""


class MCPConnectionError(MCPError):
    """Network, HTTP, or unreadable response body reaching MCP."""


class MCPClientError(MCPError):
    """JSON-RPC error, invalid MCP payload, or tool-level failure from the server."""


class LLMProviderError(MeridianBotError):
    """OpenAI (or compatible) API failure during chat completion."""
