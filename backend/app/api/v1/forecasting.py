from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.dataset import Dataset
from app.schemas.analytics import ForecastResult, AnomalyItem
from app.services.forecasting import forecasting_engine
from app.services.anomaly_detector import anomaly_detector
from app.services.kpi_calculator import kpi_calculator

router = APIRouter(prefix="/analytics", tags=["Analytics & Forecasting"])

@router.get("/forecast", response_model=ForecastResult)
def get_forecast(
    dataset_id: Optional[str] = None,
    periods_ahead: int = Query(default=6, ge=1, le=24),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Dataset).filter(Dataset.org_id == current_user.org_id)
    if dataset_id:
        dataset = query.filter(Dataset.id == dataset_id).first()
    else:
        dataset = query.order_by(Dataset.created_at.desc()).first()

    if not dataset:
        raise HTTPException(status_code=404, detail="No dataset found to forecast.")

    metrics = kpi_calculator.calculate_standard_metrics(dataset.table_name)
    date_col = metrics.get("detected_columns", {}).get("date")
    rev_col = metrics.get("detected_columns", {}).get("revenue")

    if not date_col or not rev_col:
        raise HTTPException(
            status_code=400,
            detail="Dataset requires identifiable date and numeric metric columns for forecasting."
        )

    try:
        res = forecasting_engine.forecast_metric(
            table_name=dataset.table_name,
            date_col=date_col,
            metric_col=rev_col,
            periods_ahead=periods_ahead
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Forecasting error: {str(e)}")

@router.get("/anomalies", response_model=List[AnomalyItem])
def get_anomalies(
    dataset_id: Optional[str] = None,
    z_threshold: float = Query(default=2.5, ge=1.5, le=5.0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Dataset).filter(Dataset.org_id == current_user.org_id)
    if dataset_id:
        dataset = query.filter(Dataset.id == dataset_id).first()
    else:
        dataset = query.order_by(Dataset.created_at.desc()).first()

    if not dataset:
        return []

    metrics = kpi_calculator.calculate_standard_metrics(dataset.table_name)
    rev_col = metrics.get("detected_columns", {}).get("revenue")
    date_col = metrics.get("detected_columns", {}).get("date")
    order_col = metrics.get("detected_columns", {}).get("order")

    if not rev_col:
        return []

    return anomaly_detector.detect_anomalies(
        table_name=dataset.table_name,
        metric_col=rev_col,
        entity_col=order_col,
        date_col=date_col,
        z_threshold=z_threshold
    )
