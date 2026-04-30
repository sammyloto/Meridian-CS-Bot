"""JSON-RPC client for order-mcp (Streamable HTTP, JSON responses)."""

from __future__ import annotations

import itertools
import json
from typing import Any

import httpx

from src.exceptions import MCPClientError, MCPConnectionError


class OrderMCPClient:
    def __init__(self, url: str, timeout: float = 60.0) -> None:
        u = url.strip().rstrip("/")
        if not u.endswith("/mcp"):
            u = f"{u}/mcp"
        self.url = u
        self.timeout = timeout
        self._rpc_id = itertools.count(1)
        self._headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        self._initialized = False

    def _post(self, body: dict[str, Any]) -> dict[str, Any] | None:
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(self.url, headers=self._headers, json=body)
                response.raise_for_status()
                text = response.text.strip()
                if not text:
                    return None
                try:
                    return response.json()
                except json.JSONDecodeError as exc:
                    raise MCPConnectionError(
                        "MCP server returned a non-JSON response."
                    ) from exc
        except httpx.HTTPStatusError as exc:
            raise MCPConnectionError(
                f"MCP HTTP error {exc.response.status_code} for {self.url}."
            ) from exc
        except httpx.RequestError as exc:
            raise MCPConnectionError(f"Could not reach MCP server: {exc}") from exc

    def connect(self) -> None:
        if self._initialized:
            return
        init_id = next(self._rpc_id)
        init_resp = self._post(
            {
                "jsonrpc": "2.0",
                "id": init_id,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "meridian-cs-bot", "version": "0.1.0"},
                },
            }
        )
        if not init_resp or "error" in init_resp:
            raise MCPClientError(
                str(init_resp.get("error") if init_resp else "empty initialize response")
            )
        self._post(
            {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {},
            }
        )
        self._initialized = True

    def list_tools(self) -> list[dict[str, Any]]:
        self.connect()
        rid = next(self._rpc_id)
        resp = self._post(
            {
                "jsonrpc": "2.0",
                "id": rid,
                "method": "tools/list",
                "params": {},
            }
        )
        if not resp or "error" in resp:
            raise MCPClientError(str(resp.get("error") if resp else "empty tools/list response"))
        tools = resp.get("result", {}).get("tools")
        if not isinstance(tools, list):
            raise MCPClientError("Invalid tools/list payload.")
        return tools

    def call_tool(self, name: str, arguments: dict[str, Any] | None) -> str:
        self.connect()
        rid = next(self._rpc_id)
        resp = self._post(
            {
                "jsonrpc": "2.0",
                "id": rid,
                "method": "tools/call",
                "params": {"name": name, "arguments": arguments or {}},
            }
        )
        if not resp or "error" in resp:
            err = resp.get("error") if resp else "empty tools/call response"
            if isinstance(err, dict):
                raise MCPClientError(err.get("message", str(err)))
            raise MCPClientError(str(err))
        result = resp.get("result") or {}
        if result.get("isError"):
            parts: list[str] = []
            for block in result.get("content", []):
                if isinstance(block, dict) and block.get("type") == "text":
                    parts.append(str(block.get("text", "")))
            raise MCPClientError("\n".join(parts).strip() or "Tool returned an error.")
        texts: list[str] = []
        for block in result.get("content", []):
            if isinstance(block, dict) and block.get("type") == "text":
                texts.append(str(block.get("text", "")))
        return "\n".join(texts).strip()
