# Architecture

Notion is the source of truth for day-to-day resale operations. The data-access layer retrieves every paginated page and converts supported Notion property types into a pandas-friendly tabular form. The metrics layer contains business rules independently of the interface, making calculations testable. Streamlit is a read-only presentation layer.

## Data flow

1. The user records or updates inventory and sales in Notion.
2. `NotionRepository` queries both databases through the official API.
3. Property values are normalised into pandas DataFrames.
4. `dashboard_metrics` applies quantity-aware financial calculations.
5. Streamlit renders headline metrics, recent sales, and action lists.

## Design decisions

- **Two databases:** avoids duplicating product data for every sale.
- **Sales line items:** supports multi-item orders and different prices per item.
- **Environment configuration:** keeps credentials outside source control.
- **Pure metric function:** allows business logic to be tested without Notion access.
- **Read-only dashboard:** operational edits remain in the familiar Notion interface.
