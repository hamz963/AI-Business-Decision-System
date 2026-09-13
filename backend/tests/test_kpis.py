import pytest
import pandas as pd
from app.services.duckdb_engine import duckdb_engine
from app.services.kpi_calculator import kpi_calculator

def test_kpi_calculator_metrics():
    # Register test dataframe in DuckDB
    df = pd.DataFrame({
        "order_id": ["O-1", "O-2", "O-3", "O-4"],
        "customer_id": ["C-1", "C-2", "C-1", "C-3"],
        "revenue": [1000.0, 2000.0, 1500.0, 500.0],  # Total = 5000.0
        "cogs": [600.0, 1200.0, 900.0, 300.0],       # Total = 3000.0
        "order_date": ["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-04"]
    })
    table_name = "test_kpi_tbl"
    duckdb_engine.register_dataframe(table_name, df)

    res = kpi_calculator.calculate_standard_metrics(table_name)
    assert res["revenue"] == 5000.0
    assert res["cogs"] == 3000.0
    assert res["gross_profit"] == 2000.0
    assert res["gross_margin_pct"] == 40.0
    assert res["orders"] == 4
    assert res["customers"] == 3
    assert res["average_order_value"] == 1250.0

def test_category_breakdown():
    df = pd.DataFrame({
        "category": ["Enterprise", "Enterprise", "Consumer", "Consumer"],
        "revenue": [3000.0, 2000.0, 1000.0, 500.0]
    })
    table_name = "test_cat_tbl"
    duckdb_engine.register_dataframe(table_name, df)

    breakdown = kpi_calculator.calculate_category_breakdown(table_name, "category", "revenue")
    assert len(breakdown) == 2
    assert breakdown[0]["category"] == "Enterprise"
    assert breakdown[0]["revenue"] == 5000.0
    assert breakdown[0]["share_pct"] == pytest.approx(76.9, 0.1)
