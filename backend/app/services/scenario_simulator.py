from typing import Dict, Any
from app.schemas.scenario import (
    ScenarioParams, ScenarioMetrics, ScenarioDeltas, ScenarioResultOut
)

class ScenarioSimulator:
    """
    Scenario & What-If Simulation Engine.
    Simulates pricing elasticity, marketing budget scaling, cost shocks,
    and headcount variations to calculate projected P&L with explicit
    trade-off and risk scoring.
    """

    @staticmethod
    def simulate(
        baseline_revenue: float,
        baseline_cogs: float,
        baseline_opex: float,
        params: ScenarioParams
    ) -> ScenarioResultOut:
        # Prevent division by zero
        base_rev = max(1000.0, baseline_revenue)
        base_cogs = max(500.0, baseline_cogs)
        base_opex = max(500.0, baseline_opex)

        base_gross_profit = base_rev - base_cogs
        base_gross_margin_pct = (base_gross_profit / base_rev) * 100.0
        base_net_profit = base_gross_profit - base_opex
        base_net_margin_pct = (base_net_profit / base_rev) * 100.0
        base_volume = 10000.0  # normalized index unit volume

        # 1. Price Elasticity & Volume Impact
        # ΔQ% = elasticity * ΔP%
        # If price increases by 10% and elasticity is -1.2, volume drops by 12%
        price_factor = 1.0 + (params.price_change_pct / 100.0)
        volume_delta_pct = params.assumed_elasticity * params.price_change_pct
        volume_factor = max(0.1, 1.0 + (volume_delta_pct / 100.0))

        # 2. Marketing Spend Impact
        # Logarithmic diminishing returns: each +10% marketing yields +3% volume boost
        mkt_volume_boost_pct = (params.marketing_spend_pct * 0.30)
        final_volume_factor = max(0.1, volume_factor * (1.0 + mkt_volume_boost_pct / 100.0))

        # 3. Discount Impact
        # Discount directly reduces effective price realization
        effective_price_factor = price_factor * (1.0 - (params.discount_rate_pct / 100.0))

        # Projected Revenue
        proj_revenue = base_rev * effective_price_factor * final_volume_factor

        # Projected COGS (varies with unit volume + inflation/cost shift)
        # 80% of COGS is variable with volume; 20% fixed
        variable_cogs_ratio = 0.80
        fixed_cogs = base_cogs * (1 - variable_cogs_ratio)
        variable_cogs = base_cogs * variable_cogs_ratio * final_volume_factor
        proj_cogs = fixed_cogs + variable_cogs

        # Projected Operating Expenses (adjusted for marketing, headcount, opex shifts)
        # Assume base opex has 30% marketing, 40% labor/headcount, 30% general overhead
        mkt_portion = base_opex * 0.30 * (1.0 + params.marketing_spend_pct / 100.0)
        labor_portion = base_opex * 0.40 * (1.0 + params.headcount_change_pct / 100.0)
        overhead_portion = base_opex * 0.30 * (1.0 + params.operating_cost_pct / 100.0)
        proj_opex = max(100.0, mkt_portion + labor_portion + overhead_portion)

        # Projected Profits
        proj_gross_profit = proj_revenue - proj_cogs
        proj_gross_margin_pct = (proj_gross_profit / proj_revenue * 100.0) if proj_revenue > 0 else 0.0
        proj_net_profit = proj_gross_profit - proj_opex
        proj_net_margin_pct = (proj_net_profit / proj_revenue * 100.0) if proj_revenue > 0 else 0.0
        proj_volume = base_volume * final_volume_factor

        # Break-Even Point: Fixed Costs / Contribution Margin Ratio
        total_fixed_costs = fixed_cogs + (overhead_portion * 0.7)
        contrib_margin_ratio = (proj_revenue - variable_cogs) / proj_revenue if proj_revenue > 0 else 0.1
        break_even_point = total_fixed_costs / max(0.05, contrib_margin_ratio)

        # Calculate Deltas
        rev_delta = proj_revenue - base_rev
        rev_delta_pct = (rev_delta / base_rev) * 100.0
        net_profit_delta = proj_net_profit - base_net_profit
        net_profit_delta_pct = (net_profit_delta / abs(base_net_profit) * 100.0) if base_net_profit != 0 else 0.0
        margin_delta_basis_pts = (proj_net_margin_pct - base_net_margin_pct) * 100.0

        # Calculate Risk Score (0 - 100)
        risk_components = []
        risk_score = 15.0  # baseline operational risk

        if params.price_change_pct > 15.0:
            risk_score += 25.0
            risk_components.append("Aggressive price hike may trigger accelerated customer churn and competitive substitution.")
        elif params.price_change_pct < -15.0:
            risk_score += 20.0
            risk_components.append("Substantial price discounting erodes brand equity and contribution margin.")

        if params.marketing_spend_pct > 30.0:
            risk_score += 20.0
            risk_components.append("Rapid marketing scale-up risks CAC inflation and diminishing marginal returns.")

        if params.headcount_change_pct < -10.0:
            risk_score += 25.0
            risk_components.append("Deep headcount reduction poses severe operational capacity and service quality risks.")

        if proj_net_profit < 0:
            risk_score += 35.0
            risk_components.append("Scenario leads to negative operating profit / burn rate.")

        risk_score = min(100.0, max(5.0, risk_score))

        # Synthesize Tradeoff Summary & Actionable Recommendation
        if net_profit_delta > 0:
            tradeoff = f"Net profit expands by ${net_profit_delta:,.0f} ({net_profit_delta_pct:+.1f}%), accompanied by a {volume_delta_pct:+.1f}% shift in demand volume."
            if risk_score <= 40:
                rec = "Favorable scenario: High profit capture with manageable operational risk. Proceed to staged execution."
            else:
                rec = "Profitable but high risk: Mitigate customer friction before rolling out full price/budget adjustments."
        else:
            tradeoff = f"Net profit contracts by ${abs(net_profit_delta):,.0f} ({net_profit_delta_pct:+.1f}%). Cost additions outpace incremental volume."
            rec = "Unfavorable scenario: Rebalance parameters to protect contribution margin before consideration."

        return ScenarioResultOut(
            name="What-If Simulation",
            parameters=params,
            baseline=ScenarioMetrics(
                revenue=round(base_rev, 2),
                cogs=round(base_cogs, 2),
                gross_profit=round(base_gross_profit, 2),
                gross_margin_pct=round(base_gross_margin_pct, 2),
                operating_expenses=round(base_opex, 2),
                net_profit=round(base_net_profit, 2),
                net_margin_pct=round(base_net_margin_pct, 2),
                projected_volume=round(base_volume, 0),
                break_even_point=round(break_even_point, 2)
            ),
            projected=ScenarioMetrics(
                revenue=round(proj_revenue, 2),
                cogs=round(proj_cogs, 2),
                gross_profit=round(proj_gross_profit, 2),
                gross_margin_pct=round(proj_gross_margin_pct, 2),
                operating_expenses=round(proj_opex, 2),
                net_profit=round(proj_net_profit, 2),
                net_margin_pct=round(proj_net_margin_pct, 2),
                projected_volume=round(proj_volume, 0),
                break_even_point=round(break_even_point, 2)
            ),
            deltas=ScenarioDeltas(
                revenue_delta=round(rev_delta, 2),
                revenue_delta_pct=round(rev_delta_pct, 2),
                net_profit_delta=round(net_profit_delta, 2),
                net_profit_delta_pct=round(net_profit_delta_pct, 2),
                margin_delta_basis_pts=round(margin_delta_basis_pts, 1)
            ),
            risk_score=round(risk_score, 1),
            risk_assessment={
                "level": "low" if risk_score < 30 else ("medium" if risk_score < 60 else "high"),
                "factors": risk_components if risk_components else ["Operational parameters remain within historical tolerances."]
            },
            tradeoff_summary=tradeoff,
            recommendation=rec
        )

scenario_simulator = ScenarioSimulator()
