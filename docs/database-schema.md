# Notion database schema

Property names are case-sensitive because the Python layer maps them by name.

## Inventory

| Property | Suggested Notion type | Purpose |
|---|---|---|
| Product Name | Title | Human-readable item name |
| SKU | Text | `CATEGORY-BRAND-NAME-SIZE` identifier |
| Brand | Select/Text | Product brand |
| Category | Select | Main category |
| Category Type | Select | More specific grouping |
| Condition | Select | Item condition |
| Cost Price | Number (£) | Unit acquisition cost |
| Retail Price | Number (£) | Original/reference retail price |
| Asking Price | Number (£) | Current listing price |
| Expected Price | Number (£) | Realistic sale estimate |
| Minimum Price | Number (£) | Lowest acceptable price |
| Quantity In Stock | Number | Units originally/currently stocked |
| Quantity Sold | Rollup | Sum from related Sales rows; blank treated as zero |
| Quantity Available | Formula | Quantity In Stock minus Quantity Sold |
| Fully Sold | Formula/Checkbox | Whether no units remain |
| Sales | Relation | Links to Sales database |
| All Platforms Listed Date | Date | Basis for age and price action |
| Listed Vinted/eBay/Depop | Checkbox | Platform listing status |
| Days on Market | Formula | Days since listing |
| Price Action | Formula/Select | Review trigger at two weeks/one month |
| Below Minimum | Formula/Checkbox | Current price below minimum |
| Total Revenue | Rollup | Revenue from related sales |
| Actual Profit | Formula | Revenue less sold-unit cost |
| ROI | Formula | Actual profit divided by sold-unit cost |
| Average Sell Price | Rollup/Formula | Average realised unit price |
| Average Sell Speed | Rollup | Average days to sell |
| Stock Status | Formula/Status | In stock, low stock, or sold out |
| Description | Text | Listing description |
| Size, Gender, Colour, Material | Select/Text | Core listing attributes |
| Strap Type, Closure Type, Compartments | Select/Text | Bag attributes |
| Stone / Detail, Theme/Style, Plating/Material Type | Select/Text | Jewellery attributes |
| Set or Single? | Select | Jewellery unit type |

## Sales

| Property | Suggested Notion type | Purpose |
|---|---|---|
| Product | Relation | Related Inventory item |
| SKU | Rollup | SKU from related product |
| Platform | Select | Vinted, eBay, Depop, etc. |
| Date Sold | Date | Transaction date |
| Sold Price | Number (£) | Unit sold price |
| Quantity Sold | Number | Units in this line item |
| Order ID | Text | Groups items from one order |
| Sell Speed | Formula | Days between listing and sale |
| Listed Vinted/eBay/Depop | Rollup | Product listing history if required |
| Cost Price | Rollup | Unit cost used by dashboard calculations |

For multi-item orders, use separate Sales rows for each product and repeat the same Order ID. This preserves the correct price, cost, and sell speed for every item.
