import pandas as pd


def _number(frame: pd.DataFrame, column: str) -> pd.Series:
    if column not in frame:
        return pd.Series(0.0, index=frame.index, dtype=float)
    return pd.to_numeric(frame[column], errors="coerce").fillna(0.0)


def dashboard_metrics(inventory: pd.DataFrame, sales: pd.DataFrame) -> dict[str, float]:
    quantities_sold = _number(sales, "Quantity Sold")
    sold_prices = _number(sales, "Sold Price")
    revenue = float((quantities_sold * sold_prices).sum())

    if "Cost Price" in sales:
        sold_cost = float((_number(sales, "Cost Price") * quantities_sold).sum())
    else:
        sold_cost = float(_number(sales, "Total Cost").sum())

    actual_profit = revenue - sold_cost
    actual_roi = (actual_profit / sold_cost * 100) if sold_cost else 0.0
    sell_speed = _number(sales, "Sell Speed")
    positive_speed = sell_speed[sell_speed > 0]

    available = _number(inventory, "Quantity Available")
    cost = _number(inventory, "Cost Price")

    return {
        "total_revenue": revenue,
        "units_sold": float(quantities_sold.sum()),
        "sold_inventory_cost": sold_cost,
        "actual_profit": actual_profit,
        "actual_roi": actual_roi,
        "average_sell_speed": float(positive_speed.mean()) if not positive_speed.empty else 0.0,
        "potential_profit": float(((_number(inventory, "Retail Price") - cost) * available).sum()),
        "expected_profit": float(((_number(inventory, "Expected Price") - cost) * available).sum()),
        "minimum_profit": float(((_number(inventory, "Minimum Price") - cost) * available).sum()),
    }
