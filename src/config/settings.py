"""Environment-driven settings."""

from __future__ import annotations

import os
from dataclasses import dataclass


DEFAULT_MCP_URL = "https://order-mcp-74afyau24q-uc.a.run.app/mcp"
DEFAULT_MODEL = "gpt-4o-mini"


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    mcp_server_url: str
    openai_model: str

    @classmethod
    def from_env(cls) -> Settings:
        key = os.environ.get("OPENAI_API_KEY", "").strip()
        return cls(
            openai_api_key=key,
            mcp_server_url=os.environ.get("MCP_SERVER_URL", DEFAULT_MCP_URL).strip(),
            openai_model=os.environ.get("OPENAI_MODEL", DEFAULT_MODEL).strip(),
        )

    def validate(self) -> list[str]:
        """Return human-readable configuration errors (empty if valid)."""
        errors: list[str] = []
        if not self.openai_api_key:
            errors.append("OPENAI_API_KEY is not set.")
        if not self.mcp_server_url:
            errors.append("MCP_SERVER_URL is empty.")
        return errors
