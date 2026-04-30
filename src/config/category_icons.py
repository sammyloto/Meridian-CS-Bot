"""
Category buckets and Lucide SVG URLs for product tool output enrichment.

Icons are from Lucide (https://github.com/lucide-icons/lucide) — ISC license,
MIT-compatible; served via jsDelivr for stable, version-pinned URLs.

Pinned package: lucide-static@0.469.0 — paths are /icons/<name>.svg
Docs: https://www.jsdelivr.com/package/npm/lucide-static
"""

from __future__ import annotations

import re
from typing import Final

# --- Six display buckets (stable keys for alt text and routing) ---
BUCKET_COMPUTERS: Final = "computers"
BUCKET_MONITORS: Final = "monitors"
BUCKET_KEYBOARDS: Final = "keyboards"
BUCKET_PRINTERS: Final = "printers"
BUCKET_NETWORKING_GEAR: Final = "networking_gear"
BUCKET_ACCESSORIES: Final = "accessories"

BUCKETS: Final[tuple[str, ...]] = (
    BUCKET_COMPUTERS,
    BUCKET_MONITORS,
    BUCKET_KEYBOARDS,
    BUCKET_PRINTERS,
    BUCKET_NETWORKING_GEAR,
    BUCKET_ACCESSORIES,
)

# --- jsDelivr: one Lucide SVG file per bucket (MIT-compatible Lucide project) ---
_LUCIDE_VER = "0.469.0"
_LUCIDE_BASE: Final[str] = f"https://cdn.jsdelivr.net/npm/lucide-static@{_LUCIDE_VER}/icons"

BUCKET_LUCIDE_SVG: Final[dict[str, str]] = {
    BUCKET_COMPUTERS: f"{_LUCIDE_BASE}/laptop.svg",
    BUCKET_MONITORS: f"{_LUCIDE_BASE}/monitor.svg",
    BUCKET_KEYBOARDS: f"{_LUCIDE_BASE}/keyboard.svg",
    BUCKET_PRINTERS: f"{_LUCIDE_BASE}/printer.svg",
    BUCKET_NETWORKING_GEAR: f"{_LUCIDE_BASE}/router.svg",
    BUCKET_ACCESSORIES: f"{_LUCIDE_BASE}/package.svg",
}

# MCP `Category:` labels (and common variants) → bucket
_CATEGORY_LABEL_TO_BUCKET: Final[dict[str, str]] = {
    "computers": BUCKET_COMPUTERS,
    "computer": BUCKET_COMPUTERS,
    "monitors": BUCKET_MONITORS,
    "monitor": BUCKET_MONITORS,
    "keyboards": BUCKET_KEYBOARDS,
    "keyboard": BUCKET_KEYBOARDS,
    "printers": BUCKET_PRINTERS,
    "printer": BUCKET_PRINTERS,
    "networking": BUCKET_NETWORKING_GEAR,
    "networking gear": BUCKET_NETWORKING_GEAR,
    "network": BUCKET_NETWORKING_GEAR,
    "networks": BUCKET_NETWORKING_GEAR,
    "routers": BUCKET_NETWORKING_GEAR,
    "router": BUCKET_NETWORKING_GEAR,
    "switches": BUCKET_NETWORKING_GEAR,
    "switch": BUCKET_NETWORKING_GEAR,
    "accessories": BUCKET_ACCESSORIES,
    "accessory": BUCKET_ACCESSORIES,
}

# SKU prefix (first segment before hyphen, uppercase) → bucket when category missing
_SKU_PREFIX_TO_BUCKET: Final[dict[str, str]] = {
    "COM": BUCKET_COMPUTERS,
    "MON": BUCKET_MONITORS,
    "KEY": BUCKET_KEYBOARDS,
    "PRI": BUCKET_PRINTERS,
    "NET": BUCKET_NETWORKING_GEAR,
    "ACC": BUCKET_ACCESSORIES,
}

# Keywords in name / description / category (lowercase) → bucket
_KEYWORD_BUCKETS: Final[list[tuple[tuple[str, ...], str]]] = [
    (("monitor", "display", "4k", "24-inch", "27-inch", "ultrawide"), BUCKET_MONITORS),
    (("laptop", "desktop", "workstation", "chromebook", "macbook", "ultrabook", "gaming pc", "tower"), BUCKET_COMPUTERS),
    (("keyboard", "mechanical key"), BUCKET_KEYBOARDS),
    (("printer", "toner", "inkjet"), BUCKET_PRINTERS),
    (("router", "switch", "ethernet", "wifi", "wi-fi", "access point", "mesh"), BUCKET_NETWORKING_GEAR),
    (("mouse", "webcam", "headset", "cable", "adapter", "hub", "dock", "charger"), BUCKET_ACCESSORIES),
]

_SKU_FULL_RE = re.compile(r"\b([A-Z]{3})-(\d+)\b")


def icon_markdown(bucket: str) -> str:
    """Small markdown image line fragment for Streamlit/chat markdown."""
    url = BUCKET_LUCIDE_SVG.get(bucket, BUCKET_LUCIDE_SVG[BUCKET_ACCESSORIES])
    return f"![{bucket}]({url})"


def resolve_product_bucket(
    *,
    category: str | None,
    name: str | None,
    description: str | None,
    sku: str | None,
) -> str:
    """Map MCP-derived fields to one of six buckets; default accessories."""
    haystack = " ".join(
        x for x in (category or "", name or "", description or "") if x
    ).lower()

    if category:
        key = category.strip().lower()
        if key in _CATEGORY_LABEL_TO_BUCKET:
            return _CATEGORY_LABEL_TO_BUCKET[key]

    if sku:
        m = _SKU_FULL_RE.search(sku.upper())
        if m and m.group(1) in _SKU_PREFIX_TO_BUCKET:
            return _SKU_PREFIX_TO_BUCKET[m.group(1)]

    for keywords, bucket in _KEYWORD_BUCKETS:
        if any(k in haystack for k in keywords):
            return bucket

    return BUCKET_ACCESSORIES
