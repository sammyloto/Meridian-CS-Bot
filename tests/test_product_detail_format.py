"""Tests for deterministic product description / link formatting."""

import re

from src.agent.product_detail_format import append_product_detail_formatting


def _sample_get_product() -> str:
    return (
        "Product: 24-inch Monitor - Model B\n"
        "SKU: MON-0052\n"
        "Category: Monitors\n"
        "Price: $297.11 USD\n"
        "Stock: 4 units\n"
        "Status: Active\n"
        "Description: Sort research pretty different eat trouble floor.\n"
        "Head maybe top conference source wonder west. Theory tend similar financial.\n"
    )


def test_get_product_appends_description_and_na_link() -> None:
    raw = _sample_get_product()
    out = append_product_detail_formatting("get_product", raw)
    assert "---\n- Description:" in out
    assert "Sort research" in out or "Sort research pretty" in out
    assert "- More info: N/A" in out


def test_get_product_with_url_line() -> None:
    raw = _sample_get_product() + "Product URL: https://example.com/p/monitor\n"
    out = append_product_detail_formatting("get_product", raw)
    assert "[More info](https://example.com/p/monitor)" in out


def test_list_products_row_summary_and_na_link() -> None:
    raw = (
        "Found 2 products:\n\n"
        "![monitors](https://cdn.jsdelivr.net/npm/lucide-static@0.469.0/icons/monitor.svg) "
        "[MON-0052] 24-inch Monitor - Model B\n"
        "  Category: Monitors | Price: $297.11 | Stock: 4 units\n"
    )
    out = append_product_detail_formatting("list_products", raw)
    assert "  - Description:" in out
    assert "24-inch Monitor" in out
    assert "  - More info: N/A" in out


def test_idempotent_second_call() -> None:
    raw = _sample_get_product()
    once = append_product_detail_formatting("get_product", raw)
    twice = append_product_detail_formatting("get_product", once)
    assert once == twice


def test_trim_long_description() -> None:
    long_desc = "x" * 250
    raw = "Product: P\nSKU: COM-0001\nCategory: Computers\nDescription: " + long_desc + "\n"
    out = append_product_detail_formatting("get_product", raw)
    assert "…" in out
    m = re.search(r"- Description: (.+?)\n- More info:", out, re.DOTALL)
    assert m and len(m.group(1)) <= 201
