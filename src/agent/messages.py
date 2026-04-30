"""Construction of OpenAI-style message lists."""

from __future__ import annotations

from typing import Any

from src.config.prompts import SYSTEM_PROMPT


def build_initial_messages(system_extra: str | None = None) -> list[dict[str, Any]]:
    content = SYSTEM_PROMPT
    if system_extra:
        content = f"{SYSTEM_PROMPT}\n\n{system_extra}"
    return [{"role": "system", "content": content}]
