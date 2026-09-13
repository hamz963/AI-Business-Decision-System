from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class ScenarioParams(BaseModel):
    price_change_pct: float = Field(default=0.0, description="Percentage change in selling price (-50 to +100)")
    marketing_spend_pct: float = Field(default=0.0, description="Percentage change in marketing budget")
    operating_cost_pct: float = Field(default=0.0, description="Percentage change in operational/overheads")
    headcount_change_pct: float = Field(default=0.0, description="Percentage change in staffing/labor cost")
    discount_rate_pct: float = Field(default=0.0, description="Change in average discount given")
    assumed_elasticity: float = Field(default=-1.2, description="Price elasticity of demand coefficient")

class ScenarioMetrics(BaseModel):
    revenue: float
    cogs: float
    gross_profit: float
    gross_margin_pct: float
    operating_expenses: float
    net_profit: float
    net_margin_pct: float
    projected_volume: float
    break_even_point: float

class ScenarioDeltas(BaseModel):
    revenue_delta: float
    revenue_delta_pct: float
    net_profit_delta: float
    net_profit_delta_pct: float
    margin_delta_basis_pts: float

class ScenarioRunRequest(BaseModel):
    dataset_id: Optional[str] = None
    parameters: ScenarioParams
    name: Optional[str] = "What-If Simulation"
    description: Optional[str] = None

class ScenarioResultOut(BaseModel):
    id: Optional[str] = None
    name: str
    parameters: ScenarioParams
    baseline: ScenarioMetrics
    projected: ScenarioMetrics
    deltas: ScenarioDeltas
    risk_score: float
    risk_assessment: Dict[str, Any]
    tradeoff_summary: str
    recommendation: str
