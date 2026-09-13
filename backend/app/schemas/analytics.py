from typing import Optional, Dict, Any, List
from pydantic import BaseModel

class PeriodComparison(BaseModel):
    metric_name: str
    current_value: float
    previous_value: float
    absolute_change: float
    percentage_change: float
    trend: str  # up, down, flat
    is_positive: bool

class BreakdownItem(BaseModel):
    category: str
    revenue: float
    cost: float
    profit: float
    margin_pct: float
    volume: int
    share_pct: float

class ForecastPoint(BaseModel):
    date: str
    actual: Optional[float] = None
    predicted: float
    lower_bound: float
    upper_bound: float

class ForecastResult(BaseModel):
    metric: str
    model_name: str
    validation_mape: float
    validation_rmse: float
    history: List[ForecastPoint]
    forecast: List[ForecastPoint]
    summary_growth_pct: float
    assumptions: List[str]

class AnomalyItem(BaseModel):
    id: str
    date: str
    entity: str
    field: str
    observed_value: float
    expected_value: float
    deviation_z_score: float
    severity: str  # low, medium, high, critical
    details: str

class ExecutiveBriefing(BaseModel):
    generated_at: str
    headline: str
    summary: str
    key_drivers: List[str]
    forecast_outlook: str
    critical_risks: List[str]
    strategic_recommendations: List[Dict[str, Any]]
    confidence: str
    evidence_citations: List[Dict[str, Any]]
