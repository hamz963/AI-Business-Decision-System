import pandas as pd
from app.services.data_quality import data_quality_engine

def test_data_quality_perfect_data():
    df = pd.DataFrame({
        "order_id": ["ORD-1", "ORD-2", "ORD-3", "ORD-4"],
        "revenue": [100.0, 250.0, 300.0, 150.0],
        "category": ["A", "B", "A", "B"]
    })
    score, report = data_quality_engine.analyze_dataframe(df)
    assert score >= 95.0
    assert report["status"] == "excellent"
    assert len(report["issues"]) == 0

def test_data_quality_with_nulls_and_duplicates():
    df = pd.DataFrame({
        "order_id": ["ORD-1", "ORD-1", "ORD-2", None],
        "revenue": [100.0, 100.0, None, -50.0]
    })
    score, report = data_quality_engine.analyze_dataframe(df)
    assert score < 85.0
    assert len(report["issues"]) > 0 or len(report["warnings"]) > 0
