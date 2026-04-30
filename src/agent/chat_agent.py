"""OpenAI tool-calling loop backed by order-mcp."""

from __future__ import annotations

from typing import Any

from openai import APIConnectionError, APIError, APITimeoutError, OpenAI, RateLimitError

from src.agent.product_detail_format import append_product_detail_formatting
from src.agent.product_icon_enricher import (
    augment_assistant_reply_with_icons,
    enrich_product_tool_result,
    tool_contents_since_last_user,
)
from src.agent.tool_policy import (
    apply_verified_customer_scope,
    extract_customer_id_from_verify_response,
    parse_tool_arguments_json,
)
from src.config.constants import MAX_AGENT_TOOL_ROUNDS
from src.exceptions import LLMProviderError, MCPClientError
from src.mcp.client import OrderMCPClient


def run_agent_turn(
    *,
    openai_client: OpenAI,
    model: str,
    mcp: OrderMCPClient,
    openai_tools: list[dict[str, Any]],
    messages: list[dict[str, Any]],
    verified_customer_id: str | None,
) -> tuple[str, str | None, list[dict[str, Any]]]:
    """
    Run one user turn. Returns (assistant_text, updated_verified_customer_id, updated_messages).
    """
    convo: list[dict[str, Any]] = list(messages)
    active_customer_id = verified_customer_id

    for _ in range(MAX_AGENT_TOOL_ROUNDS):
        try:
            response = openai_client.chat.completions.create(
                model=model,
                messages=convo,
                tools=openai_tools,
                tool_choice="auto",
            )
        except (APIConnectionError, APITimeoutError, RateLimitError, APIError) as exc:
            raise LLMProviderError(str(exc)) from exc

        msg = response.choices[0].message

        if not msg.tool_calls:
            text = (msg.content or "").strip()
            tool_bodies = tool_contents_since_last_user(convo)
            text = augment_assistant_reply_with_icons(text, tool_bodies)
            convo.append({"role": "assistant", "content": text})
            return text, active_customer_id, convo

        assistant_payload: dict[str, Any] = {
            "role": "assistant",
            "content": msg.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments or "{}",
                    },
                }
                for tc in msg.tool_calls
            ],
        }
        convo.append(assistant_payload)

        for tc in msg.tool_calls:
            name = tc.function.name
            args = parse_tool_arguments_json(tc.function.arguments or "{}")
            scoped = apply_verified_customer_scope(name, args, active_customer_id)
            try:
                tool_text = mcp.call_tool(name, scoped)
            except MCPClientError as exc:
                tool_text = f"MCP error ({name}): {exc}"
            else:
                tool_text = enrich_product_tool_result(name, tool_text)
                tool_text = append_product_detail_formatting(name, tool_text)
            if name == "verify_customer_pin" and not tool_text.lower().startswith("mcp error"):
                extracted = extract_customer_id_from_verify_response(tool_text)
                if extracted:
                    active_customer_id = extracted
            convo.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": tool_text,
                }
            )

    fallback = (
        "Sorry — this request needed too many tool steps. Please try a simpler question or break it into parts."
    )
    convo.append({"role": "assistant", "content": fallback})
    return fallback, active_customer_id, convo
