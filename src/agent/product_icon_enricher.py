"""Deterministic Lucide icon injection for product MCP tool text and assistant replies."""

from __future__ import annotations

import re
from typing import Final

from src.config.category_icons import icon_markdown, resolve_product_bucket

PRODUCT_TOOL_NAMES: Final[frozenset[str]] = frozenset(
    {"list_products", "search_products", "get_product"}
)

# Matches list/search lines like: [MON-0052] 24-inch Monitor …
_LIST_PRODUCT_LINE: Final[re.Pattern[str]] = re.compile(
    r"^(?P<prefix>!\[[^\]]+\]\([^)]+\)\s*)?(?P<sku>\[[A-Z]{3}-\d+\])(?P<rest>\s*.*)$"
)
_CATEGORY_LINE: Final[re.Pattern[str]] = re.compile(
    r"^\s*Category:\s*(?P<cat>[^|]+)",
)
_SKU_LINE_GET: Final[re.Pattern[str]] = re.compile(r"^SKU:\s*(?P<sku>[A-Z]{3}-\d+)\s*$", re.MULTILINE)
_CATEGORY_LINE_GET: Final[re.Pattern[str]] = re.compile(
    r"^Category:\s*(?P<cat>.+)\s*$",
    re.MULTILINE,
)
_PRODUCT_TITLE_GET: Final[re.Pattern[str]] = re.compile(
    r"^Product:\s*(?P<name>.+)\s*$",
    re.MULTILINE,
)

# Built from tool output after enrichment — capture icon markdown + SKU id
_SKU_ICON_PAIR_RE: Final[re.Pattern[str]] = re.compile(
    r"(?<!\()(!\[[^\]]+\]\((?:https://cdn\.jsdelivr\.net/npm/lucide-static)[^)]+\))\s*\[([A-Z]{3}-\d+)\]"
)


def enrich_product_tool_result(tool_name: str, text: str) -> str:
    """Inject category icons into raw MCP product tool strings."""
    if tool_name not in PRODUCT_TOOL_NAMES or not text.strip():
        return text
    if tool_name == "get_product":
        return _enrich_get_product_detail(text)
    return _enrich_list_or_search(text)


def _enrich_list_or_search(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = _LIST_PRODUCT_LINE.match(line)
        if not m:
            out.append(line)
            i += 1
            continue
        if m.group("prefix"):
            out.append(line)
            i += 1
            continue

        sku_bracket = m.group("sku")
        sku_id = sku_bracket.strip("[]")
        rest_name = m.group("rest") or ""
        category_val: str | None = None
        if i + 1 < len(lines):
            cm = _CATEGORY_LINE.match(lines[i + 1])
            if cm:
                category_val = cm.group("cat").strip()

        bucket = resolve_product_bucket(
            category=category_val,
            name=f"{sku_bracket}{rest_name}",
            description=None,
            sku=sku_id,
        )
        icon = icon_markdown(bucket)
        out.append(f"{icon} {line}")
        i += 1

    return "\n".join(out)


def _enrich_get_product_detail(text: str) -> str:
    if text.lstrip().startswith("![") and "](" in text.split("\n", 1)[0]:
        return text

    sku_m = _SKU_LINE_GET.search(text)
    cat_m = _CATEGORY_LINE_GET.search(text)
    name_m = _PRODUCT_TITLE_GET.search(text)

    sku = sku_m.group("sku") if sku_m else None
    category = cat_m.group("cat").strip() if cat_m else None
    name = name_m.group("name").strip() if name_m else None

    bucket = resolve_product_bucket(
        category=category,
        name=name,
        description=None,
        sku=sku,
    )
    icon = icon_markdown(bucket)
    sku_part = f" [{sku}]" if sku else ""
    header = f"{icon}{sku_part}\n\n"
    return header + text


def extract_sku_icon_markdown(tool_texts: list[str]) -> dict[str, str]:
    """SKU id → markdown icon fragment from enriched tool bodies."""
    found: dict[str, str] = {}
    for body in tool_texts:
        if not body:
            continue
        for m in _SKU_ICON_PAIR_RE.finditer(body):
            found[m.group(2)] = m.group(1)

        # get_product: first line is icon + optional [SKU]; map via SKU: field below
        first_line = body.split("\n", 1)[0]
        header_m = re.match(
            r"^(!\[[^\]]+\]\((?:https://cdn\.jsdelivr\.net/npm/lucide-static)[^)]+\))\s*(?:\[([A-Z]{3}-\d+)\])?\s*$",
            first_line,
        )
        if header_m:
            sku_from_bracket = header_m.group(2)
            sku_m = _SKU_LINE_GET.search(body)
            sku_key = sku_from_bracket or (sku_m.group("sku") if sku_m else None)
            if sku_key:
                found.setdefault(sku_key, header_m.group(1))
    return found


def augment_assistant_reply_with_icons(reply: str, tool_bodies: list[str]) -> str:
    """Prefix each bare `[SKU]` mention in the assistant reply with the bucket icon from tools."""
    if not reply or not tool_bodies:
        return reply

    sku_to_icon = extract_sku_icon_markdown(tool_bodies)
    if not sku_to_icon:
        return reply

    # Replace each `[ABC-1234]` once when not already preceded by our lucide URL pattern
    result = reply
    for sku, icon_md in sku_to_icon.items():
        token = f"[{sku}]"
        pos = 0
        while True:
            idx = result.find(token, pos)
            if idx == -1:
                break
            window_start = max(0, idx - 120)
            window = result[window_start:idx]
            if "cdn.jsdelivr.net/npm/lucide-static" in window:
                pos = idx + len(token)
                continue
            result = result[:idx] + f"{icon_md} " + result[idx:]
            pos = idx + len(icon_md) + 1 + len(token)
    return result


def tool_contents_since_last_user(convo: list[dict]) -> list[str]:
    """Collect tool message bodies after the last user message in an OpenAI-style conversation."""
    last_user = -1
    for i, m in enumerate(convo):
        if m.get("role") == "user":
            last_user = i
    if last_user < 0:
        return []

    bodies: list[str] = []
    for m in convo[last_user + 1 :]:
        if m.get("role") == "tool" and isinstance(m.get("content"), str):
            bodies.append(m["content"])
    return bodies
