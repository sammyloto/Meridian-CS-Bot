"""Tests for category bucketing and product icon enrichment."""

from src.agent.product_icon_enricher import (
    augment_assistant_reply_with_icons,
    enrich_product_tool_result,
    extract_sku_icon_markdown,
)
from src.config.category_icons import (
    BUCKET_ACCESSORIES,
    BUCKET_COMPUTERS,
    BUCKET_MONITORS,
    BUCKET_NETWORKING_GEAR,
    resolve_product_bucket,
)


def test_resolve_from_mcp_category_label() -> None:
    assert resolve_product_bucket(category="Monitors", name="", description=None, sku=None) == BUCKET_MONITORS
    assert resolve_product_bucket(category="Computers", name="", description=None, sku=None) == BUCKET_COMPUTERS


def test_resolve_from_sku_prefix() -> None:
    assert resolve_product_bucket(category=None, name="", description=None, sku="MON-0052") == BUCKET_MONITORS
    assert resolve_product_bucket(category=None, name="", description=None, sku="NET-0001") == BUCKET_NETWORKING_GEAR


def test_resolve_fallback_accessories() -> None:
    assert (
        resolve_product_bucket(category=None, name="Mystery gadget", description=None, sku="XYZ-9999")
        == BUCKET_ACCESSORIES
    )


def test_enrich_list_products_sample() -> None:
    raw = """Found 2 products:\n\n[MON-0052] 24-inch Monitor - Model B\n  Category: Monitors | Price: $297.11 | Stock: 4 units"""
    out = enrich_product_tool_result("list_products", raw)
    assert "![monitors](" in out
    assert "cdn.jsdelivr.net/npm/lucide-static" in out
    assert out.split("\n")[2].startswith("![monitors]")


def test_enrich_get_product_sample() -> None:
    raw = """Product: 24-inch Monitor - Model B\nSKU: MON-0052\nCategory: Monitors\nPrice: $297.11 USD\n"""
    out = enrich_product_tool_result("get_product", raw)
    assert out.startswith("![monitors](")
    assert "[MON-0052]" in out.split("\n")[0]


def test_augment_assistant_prefixes_sku() -> None:
    tools = [
        enrich_product_tool_result(
            "list_products",
            "[PRI-0001] Office Printer\n  Category: Printers | Price: $10 | Stock: 1",
        )
    ]
    reply = "We have [PRI-0001] in stock."
    aug = augment_assistant_reply_with_icons(reply, tools)
    assert "![printers](" in aug and "[PRI-0001]" in aug
    assert aug.index("![printers](") < aug.index("[PRI-0001]")


def test_extract_sku_icon_map() -> None:
    body = enrich_product_tool_result(
        "list_products",
        "[COM-0001] Box\n  Category: Computers | Price: $1 | Stock: 1",
    )
    m = extract_sku_icon_markdown([body])
    assert "COM-0001" in m
    assert "laptop.svg" in m["COM-0001"]
