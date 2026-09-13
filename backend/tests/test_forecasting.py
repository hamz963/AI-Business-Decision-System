import pytest
import pandas as pd
from app.services.duckdb_engine import duckdb_engine
from app.services.forecasting import forecasting_engine
from app.services.anomaly_detector import anomaly_detector

def test_forecasting_engine():
    # 12 monthly periods
    dates = pd.date_range("2024-01-01", periods=12, freq="MS").strftime("%Y-%m-%d").tolist()
    # Upward trend: 100, 110, 120, ...
    revs = [100.0 + i * 10.0 for i in range(12)]
    df = pd.DataFrame({"trans_date": dates, "sales": revs})
    
    table_name = "test_forecast_tbl"
    duckdb_engine.register_dataframe(table_name, df)

    res = forecasting_engine.forecast_metric(table_name, "trans_date", "sales", periods_ahead=4)
    assert len(res.history) == 12
    assert len(res.forecast) == 4
    assert res.validation_mape >= 0.0
    assert res.validation_rmse >= 0.0
    # Predictions should be positive
    for pt in res.forecast:
        assert pt.predicted > 0.0
        assert pt.lower_bound <= pt.predicted <= pt.upper_bound

def test_anomaly_detector():
    # Normal distribution with 2 clear outliers
    values = [100.0] * 20 + [5000.0]  # 5000 is a clear outlier
    df = pd.DataFrame({
        "order_id": [f"ORD-{i}" for i in range(len(values))],
        "amount": values,
        "date": ["2025-01-01"] * len(values)
    })
    table_name = "test_anomaly_tbl"
    duckdb_engine.register_dataframe(table_name, df)

    anomalies = anomaly_detector.detect_anomalies(table_name, "amount", entity_col="order_id", date_col="date")
    assert len(anomalies) >= 1
    assert anomalies[0].observed_value == 5000.0
    assert anomalies[0].severity in ["high", "critical"]
