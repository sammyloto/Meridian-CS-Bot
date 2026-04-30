"""Langfuse helpers: env mapping, graceful disable, MCP arg redaction."""

import os

import pytest

from src.observability.langfuse_integration import (
    create_openai_client,
    langfuse_tracing_enabled,
    prepare_langfuse_env,
    trace_mcp_tool_call,
)


@pytest.fixture(autouse=True)
def clear_langfuse_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in (
        "LANGFUSE_PUBLIC_KEY",
        "LANGFUSE_SECRET_KEY",
        "LANGFUSE_HOST",
        "LANGFUSE_BASE_URL",
    ):
        monkeypatch.delenv(key, raising=False)


def test_prepare_langfuse_env_maps_host_to_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LANGFUSE_HOST", "https://eu.example.com")
    monkeypatch.delenv("LANGFUSE_BASE_URL", raising=False)
    prepare_langfuse_env()
    assert os.environ.get("LANGFUSE_BASE_URL") == "https://eu.example.com"


def test_prepare_langfuse_env_preserves_explicit_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LANGFUSE_HOST", "https://ignored.example.com")
    monkeypatch.setenv("LANGFUSE_BASE_URL", "https://explicit.example.com")
    prepare_langfuse_env()
    assert os.environ.get("LANGFUSE_BASE_URL") == "https://explicit.example.com"


def test_langfuse_tracing_enabled_only_with_both_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    assert langfuse_tracing_enabled() is False
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "pk-lf-test")
    assert langfuse_tracing_enabled() is False
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "sk-lf-test")
    assert langfuse_tracing_enabled() is True


def test_create_openai_client_fallback_without_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    from openai import OpenAI as VanillaOpenAI

    monkeypatch.delenv("LANGFUSE_PUBLIC_KEY", raising=False)
    monkeypatch.delenv("LANGFUSE_SECRET_KEY", raising=False)
    client = create_openai_client(api_key="sk-openai-test")
    assert isinstance(client, VanillaOpenAI)


def test_trace_mcp_tool_call_no_keys_runs_inline(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LANGFUSE_PUBLIC_KEY", raising=False)
    monkeypatch.delenv("LANGFUSE_SECRET_KEY", raising=False)
    calls = {"n": 0}

    def inner() -> str:
        calls["n"] += 1
        return "ok"

    assert trace_mcp_tool_call("list_products", {}, inner) == "ok"
    assert calls["n"] == 1


def test_redact_verify_customer_pin_arguments() -> None:
    from src.observability.langfuse_integration import _redact_mcp_arguments

    r = _redact_mcp_arguments("verify_customer_pin", {"email": "x@y.com", "pin": "9999"})
    assert r["pin"] == "[REDACTED]"
    assert r["email"] == "x@y.com"
