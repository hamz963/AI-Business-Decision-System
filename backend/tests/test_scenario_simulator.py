import pytest
from app.services.scenario_simulator import scenario_simulator
from app.schemas.scenario import ScenarioParams


def test_scenario_price_increase():
    """
    Baseline: $1,000,000 revenue, $600,000 COGS, $200,000 OPEX.
    With elasticity=-1.0 and +10% price:
      - Volume factor = 1 + (-1.0 * 10/100) = 0.9
      - Revenue = 1,000,000 * 1.10 * 0.90 = 990,000
    """
    params = ScenarioParams(
        price_change_pct=10.0,
        marketing_spend_pct=0.0,
        operating_cost_pct=0.0,
        assumed_elasticity=-1.0,
    )

    res = scenario_simulator.simulate(
        baseline_revenue=1_000_000.0,
        baseline_cogs=600_000.0,
        baseline_opex=200_000.0,
        params=params,
    )

    # Use pytest.approx for all floating-point comparisons
    assert res.baseline.revenue == pytest.approx(1_000_000.0)
    assert res.baseline.gross_profit == pytest.approx(400_000.0)
    assert res.baseline.net_profit == pytest.approx(200_000.0)
    assert res.projected.revenue == pytest.approx(990_000.0, rel=1e-4)
    assert res.risk_score >= 5.0
    assert "Simulation" in res.name


def test_scenario_cost_reduction():
    """Operating cost reduction should always improve net profit."""
    params = ScenarioParams(
        price_change_pct=0.0,
        marketing_spend_pct=0.0,
        operating_cost_pct=-10.0,
    )

    res = scenario_simulator.simulate(
        baseline_revenue=1_000_000.0,
        baseline_cogs=600_000.0,
        baseline_opex=200_000.0,
        params=params,
    )

    assert res.projected.net_profit > res.baseline.net_profit
    assert res.deltas.net_profit_delta > 0


def test_scenario_extreme_discount_stays_bounded():
    """Even 100% discount should not produce negative risk score or revenue."""
    params = ScenarioParams(
        price_change_pct=-50.0,
        marketing_spend_pct=0.0,
        operating_cost_pct=0.0,
    )

    res = scenario_simulator.simulate(
        baseline_revenue=1_000_000.0,
        baseline_cogs=600_000.0,
        baseline_opex=200_000.0,
        params=params,
    )

    assert res.projected.revenue >= 0
    assert 5.0 <= res.risk_score <= 100.0
