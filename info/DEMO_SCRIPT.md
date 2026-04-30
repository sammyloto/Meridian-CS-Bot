# Live demo script (Video 3)

Run through these **after** the Space (or local app) is warm. Replace placeholders with credentials your assessors provide (or discover via a test `verify_customer_pin` flow).

## 1. Guest product browse

**Say:** "I'm looking for 24-inch monitors. What do you have in stock?"

**Expected tools:** `search_products` and/or `list_products` with category Monitors if offered.

**Pass if:** SKUs, prices, and stock come from tool output (assistant cites concrete SKUs like `MON-0054`).

## 2. Product detail

**Say:** "Tell me the price and stock for MON-0054."

**Expected tools:** `get_product`

**Pass if:** Single SKU details match tool text.

## 3. Authenticate

**Say:** "Please verify me. My email is `{EMAIL}` and my PIN is `{PIN}`."

**Expected tools:** `verify_customer_pin`

**Pass if:** Assistant confirms identity; sidebar shows **Verified customer** UUID.

## 4. Order history

**Say:** "What are my recent orders?"

**Expected tools:** `list_orders` (with authenticated customer)

**Pass if:** Orders listed; optionally ask to expand one order.

## 5. Order detail

**Say:** "Show me details for order `{ORDER_ID}`."

**Expected tools:** `get_order`

**Pass if:** Line items visible.

## 6. Place order (use with care in shared environments)

**Say:** "I'd like to order 1× MON-0054."

**Expected tools:** `get_product` (price) → `create_order`

**Pass if:** Confirmation includes order id/status from MCP; no invented prices.

---

## Expected tool sequence cheat sheet

| Scenario | Typical sequence |
|----------|------------------|
| Browse | `search_products` → optional `get_product` |
| Auth | `verify_customer_pin` |
| History | `list_orders` → `get_order` |
| Purchase | `get_product` → `create_order` |
