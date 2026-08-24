import pandas as pd

from src.metrics import dashboard_metrics


def test_metrics_use_quantity_sold_for_revenue_and_cost():
    inventory = pd.DataFrame({
        "Quantity Available": [2], "Cost Price": [10], "Retail Price": [40],
        "Expected Price": [30], "Minimum Price": [20],
    })
    sales = pd.DataFrame({
        "Quantity Sold": [2], "Sold Price": [25], "Cost Price": [10], "Sell Speed": [7],
    })
    result = dashboard_metrics(inventory, sales)
    assert result["total_revenue"] == 50
    assert result["sold_inventory_cost"] == 20
    assert result["actual_profit"] == 30
    assert result["actual_roi"] == 150
    assert result["expected_profit"] == 40


def test_empty_frames_return_zero_metrics():
    result = dashboard_metrics(pd.DataFrame(), pd.DataFrame())
    assert all(value == 0 for value in result.values())
