from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict

class DecisionOption(BaseModel):
    name: str
    description: str
    expected_profit: float
    risk_score: float        # 0 to 100
    growth_potential: float  # 0 to 100
    feasibility: float       # 0 to 100
    net_score: float

class ExpectedImpact(BaseModel):
    revenue_impact_range: str
    profit_impact_range: str
    time_to_value: str
    operational_effort: str

class DecisionCreate(BaseModel):
    title: str
    category: str = "strategic"
    description: str
    rationale: str
    evidence: List[Dict[str, Any]]
    assumptions: List[str]
    expected_impact: ExpectedImpact
    options_matrix: List[DecisionOption]
    recommended_option: str
    confidence_score: float = 0.85
    risk_level: str = "medium"

class DecisionReview(BaseModel):
    status: str  # approved, rejected, implemented
    review_notes: Optional[str] = None

class DecisionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    org_id: str
    title: str
    category: str
    description: str
    rationale: str
    evidence: List[Dict[str, Any]]
    assumptions: List[str]
    expected_impact: Dict[str, Any]
    options_matrix: Optional[List[Dict[str, Any]]] = None
    recommended_option: Optional[str] = None
    confidence_score: float
    risk_level: str
    status: str
    reviewed_by_id: Optional[str] = None
    review_notes: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
