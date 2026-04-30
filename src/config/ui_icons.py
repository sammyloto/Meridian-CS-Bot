"""Lucide SVG URLs for UI chrome (sidebar, etc.) — same pin as category_icons."""

from __future__ import annotations

from typing import Final

# Keep in sync with src/config/category_icons.py
_LUCIDE_VER = "0.469.0"
_LUCIDE_BASE: Final[str] = f"https://cdn.jsdelivr.net/npm/lucide-static@{_LUCIDE_VER}/icons"

LUCIDE_USER_ICON_URL: Final[str] = f"{_LUCIDE_BASE}/user.svg"
