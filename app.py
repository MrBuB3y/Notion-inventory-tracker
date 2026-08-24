import pandas as pd
import streamlit as st

from src.config import Settings
from src.metrics import dashboard_metrics
from src.notion_client import NotionRepository


st.set_page_config(page_title="James Resale Dashboard", page_icon="📦", layout="wide")
st.title("James Resale Inventory Dashboard")
st.caption("Inventory and sales analytics powered by Notion")

try:
    settings = Settings.from_environment()
    repository = NotionRepository(settings)
    inventory = repository.fetch_inventory()
    sales = repository.fetch_sales()
    metrics = dashboard_metrics(inventory, sales)
except Exception as exc:
    st.error(f"Dashboard data could not be loaded: {exc}")
    st.info("Check your .env values and confirm both databases are shared with the integration.")
    st.stop()

cols = st.columns(5)
cards = [
    ("Revenue", metrics["total_revenue"], "£{:,.2f}"),
    ("Units sold", metrics["units_sold"], "{:,.0f}"),
    ("Actual profit", metrics["actual_profit"], "£{:,.2f}"),
    ("Actual ROI", metrics["actual_roi"], "{:.1f}%"),
    ("Avg. sell speed", metrics["average_sell_speed"], "{:.1f} days"),
]
for col, (label, value, template) in zip(cols, cards):
    col.metric(label, template.format(value))

st.subheader("Profit outlook")
profit_cols = st.columns(3)
profit_cols[0].metric("Potential profit", f"£{metrics['potential_profit']:,.2f}")
profit_cols[1].metric("Expected profit", f"£{metrics['expected_profit']:,.2f}")
profit_cols[2].metric("Minimum profit", f"£{metrics['minimum_profit']:,.2f}")

st.subheader("Recent sales")
if sales.empty:
    st.info("No sales records found.")
else:
    display_columns = [c for c in ["Product", "Platform", "Date Sold", "Quantity Sold", "Sold Price"] if c in sales]
    recent = sales.sort_values("Date Sold", ascending=False) if "Date Sold" in sales else sales
    st.dataframe(recent[display_columns].head(20), use_container_width=True, hide_index=True)

st.subheader("Inventory requiring attention")
if inventory.empty:
    st.info("No inventory records found.")
else:
    attention = inventory.copy()
    if "Below Minimum" in attention:
        attention = attention[attention["Below Minimum"].fillna(False)]
    columns = [c for c in ["Product Name", "SKU", "Quantity Available", "Asking Price", "Minimum Price", "Price Action"] if c in attention]
    st.dataframe(attention[columns], use_container_width=True, hide_index=True)
