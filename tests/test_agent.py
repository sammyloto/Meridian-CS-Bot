"""Unit tests for agent helpers (no network)."""

from src.agent.tool_policy import apply_verified_customer_scope
from src.agent.tool_schema import mcp_tool_to_openai


def test_mcp_tool_to_openai_shape() -> None:
    mcp_tool = {
        "name": "get_product",
        "description": "Get a product",
        "inputSchema": {
            "type": "object",
            "properties": {"sku": {"type": "string"}},
            "required": ["sku"],
        },
    }
    oai = mcp_tool_to_openai(mcp_tool)
    assert oai["type"] == "function"
    assert oai["function"]["name"] == "get_product"
    assert oai["function"]["parameters"]["properties"]["sku"]["type"] == "string"


def test_apply_verified_customer_scope() -> None:
    cid = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
    assert apply_verified_customer_scope("list_orders", {}, cid) == {"customer_id": cid}
    assert apply_verified_customer_scope("create_order", {"items": []}, cid) == {
        "customer_id": cid,
        "items": [],
    }
    assert apply_verified_customer_scope("search_products", {"query": "mon"}, cid) == {
        "query": "mon",
    }
