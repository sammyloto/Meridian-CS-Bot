# MCP tools — `order-mcp`

All tools return **human-readable text** in `tools/call` → `result.content[].type == "text"`.

## Catalog

| Tool | Arguments | When to use |
|------|-----------|-------------|
| `list_products` | `category?`, `is_active?` | Browse catalog, stock by category |
| `get_product` | `sku` (string) | Price, stock, details for one SKU |
| `search_products` | `query` (string) | Keyword / NL product lookup |
| `get_customer` | `customer_id` (UUID) | Profile lookup (post-auth) |
| `verify_customer_pin` | `email`, `pin` (4-digit string) | Authenticate returning customer |
| `list_orders` | `customer_id?`, `status?` | Order history; status: `draft`, `submitted`, `approved`, `fulfilled`, `cancelled` |
| `get_order` | `order_id` (UUID) | One order with line items |
| `create_order` | `customer_id`, `items[]` | Place order |

### `items` shape for `create_order`

Each element:

- `sku` (string)
- `quantity` (int, &gt; 0)
- `unit_price` (string, decimal)
- `currency` (string, default `USD`)

## Guardrails (bot behavior)

1. **Never invent** SKUs, prices, or stock — always from `get_product`, `list_products`, or `search_products`.
2. **Before `create_order`:** call `get_product` for each SKU to obtain the **current** `unit_price` and confirm stock.
3. **Order history / checkout:** prefer `verify_customer_pin` first; then use returned customer context.
4. On MCP errors (not found, insufficient inventory), **relay the server message** and suggest next steps.

## Example user utterances → tools

- "What monitors do you have?" → `list_products` / `search_products`
- "How much is MON-0054?" → `get_product`
- "Log me in, email … PIN …" → `verify_customer_pin`
- "My recent orders" → `list_orders` (with authenticated `customer_id`)
- "Show order abc-…" → `get_order`
- "Buy 2 of MON-0054" → `get_product` then `create_order`
