"""Langfuse: env alignment, OpenAI drop-in client, optional MCP tool spans.

Tracing is off unless LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY are both non-empty.
Secrets (PIN, Langfuse keys) must never be logged.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")

# Langfuse SDK reads LANGFUSE_BASE_URL; LANGFUSE_HOST is supported by SDK but we mirror for clarity.
_ENV_PUBLIC = "LANGFUSE_PUBLIC_KEY"
_ENV_SECRET = "LANGFUSE_SECRET_KEY"
_ENV_HOST = "LANGFUSE_HOST"
_ENV_BASE_URL = "LANGFUSE_BASE_URL"

_MAX_TOOL_OUTPUT_CHARS = 8000


def prepare_langfuse_env() -> None:
    """Map LANGFUSE_HOST → LANGFUSE_BASE_URL when base URL unset (SDK default-style behavior)."""
    host = os.environ.get(_ENV_HOST, "").strip()
    base = os.environ.get(_ENV_BASE_URL, "").strip()
    if host and not base:
        os.environ[_ENV_BASE_URL] = host


def langfuse_tracing_enabled() -> bool:
    pub = os.environ.get(_ENV_PUBLIC, "").strip()
    sec = os.environ.get(_ENV_SECRET, "").strip()
    return bool(pub and sec)


def create_openai_client(*, api_key: str) -> Any:
    """Return Langfuse-wrapped OpenAI client when tracing enabled; else stock OpenAI."""
    if not langfuse_tracing_enabled():
        from openai import OpenAI

        return OpenAI(api_key=api_key)
    from langfuse.openai import OpenAI as LangfuseOpenAI

    return LangfuseOpenAI(api_key=api_key)


def _redact_mcp_arguments(tool_name: str, arguments: dict[str, Any] | None) -> dict[str, Any]:
    if not arguments:
        return {}
    out = dict(arguments)
    if tool_name == "verify_customer_pin" and "pin" in out:
        out["pin"] = "[REDACTED]"
    return out


def trace_mcp_tool_call(
    tool_name: str,
    arguments: dict[str, Any] | None,
    fn: Callable[[], T],
) -> T:
    """Run ``fn`` inside a Langfuse tool observation when tracing is enabled."""
    if not langfuse_tracing_enabled():
        return fn()

    from langfuse import get_client

    lf = get_client()
    safe_in = _redact_mcp_arguments(tool_name, arguments)
    with lf.start_as_current_observation(
        name=f"mcp.{tool_name}",
        as_type="tool",
        input={"tool": tool_name, "arguments": safe_in},
        end_on_exit=True,
    ) as obs:
        try:
            result = fn()
        except Exception as exc:
            obs.update(level="ERROR", status_message=str(exc)[:500])
            raise
        out_preview = result if isinstance(result, str) else str(result)
        if len(out_preview) > _MAX_TOOL_OUTPUT_CHARS:
            out_preview = out_preview[:_MAX_TOOL_OUTPUT_CHARS] + "\n… [truncated]"
        obs.update(output=out_preview)
        return result
