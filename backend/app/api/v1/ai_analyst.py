import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.dataset import Dataset
from app.models.user import User
from app.schemas.ai import (
    AIQueryRequest,
    AIQueryResponse,
    ModelOption,
    SetModelRequest,
)
from app.services.ai_analyst import (
    ai_business_analyst,
    get_available_models,
    set_active_model,
    get_active_model,
)
from app.services.audit_service import audit_service
from app.services.kpi_calculator import kpi_calculator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Business Analyst"])


@router.get("/models", response_model=List[ModelOption])
def list_models(current_user: User = Depends(get_current_user)):
    """List all available free-tier and offline AI models with active status."""
    return get_available_models()


@router.post("/models/select")
def select_model(
    req: SetModelRequest,
    current_user: User = Depends(get_current_user),
):
    """Dynamically switch the active AI model for decisions and analysis."""
    try:
        active = set_active_model(req.model_id)
        return {"status": "success", "active_model": active}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/query", response_model=AIQueryResponse)
def query_ai_analyst(
    req: AIQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    table_name = None
    cached_kpis = None

    if req.dataset_id:
        ds = db.query(Dataset).filter(
            Dataset.id == req.dataset_id,
            Dataset.org_id == current_user.org_id,
        ).first()
        if ds:
            table_name = ds.table_name
        else:
            raise HTTPException(status_code=404, detail="Dataset not found.")
    else:
        latest_ds = (
            db.query(Dataset)
            .filter(Dataset.org_id == current_user.org_id)
            .order_by(Dataset.created_at.desc())
            .first()
        )
        if latest_ds:
            table_name = latest_ds.table_name

    if table_name:
        try:
            cached_kpis = kpi_calculator.calculate_standard_metrics(table_name)
        except Exception:
            logger.exception("KPI pre-fetch failed for table '%s'", table_name)

    try:
        response = ai_business_analyst.answer_query(
            query=req.query,
            table_name=table_name,
            cached_kpis=cached_kpis,
            model_name=req.model_name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    audit_service.log_action(
        db=db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        action="AI_ANALYST_QUERY",
        entity_type="ai_query",
        details={
            "query": req.query,
            "intent": response.intent,
            "confidence": response.confidence,
            "analyst_mode": response.analyst_mode,
        },
    )

    return response
