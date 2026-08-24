from typing import Any

import pandas as pd
from notion_client import Client

from src.config import Settings


def _plain_text(items: list[dict[str, Any]]) -> str:
    return "".join(item.get("plain_text", "") for item in items)


def property_value(prop: dict[str, Any]) -> Any:
    kind = prop.get("type")
    value = prop.get(kind) if kind else None
    if kind in {"title", "rich_text"}:
        return _plain_text(value or [])
    if kind in {"number", "checkbox", "url", "email", "phone_number"}:
        return value
    if kind in {"select", "status"}:
        return value.get("name") if value else None
    if kind == "multi_select":
        return ", ".join(item["name"] for item in value or [])
    if kind == "date":
        return value.get("start") if value else None
    if kind == "formula":
        formula_type = value.get("type") if value else None
        return value.get(formula_type) if formula_type else None
    if kind == "rollup":
        rollup_type = value.get("type") if value else None
        return value.get(rollup_type) if rollup_type else None
    if kind == "relation":
        return [item["id"] for item in value or []]
    return value


class NotionRepository:
    def __init__(self, settings: Settings):
        self.client = Client(auth=settings.notion_token)
        self.inventory_database_id = settings.inventory_database_id
        self.sales_database_id = settings.sales_database_id

    def _query_all(self, database_id: str) -> pd.DataFrame:
        records: list[dict[str, Any]] = []
        cursor = None
        while True:
            payload = {"database_id": database_id}
            if cursor:
                payload["start_cursor"] = cursor
            response = self.client.databases.query(**payload)
            for page in response["results"]:
                record = {name: property_value(prop) for name, prop in page["properties"].items()}
                record["Notion Page ID"] = page["id"]
                records.append(record)
            if not response.get("has_more"):
                break
            cursor = response.get("next_cursor")
        return pd.DataFrame(records)

    def fetch_inventory(self) -> pd.DataFrame:
        return self._query_all(self.inventory_database_id)

    def fetch_sales(self) -> pd.DataFrame:
        return self._query_all(self.sales_database_id)
