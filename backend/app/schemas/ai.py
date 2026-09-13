from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ModelOption(BaseModel):
    id: str
    name: str
    provider: str
    description: str
    free_tier: bool = True
    is_active: bool = False


class SetModelRequest(BaseModel):
    model_id: str


class AIQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000, description="Business question to answer")
    dataset_id: Optional[str] = None
    context_period: Optional[str] = "last_12_months"
    model_name: Optional[str] = None


class AIToolCall(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    output: Any


class AIQueryResponse(BaseModel):
    query: str
    intent: str
    answer: str
    facts: List[str]
    inferences: List[str]
    predictions: List[str]
    assumptions: List[str]
    recommendations: List[str]
    evidence: List[Dict[str, Any]]
    confidence: str  # High, Medium, Low, N/A
    tools_executed: List[AIToolCall] = []
    suggested_actions: List[str] = []
    analyst_mode: str = "gemini-2.5-flash"
