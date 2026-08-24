# -*- coding: utf-8 -*-

import os
import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

st.set_page_config(page_title="Resale Dashboard", layout="wide")
load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
INVENTORY_DATABASE_ID = os.getenv("INVENTORY_DATABASE_ID")
SALES_DATABASE_ID = os.getenv("SALES_DATABASE_ID")

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}


def query_notion_database(database_id: str) -> list[dict]:
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    results = []
    payload = {}

    while True:
        response = requests.post(url, headers=HEADERS, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()

        results.extend(data.get("results", []))

        if not data.get("has_more"):
            break

        payload["start_cursor"] = data.get("next_cursor")

    return results


def extract_rollup_array_item(item):
    item_type = item.get("type")

    if item_type == "title":
        return "".join(t.get("plain_text", "") for t in item.get("title", [])).strip()

    if item_type == "rich_text":
        return "".join(t.get("plain_text", "") for t in item.get("rich_text", [])).strip()

    if item_type == "number":
        return item.get("number")

    if item_type == "select":
        val = item.get("select")
        return val.get("name") if val else None

    if item_type == "date":
        val = item.get("date")
        return val.get("start") if val else None

    if item_type == "formula":
        formula = item.get("formula", {})
        formula_type = formula.get("type")
        return formula.get(formula_type)

    return str(item)


def extract_property_value(prop: dict):
    prop_type = prop.get("type")

    if prop_type == "title":
        return "".join(t.get("plain_text", "") for t in prop.get("title", [])).strip()

    if prop_type == "rich_text":
        return "".join(t.get("plain_text", "") for t in prop.get("rich_text", [])).strip()

    if prop_type == "number":
        return prop.get("number")

    if prop_type == "select":
        value = prop.get("select")
        return value.get("name") if value else None

    if prop_type == "multi_select":
        values = prop.get("multi_select", [])
        return ", ".join(v.get("name", "") for v in values)

    if prop_type == "date":
        value = prop.get("date")
        return value.get("start") if value else None

    if prop_type == "checkbox":
        return prop.get("checkbox")

    if prop_type == "url":
        return prop.get("url")

    if prop_type == "formula":
        formula = prop.get("formula", {})
        formula_type = formula.get("type")
        return formula.get(formula_type)

    if prop_type == "relation":
        relations = prop.get("relation", [])
        return [r.get("id") for r in relations]

    if prop_type == "rollup":
        rollup = prop.get("rollup", {})
        rollup_type = rollup.get("type")

        if rollup_type == "number":
            return rollup.get("number")

        if rollup_type == "date":
            value = rollup.get("date")
            return value.get("start") if isinstance(value, dict) else value

        if rollup_type == "array":
            items = rollup.get("array", [])
            extracted = [extract_rollup_array_item(item) for item in items]

            if len(extracted) == 0:
                return None
            if len(extracted) == 1:
                return extracted[0]
            return extracted

    return None


def notion_pages_to_dataframe(pages: list[dict]) -> pd.DataFrame:
    records = []

    for page in pages:
        row = {"Page ID": page.get("id")}
        props = page.get("properties", {})

        for name, prop in props.items():
            row[name.strip()] = extract_property_value(prop)

        records.append(row)

    return pd.DataFrame.from_records(records)


def safe_numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def clean_date_value(value):
    if isinstance(value, dict):
        if "start" in value:
            return value["start"]
        if "date" in value and isinstance(value["date"], dict):
            return value["date"].get("start")
        return None

    if isinstance(value, list):
        if len(value) == 0:
            return None
        return clean_date_value(value[0])

    return value


def safe_dates(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    for col in cols:
        if col in df.columns:
            df[col] = df[col].apply(clean_date_value)
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def get_first_relation_id(value):
    if isinstance(value, list) and len(value) > 0:
        return value[0]
    return None


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    inventory_pages = query_notion_database(INVENTORY_DATABASE_ID)
    sales_pages = query_notion_database(SALES_DATABASE_ID)

    inventory_df = notion_pages_to_dataframe(inventory_pages)
    sales_df = notion_pages_to_dataframe(sales_pages)

    inventory_numeric_cols = [
        "Cost Price",
        "Asking Price",
        "Expected Price",
        "Minimum Price",
        "Retail Price",
        "Quantity In Stock",
        "Quantity Sold",
        "Quantity Available",
        "Total Revenue",
        "Average Sell Price",
        "Average Sell Speed",
        "Actual Profit",
        "ROI",
        "Days on Market",
    ]

    sales_numeric_cols = [
        "Quantity Sold",
        "Sold Price",
        "Sell Speed",
    ]

    inventory_df = safe_numeric(inventory_df, inventory_numeric_cols)
    sales_df = safe_numeric(sales_df, sales_numeric_cols)

    inventory_date_cols = [
        "Listed Vinted",
        "Listed Depop",
        "Listed eBay",
        "All Platforms Listed Date",
    ]

    sales_date_cols = [
        "Date Sold",
        "Listed Vinted",
        "Listed Depop",
        "Listed eBay",
    ]

    inventory_df = safe_dates(inventory_df, inventory_date_cols)
    sales_df = safe_dates(sales_df, sales_date_cols)

    for col in ["Quantity In Stock", "Quantity Sold", "Quantity Available"]:
        if col in inventory_df.columns:
            inventory_df[col] = inventory_df[col].fillna(0)

    for col in ["Quantity Sold", "Sold Price", "Sell Speed"]:
        if col in sales_df.columns:
            sales_df[col] = sales_df[col].fillna(0)

    return inventory_df, sales_df


def build_analytics(inventory_df: pd.DataFrame, sales_df: pd.DataFrame):
    if "Product" not in sales_df.columns:
        raise ValueError("Sales DB is missing the Product relation column.")

    sales_df["Product Page ID"] = sales_df["Product"].apply(get_first_relation_id)

    inventory_cols = [
        "Page ID",
        "SKU",
        "Product Name",
        "Category",
        "Brand",
        "Cost Price",
        "Asking Price",
        "Expected Price",
        "Minimum Price",
    ]

    available_cols = [col for col in inventory_cols if col in inventory_df.columns]

    inventory_lookup = inventory_df[available_cols].copy()
    inventory_lookup = inventory_lookup.rename(columns={"Page ID": "Product Page ID"})

    merged_sales = sales_df.merge(
        inventory_lookup,
        how="left",
        on="Product Page ID",
        suffixes=("", "_inventory"),
    )

    for col in ["Cost Price", "Quantity Sold", "Sold Price"]:
        if col not in merged_sales.columns:
            merged_sales[col] = 0
        merged_sales[col] = pd.to_numeric(merged_sales[col], errors="coerce").fillna(0)

    merged_sales["Supplier Cost"] = merged_sales["Cost Price"] * merged_sales["Quantity Sold"]
    merged_sales["Actual Profit Calc"] = merged_sales["Sold Price"] - merged_sales["Supplier Cost"]

    for col in ["Asking Price", "Expected Price", "Minimum Price", "Cost Price", "Quantity Available"]:
        if col not in inventory_df.columns:
            inventory_df[col] = 0
        inventory_df[col] = pd.to_numeric(inventory_df[col], errors="coerce").fillna(0)

    inventory_df["Potential Profit Remaining"] = (
        (inventory_df["Asking Price"] - inventory_df["Cost Price"])
        * inventory_df["Quantity Available"]
    )

    inventory_df["Expected Profit Remaining"] = (
        (inventory_df["Expected Price"] - inventory_df["Cost Price"])
        * inventory_df["Quantity Available"]
    )

    inventory_df["Minimum Profit Remaining"] = (
        (inventory_df["Minimum Price"] - inventory_df["Cost Price"])
        * inventory_df["Quantity Available"]
    )

    total_revenue = merged_sales["Sold Price"].sum(skipna=True)
    units_sold = merged_sales["Quantity Sold"].sum(skipna=True)
    supplier_cost = merged_sales["Supplier Cost"].sum(skipna=True)
    actual_profit = merged_sales["Actual Profit Calc"].sum(skipna=True)

    avg_sell_price = total_revenue / units_sold if units_sold > 0 else None

    if "Sell Speed" in merged_sales.columns:
        avg_sell_speed = pd.to_numeric(merged_sales["Sell Speed"], errors="coerce").mean(skipna=True)
    else:
        avg_sell_speed = None

    actual_roi = actual_profit / supplier_cost if supplier_cost > 0 else None

    metrics = {
        "Total Revenue": total_revenue,
        "Units Sold": units_sold,
        "Supplier Cost on Sold Items": supplier_cost,
        "Actual Profit": actual_profit,
        "Average Sell Price": avg_sell_price,
        "Average Sell Speed": avg_sell_speed,
        "Actual ROI": actual_roi,
        "Current Stock Units": inventory_df["Quantity Available"].sum(skipna=True),
        "Potential Profit Remaining": inventory_df["Potential Profit Remaining"].sum(skipna=True),
        "Expected Profit Remaining": inventory_df["Expected Profit Remaining"].sum(skipna=True),
        "Minimum Profit Remaining": inventory_df["Minimum Profit Remaining"].sum(skipna=True),
    }

    return inventory_df, sales_df, merged_sales, metrics


st.title("Resale Analytics Dashboard")

if st.button("🔄 Refresh Data"):
    st.rerun()

if not NOTION_TOKEN:
    st.error("Missing NOTION_TOKEN in .env")
    st.stop()

if not INVENTORY_DATABASE_ID:
    st.error("Missing INVENTORY_DATABASE_ID in .env")
    st.stop()

if not SALES_DATABASE_ID:
    st.error("Missing SALES_DATABASE_ID in .env")
    st.stop()

try:
    inventory_df, sales_df = load_data()
    inventory_df, sales_df, merged_sales, metrics = build_analytics(inventory_df, sales_df)
except Exception as e:
    st.error(f"Error loading dashboard: {e}")
    st.exception(e)
    st.stop()


st.subheader("Main Metrics")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Revenue", f"£{metrics['Total Revenue']:.2f}")
c2.metric("Units Sold", f"{metrics['Units Sold']:.0f}")
c3.metric("Supplier Cost on Sold Items", f"£{metrics['Supplier Cost on Sold Items']:.2f}")
c4.metric("Actual Profit", f"£{metrics['Actual Profit']:.2f}")

c5, c6, c7, c8 = st.columns(4)
c5.metric(
    "Average Sell Price",
    f"£{metrics['Average Sell Price']:.2f}" if metrics["Average Sell Price"] is not None else "N/A",
)
c6.metric(
    "Average Sell Speed",
    f"{metrics['Average Sell Speed']:.1f} days"
    if metrics["Average Sell Speed"] is not None and pd.notna(metrics["Average Sell Speed"])
    else "N/A",
)
c7.metric(
    "Actual ROI",
    f"{metrics['Actual ROI']:.2%}" if metrics["Actual ROI"] is not None else "N/A",
)
c8.metric("Current Stock Units", f"{metrics['Current Stock Units']:.0f}")

st.subheader("Remaining Stock Profit Potential")

c9, c10, c11 = st.columns(3)
c9.metric("Potential Profit Remaining", f"£{metrics['Potential Profit Remaining']:.2f}")
c10.metric("Expected Profit Remaining", f"£{metrics['Expected Profit Remaining']:.2f}")
c11.metric("Minimum Profit Remaining", f"£{metrics['Minimum Profit Remaining']:.2f}")


st.subheader("Sales Data Used for Profit")

sales_display_cols = [
    col for col in [
        "Order ID",
        "SKU",
        "Product Name",
        "Platform",
        "Date Sold",
        "Quantity Sold",
        "Sold Price",
        "Cost Price",
        "Supplier Cost",
        "Actual Profit Calc",
        "Sell Speed",
    ] if col in merged_sales.columns
]

st.dataframe(
    merged_sales[sales_display_cols],
    use_container_width=True,
    hide_index=True,
)


st.subheader("Inventory Overview")

inventory_display_cols = [
    col for col in [
        "Product Name",
        "SKU",
        "Brand",
        "Category",
        "Category Type",
        "Jewellery Type",
        "Quantity In Stock",
        "Quantity Sold",
        "Quantity Available",
        "Cost Price",
        "Asking Price",
        "Expected Price",
        "Minimum Price",
        "Potential Profit Remaining",
        "Expected Profit Remaining",
        "Minimum Profit Remaining",
        "Total Revenue",
        "Average Sell Price",
        "Stock Status",
        "Price Action",
    ] if col in inventory_df.columns
]

st.dataframe(
    inventory_df[inventory_display_cols],
    use_container_width=True,
    hide_index=True,
)
