"""Streamlit UI — session state, layout, and delegation to the chat agent."""

from __future__ import annotations

import copy

import streamlit as st
from openai import OpenAI

from src.agent import build_initial_messages, run_agent_turn
from src.config.settings import Settings
from src.exceptions import MCPError
from src.mcp.client import OrderMCPClient
from src.ui.bootstrap import create_mcp_client_and_openai_tools
from src.ui.error_presenter import format_chat_turn_error, format_mcp_startup_error


@st.cache_resource(show_spinner=False)
def _cached_mcp_bundle(mcp_url: str) -> tuple[OrderMCPClient, list[dict]]:
    return create_mcp_client_and_openai_tools(mcp_url)


def _init_session() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = build_initial_messages()
    if "verified_customer_id" not in st.session_state:
        st.session_state.verified_customer_id = None


def _reset_chat() -> None:
    st.session_state.messages = build_initial_messages()
    st.session_state.verified_customer_id = None


def _display_messages() -> None:
    for m in st.session_state.messages:
        role = m.get("role")
        if role == "system":
            continue
        if role in ("user", "assistant"):
            with st.chat_message(role):
                st.markdown(m.get("content") or "")


def main() -> None:
    st.set_page_config(page_title="Meridian Support", page_icon="🛒", layout="centered")
    settings = Settings.from_env()
    config_errors = settings.validate()

    st.title("Meridian Electronics — Support")
    st.caption("Prototype assistant powered by OpenAI and Meridian order MCP.")

    _init_session()

    with st.sidebar:
        st.subheader("Session")
        if st.session_state.verified_customer_id:
            st.success("Verified customer")
            st.code(st.session_state.verified_customer_id, language=None)
        else:
            st.info("Not verified — PIN flow available in chat.")
        if st.button("Clear conversation", use_container_width=True):
            _reset_chat()
            st.rerun()
        st.divider()
        st.caption(f"MCP: `{settings.mcp_server_url}`")
        st.caption(f"Model: `{settings.openai_model}`")

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

    openai_client = OpenAI(api_key=settings.openai_api_key)

    _display_messages()

    if prompt := st.chat_input("Ask about products, orders, or account verification…"):
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
