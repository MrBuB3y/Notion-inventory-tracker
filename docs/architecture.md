# Architecture

Notion is the source of truth for day-to-day resale operations. The Streamlit application retrieves every paginated page, converts supported Notion property types into pandas-friendly tables, merges Sales with Inventory through Notion page IDs, applies the business calculations and renders a read-only dashboard.

## Data flow

1. The user records or updates inventory and sales in Notion.
2. `query_notion_database` queries both databases through the official REST API.
3. Property values are normalised into pandas DataFrames.
4. `build_analytics` applies quantity-aware financial calculations.
5. Streamlit renders headline metrics, recent sales, and action lists.

## Design decisions

- **Two databases:** avoids duplicating product data for every sale.
- **Sales line items:** supports multi-item orders and different prices per item.
- **Environment configuration:** keeps credentials outside source control.
- **Explicit transformation functions:** keeps API parsing, cleaning and calculations understandable within the current single-app implementation.
- **Read-only dashboard:** operational edits remain in the familiar Notion interface.
