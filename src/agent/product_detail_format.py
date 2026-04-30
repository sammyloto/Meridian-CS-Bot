"""
Deterministic Description / More info lines for product MCP tool text.

Runs after icon enrichment. Only uses text present in MCP payloads — no invented URLs.
"""

from __future__ import annotations

import re
from typing import Final

from src.agent.product_icon_enricher import _CATEGORY_LINE  # reuse line pattern

MAX_DESCRIPTION_CHARS: Final[int] = 200

# Labeled URL fields only (case-insensitive key before colon).
_URL_LABEL_RE: Final[re.Pattern[str]] = re.compile(
    r"(?im)^(?:URL|Product URL|Product_URL|Link|Website|Product link):\s*(https?://\S+)",
)

_LIST_SKU_TITLE_RE: Final[re.Pattern[str]] = re.compile(
    r"^(?:!\[[^\]]+\]\([^)]+\)\s*)?(?:\[[A-Z]{3}-\d+\])\s*(?P<title>.+)$",
)


def _trim_description(text: str) -> str:
    t = (text or "").strip()
    if not t:
        return "N/A"
    if len(t) <= MAX_DESCRIPTION_CHARS:
        return t
    return t[: MAX_DESCRIPTION_CHARS - 1].rstrip() + "…"


def _format_more_info(url: str | None) -> str:
    if not url:
        return "N/A"
    u = url.rstrip(").,;\"'")
    return f"[More info]({u})"


def _extract_labeled_url(text: str) -> str | None:
    m = _URL_LABEL_RE.search(text)
    return m.group(1).rstrip(").,;\"'") if m else None


def _extract_get_product_description_block(text: str) -> str | None:
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if not line.strip().lower().startswith("description:"):
            continue
        first = line.split(":", 1)[1].strip()
        chunk: list[str] = [first] if first else []
        j = i + 1
        while j < len(lines):
            nxt = lines[j]
            if not nxt.strip():
                break
            if re.match(
                r"^(SKU|Category|Price|Stock|Status|Product|URL|Link|Website|Product URL)\s*:",
                nxt.strip(),
                re.IGNORECASE,
            ):
                break
            chunk.append(nxt.strip())
            j += 1
        out = "\n".join(chunk).strip()
        return out or None
    return None


def _extract_get_product_title(text: str) -> str | None:
    m = re.search(r"(?im)^Product:\s*(.+)\s*$", text)
    return m.group(1).strip() if m else None


def _detail_marker_present(text: str) -> bool:
    return "  - Description:" in text or "\n---\n- Description:" in text


def append_product_detail_formatting(tool_name: str, text: str) -> str:
    if tool_name not in ("list_products", "search_products", "get_product"):
        return text
    if not text.strip() or _detail_marker_present(text):
        return text
    if tool_name == "get_product":
        return _append_get_product_details(text)
    return _append_list_search_details(text)


def _append_get_product_details(text: str) -> str:
    desc_raw = _extract_get_product_description_block(text)
    title = _extract_get_product_title(text)
    if desc_raw:
        desc = _trim_description(desc_raw)
    elif title:
        desc = _trim_description(title)
    else:
        desc = "N/A"
    url = _extract_labeled_url(text)
    more = _format_more_info(url)
    return text.rstrip() + f"\n\n---\n- Description: {desc}\n- More info: {more}\n"


def _append_list_search_details(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        cat_m = _CATEGORY_LINE.match(line)
        if cat_m:
            already = i + 1 < len(lines) and lines[i + 1].lstrip().startswith("- Description:")
            if not already:
                title_line = _find_nearest_product_title_line(lines, i - 1)
                if title_line:
                    tm = _LIST_SKU_TITLE_RE.match(title_line.strip())
                    title = (tm.group("title") or "").strip() if tm else title_line.strip()
                    window = "\n".join(lines[max(0, i - 2) : min(len(lines), i + 2)])
                    url = _extract_labeled_url(window)
                    desc = _trim_description(title) if title else "N/A"
                    out.append(f"  - Description: {desc}")
                    out.append(f"  - More info: {_format_more_info(url)}")
        i += 1
    return "\n".join(out)


def _find_nearest_product_title_line(lines: list[str], start: int) -> str | None:
    j = start
    while j >= 0:
        s = lines[j].strip()
        if not s:
            j -= 1
            continue
        if re.search(r"\[[A-Z]{3}-\d+\]", s):
            return lines[j]
        j -= 1
    return None
