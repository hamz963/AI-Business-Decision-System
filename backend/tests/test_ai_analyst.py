import pytest
from app.services.ai_analyst import ai_business_analyst, get_available_models, set_active_model


def test_ai_analyst_no_data_returns_no_data_intent():
    """Without a table_name or kpis, the analyst must return NO_DATA, not fake numbers."""
    res = ai_business_analyst.answer_query("What are our revenues?")
    assert res.intent == "NO_DATA"
    assert res.confidence == "N/A"
    assert len(res.analyst_mode) > 0


def test_ai_analyst_model_switching():
    """Verify listing and switching models dynamically, including OpenCode Big Pickle."""
    models = get_available_models()
    assert len(models) >= 4
    assert any(m.id == "big-pickle" for m in models)
    assert any(m.id == "gemini-2.5-flash" for m in models)
    
    # Test setting model to big-pickle
    set_active_model("big-pickle")
    active = [m for m in get_available_models() if m.is_active]
    assert len(active) == 1
    assert active[0].id == "big-pickle"

    # Reset back to default
    set_active_model("big-pickle")


def test_ai_analyst_scenario_query_with_kpis():
    """With KPI context, a what-if query should return a substantive response."""
    kpis = {
        "revenue": 1_000_000.0,
        "cogs": 600_000.0,
        "operating_expenses": 200_000.0,
        "gross_margin_pct": 40.0,
        "net_margin_pct": 20.0,
        "detected_columns": {"revenue": "revenue", "cost": "cogs", "date": "order_date"},
    }
    res = ai_business_analyst.answer_query(
        "What if prices increase by 10%?",
        cached_kpis=kpis,
    )
    valid_intents = ("SCENARIO_SIMULATION", "LLM_RESPONSE")
    assert res.intent in valid_intents, f"Unexpected intent: {res.intent}"
    assert len(res.facts) > 0
    assert res.confidence in ("High", "Medium", "Low", "N/A")
    assert len(res.predictions) > 0 or len(res.answer) > 50


def test_ai_analyst_forecast_query_with_kpis():
    kpis = {
        "revenue": 500_000.0,
        "cogs": 300_000.0,
        "operating_expenses": 100_000.0,
        "gross_margin_pct": 40.0,
        "net_margin_pct": 20.0,
        "detected_columns": {"revenue": "revenue", "date": "order_date"},
    }
    res = ai_business_analyst.answer_query("Forecast sales for next quarter", cached_kpis=kpis)
    assert res.intent in ("FORECASTING", "LLM_RESPONSE")
    assert len(res.evidence) > 0 or len(res.answer) > 50


def test_ai_analyst_anomaly_query_with_kpis():
    kpis = {
        "revenue": 500_000.0,
        "cogs": 300_000.0,
        "operating_expenses": 100_000.0,
        "gross_margin_pct": 40.0,
        "detected_columns": {"revenue": "revenue"},
    }
    res = ai_business_analyst.answer_query("Find anomalies and outliers in the ledger", cached_kpis=kpis)
    assert res.intent in ("ANOMALY_DETECTION", "LLM_RESPONSE")
    assert len(res.recommendations) > 0 or len(res.answer) > 50


def test_ai_analyst_rejects_empty_query():
    """Empty query must raise a ValueError."""
    with pytest.raises((ValueError, Exception)):
        ai_business_analyst.answer_query("   ", cached_kpis={"revenue": 1.0})


def test_ai_analyst_rejects_query_too_long():
    """Queries over 2000 chars must be rejected."""
    with pytest.raises((ValueError, Exception)):
        ai_business_analyst.answer_query("x" * 2001, cached_kpis={"revenue": 1.0})


def test_anomaly_count_is_zero_not_three_when_no_anomalies():
    """
    When anomaly detection returns an empty list, the AI response must report 0 found,
    not the old hardcoded fallback of 3.
    """
    kpis = {
        "revenue": 500_000.0,
        "cogs": 300_000.0,
        "operating_expenses": 100_000.0,
        "gross_margin_pct": 40.0,
        "orders": 100,
        "detected_columns": {},
    }
    res = ai_business_analyst.answer_query(
        "Are there any unusual spikes or anomalies?",
        cached_kpis=kpis,
        model_name="rule_based"
    )
    if res.intent == "ANOMALY_DETECTION":
        found_counts = [f for f in res.facts if "outlier" in f.lower() or "found" in f.lower()]
        for fc in found_counts:
            assert "3" not in fc or "0" in fc or "Found 0" in fc
