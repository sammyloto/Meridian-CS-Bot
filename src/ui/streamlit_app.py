"""Streamlit UI — session state, layout, and delegation to the chat agent."""

from __future__ import annotations

import copy
import html

import streamlit as st
from openai import OpenAI

from src.agent import build_initial_messages, run_agent_turn
from src.agent.tool_policy import (
    extract_customer_id_from_verify_response,
    extract_customer_name_from_get_customer_response,
    extract_customer_name_from_verify_response,
)
from src.config.settings import Settings
from src.config.ui_icons import LUCIDE_USER_ICON_URL
from src.exceptions import MCPClientError, MCPError
from src.mcp.client import OrderMCPClient
from src.ui.bootstrap import create_mcp_client_and_openai_tools
from src.ui.error_presenter import format_chat_turn_error, format_mcp_startup_error

# Synthetic user line (no secrets) so the model knows the session is verified.
# We persist this once in `messages` after sidebar verify — it appears in chat as a benign line.
SYNTHETIC_VERIFICATION_USER_MESSAGE = "I completed account verification for this session."


@st.cache_resource(show_spinner=False)
def _cached_mcp_bundle(mcp_url: str) -> tuple[OrderMCPClient, list[dict]]:
    return create_mcp_client_and_openai_tools(mcp_url)


@st.cache_data(ttl=60, show_spinner=False)
def _cached_list_orders_text(mcp_server_url: str, customer_id: str) -> str:
    client = OrderMCPClient(mcp_server_url)
    return client.call_tool("list_orders", {"customer_id": customer_id, "status": None})


def _mask_customer_id(customer_id: str) -> str:
    c = customer_id.strip()
    if len(c) <= 8:
        return c
    return f"{c[:8]}…"


def _init_session() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = build_initial_messages()
    if "verified_customer_id" not in st.session_state:
        st.session_state.verified_customer_id = None
    if "verified_customer_email" not in st.session_state:
        st.session_state.verified_customer_email = None
    if "verified_customer_name" not in st.session_state:
        st.session_state.verified_customer_name = None


def _reset_chat() -> None:
    st.session_state.messages = build_initial_messages()
    st.session_state.verified_customer_id = None
    st.session_state.verified_customer_email = None
    st.session_state.verified_customer_name = None
    for k in ("sidebar_auth_email", "sidebar_auth_pin"):
        st.session_state.pop(k, None)


def _conversation_includes_verification_notice(messages: list[dict]) -> bool:
    return any(
        m.get("role") == "user" and m.get("content") == SYNTHETIC_VERIFICATION_USER_MESSAGE
        for m in messages
    )


def _append_verification_notice_once() -> None:
    if _conversation_includes_verification_notice(st.session_state.messages):
        return
    st.session_state.messages.append(
        {"role": "user", "content": SYNTHETIC_VERIFICATION_USER_MESSAGE},
    )


def _display_messages() -> None:
    for m in st.session_state.messages:
        role = m.get("role")
        if role == "system":
            continue
        if role in ("user", "assistant"):
            with st.chat_message(role):
                st.markdown(m.get("content") or "")


def _render_sidebar_auth_and_profile(
    *,
    mcp: OrderMCPClient,
    mcp_server_url: str,
) -> None:
    st.subheader("Account")
    st.text_input("Email", key="sidebar_auth_email")
    st.text_input("PIN", type="password", key="sidebar_auth_pin")
    if st.button("Verify", use_container_width=True):
        email = (st.session_state.get("sidebar_auth_email") or "").strip()
        pin = (st.session_state.get("sidebar_auth_pin") or "").strip()
        if not email or not pin:
            st.warning("Enter both email and PIN.")
        else:
            try:
                raw = mcp.call_tool("verify_customer_pin", {"email": email, "pin": pin})
            except MCPClientError:
                st.error("Verification failed. Check email and PIN.")
            else:
                cid = extract_customer_id_from_verify_response(raw)
                if not cid:
                    st.error("Verification failed.")
                else:
                    st.session_state.verified_customer_id = cid
                    st.session_state.verified_customer_email = email
                    name = extract_customer_name_from_verify_response(raw)
                    if not name:
                        try:
                            cust = mcp.call_tool("get_customer", {"customer_id": cid})
                        except MCPClientError:
                            name = None
                        else:
                            name = extract_customer_name_from_get_customer_response(cust)
                    st.session_state.verified_customer_name = (name or "").strip() or None
                    _append_verification_notice_once()
                    st.session_state.pop("sidebar_auth_email", None)
                    st.session_state.pop("sidebar_auth_pin", None)
                    st.rerun()

    st.divider()
    st.subheader("Session")
    cid = st.session_state.verified_customer_id
    if cid:
        st.caption("Verified · customer id")
        st.code(_mask_customer_id(cid), language=None)
        display_name = (st.session_state.verified_customer_name or "").strip() or "Customer"
        safe_name = html.escape(display_name)
        st.markdown(
            f'<img src="{LUCIDE_USER_ICON_URL}" width="20" style="vertical-align:middle"/> '
            f"<strong>{safe_name}</strong>",
            unsafe_allow_html=True,
        )
        st.caption("Orders (from Meridian)")
        try:
            orders_text = _cached_list_orders_text(mcp_server_url, cid)
        except MCPClientError:
            st.warning("Could not load orders right now.")
        else:
            snippet = orders_text.strip()
            if len(snippet) > 1200:
                snippet = snippet[:1200] + "\n…"
            st.code(snippet or "No orders returned.", language=None)
    else:
        st.info("Sign in with email and PIN above. Do not send your PIN in the chat box.")

    if st.button("Clear conversation", use_container_width=True):
        _reset_chat()
        st.rerun()


def main() -> None:
    st.set_page_config(page_title="Meridian Support", page_icon="🛒", layout="centered")
    settings = Settings.from_env()
    config_errors = settings.validate()

    st.title("Meridian Electronics — Support")
    st.caption("Prototype assistant powered by OpenAI and Meridian order MCP.")

    _init_session()

    if config_errors:
        for err in config_errors:
            st.error(err)
        st.stop()

    try:
        mcp, openai_tools = _cached_mcp_bundle(settings.mcp_server_url)
    except MCPError as exc:
        st.error(format_mcp_startup_error(exc))
        st.stop()
    except Exception as exc:
        st.error(format_mcp_startup_error(exc))
        st.stop()

    with st.sidebar:
        _render_sidebar_auth_and_profile(mcp=mcp, mcp_server_url=settings.mcp_server_url)

    openai_client = OpenAI(api_key=settings.openai_api_key)

    _display_messages()

    if prompt := st.chat_input("Ask about products, orders, or shipping…"):
        user_message = {"role": "user", "content": prompt}
        st.session_state.messages.append(user_message)
        with st.chat_message("user"):
            st.markdown(prompt)

        convo_snapshot = copy.deepcopy(st.session_state.messages)
        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("Thinking…")
            try:
                reply, new_cid, updated = run_agent_turn(
                    openai_client=openai_client,
                    model=settings.openai_model,
                    mcp=mcp,
                    openai_tools=openai_tools,
                    messages=convo_snapshot,
                    verified_customer_id=st.session_state.verified_customer_id,
                )
            except Exception as exc:
                placeholder.markdown(format_chat_turn_error(exc))
                st.session_state.messages.pop()
                st.stop()
            st.session_state.messages = updated
            st.session_state.verified_customer_id = new_cid
            placeholder.markdown(reply or "_No response_")
