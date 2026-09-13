from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict

class KPIBase(BaseModel):
    name: str
    code: str
    category: str = "financial"
    description: Optional[str] = None
    formula: str
    unit: str = "$"
    target_value: Optional[float] = None
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None

class KPICreate(KPIBase):
    pass

class KPIUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    formula: Optional[str] = None
    unit: Optional[str] = None
    target_value: Optional[float] = None
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None

class KPIOut(KPIBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    org_id: str
    current_value: Optional[float] = None
    previous_value: Optional[float] = None
    change_pct: Optional[float] = None
    status: str = "healthy"
    metadata_info: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

class KPIScorecard(BaseModel):
    total_kpis: int
    healthy_count: int
    warning_count: int
    critical_count: int
    kpis: List[KPIOut]
