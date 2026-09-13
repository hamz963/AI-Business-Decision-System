from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

class ColumnMeta(BaseModel):
    name: str
    inferred_type: str  # numeric, categorical, datetime, text, boolean
    null_count: int
    null_percentage: float
    unique_count: int
    sample_values: List[Any] = []

class QualityMetric(BaseModel):
    dimension: str  # completeness, uniqueness, validity, freshness
    score: float
    details: str

class DatasetQualityReport(BaseModel):
    overall_score: float
    status: str  # excellent, good, fair, poor
    row_count: int
    column_count: int
    columns: List[ColumnMeta]
    quality_metrics: List[QualityMetric]
    issues: List[str]
    warnings: List[str]

class DatasetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    org_id: str
    name: str
    description: Optional[str] = None
    source_type: str
    table_name: str
    row_count: int
    column_count: int
    quality_score: float
    quality_report: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

class DatasetPreview(BaseModel):
    dataset: DatasetOut
    columns: List[str]
    rows: List[Dict[str, Any]]
