"""Tool argument shaping and post-verify customer binding."""

from __future__ import annotations

import json
import re
from typing import Any

_UUID_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.IGNORECASE,
)


def parse_tool_arguments_json(raw: str) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}


def extract_customer_name_from_verify_response(text: str) -> str | None:
    """Best-effort parse of customer display name from verify_customer_pin tool text."""
    for line in text.splitlines():
        raw = line.strip()
        if not raw:
            continue
        lower = raw.lower()
        for prefix in ("name:", "full name:", "customer name:", "display name:"):
            if lower.startswith(prefix):
                val = raw.split(":", 1)[-1].strip()
                return val or None
    return None


def extract_customer_name_from_get_customer_response(text: str) -> str | None:
    """Parse get_customer MCP text for a human-readable name."""
    if "not found" in text.lower() or text.lower().startswith("mcp error"):
        return None
    return extract_customer_name_from_verify_response(text)


def extract_customer_id_from_verify_response(text: str) -> str | None:
    for line in text.splitlines():
        lower = line.lower()
        if "customer" in lower and "id" in lower:
            m = _UUID_RE.search(line)
            if m:
                return m.group(0)
    m = _UUID_RE.search(text)
    return m.group(0) if m else None


def apply_verified_customer_scope(
    name: str,
    arguments: dict[str, Any],
    verified_customer_id: str | None,
) -> dict[str, Any]:
    if not verified_customer_id:
        return arguments
    out = dict(arguments)
    if name == "list_orders":
        out["customer_id"] = verified_customer_id
    elif name == "create_order":
        out["customer_id"] = verified_customer_id
    return out
