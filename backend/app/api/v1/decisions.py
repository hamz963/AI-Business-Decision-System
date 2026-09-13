from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.dataset import Dataset
from app.models.decision import Decision
from app.schemas.decision import DecisionCreate, DecisionReview, DecisionOut
from app.services.decision_engine import decision_engine
from app.services.kpi_calculator import kpi_calculator
from app.services.audit_service import audit_service

router = APIRouter(prefix="/decisions", tags=["Decisions & Recommendations"])

@router.get("/", response_model=List[DecisionOut])
def list_decisions(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Decision).filter(Decision.org_id == current_user.org_id)
    if status:
        query = query.filter(Decision.status == status)
    decisions = query.order_by(Decision.created_at.desc()).all()

    # If empty, seed initial strategic proposals
    if not decisions:
        seed = [
            {
                "title": "Optimized Tiered Pricing Realization",
                "category": "pricing",
                "description": "Enforce a 4.5% list price uplift on inelastic catalog items while restricting field discounting to max 10%.",
                "rationale": "Gross margin has contracted by 180 bps over recent quarters due to material inflation. Selective price adjustment offsets this without impacting core enterprise accounts.",
                "evidence": [
                    {"metric": "Gross Margin Contraction", "value": "-1.8% over 2 quarters"},
                    {"metric": "Price Elasticity", "value": "-1.15 (Inelastic Catalog Segment)"}
                ],
                "assumptions": ["Customer churn will remain under 1.5% across revised price bands."],
                "expected_impact": {
                    "revenue_impact_range": "+$48,000 to +$72,000",
                    "profit_impact_range": "+$42,000 net profit",
                    "time_to_value": "45 days",
                    "operational_effort": "Low"
                },
                "options_matrix": [
                    {"name": "Option A: 4.5% Selective Uplift", "expected_profit": 85.0, "risk_score": 30.0, "growth_potential": 70.0, "feasibility": 90.0, "net_score": 83.2, "description": "Targeted uplift on non-contract accounts"},
                    {"name": "Option B: 8% Broad Uplift", "expected_profit": 92.0, "risk_score": 75.0, "growth_potential": 45.0, "feasibility": 80.0, "net_score": 63.4, "description": "Across-the-board hike"},
                    {"name": "Option C: Status Quo", "expected_profit": 40.0, "risk_score": 25.0, "growth_potential": 50.0, "feasibility": 100.0, "net_score": 58.7, "description": "No price change"}
                ],
                "recommended_option": "Option A: 4.5% Selective Uplift",
                "confidence_score": 0.89,
                "risk_level": "medium",
                "status": "proposed"
            },
            {
                "title": "Procurement Safety Stock Optimization",
                "category": "inventory",
                "description": "Increase safety buffer on high-velocity components from 14 days to 28 days to insulate against supplier delays.",
                "rationale": "Supplier lead time variability increased by 35% in Q3, elevating stockout probability during peak demand.",
                "evidence": [
                    {"metric": "Supplier Lead Time Variance", "value": "+35% QoQ"},
                    {"metric": "Estimated Stockout Cost", "value": "$85,000 per occurrence"}
                ],
                "assumptions": ["Holding cost increases by approximately $3,500 monthly."],
                "expected_impact": {
                    "revenue_impact_range": "Protects ~$120,000 in at-risk revenue",
                    "profit_impact_range": "-$10,500 working capital holding cost",
                    "time_to_value": "Immediate",
                    "operational_effort": "Medium"
                },
                "options_matrix": [
                    {"name": "Option A: 28-day Safety Stock", "expected_profit": 78.0, "risk_score": 22.0, "growth_potential": 60.0, "feasibility": 92.0, "net_score": 78.2, "description": "Standardized safety stock expansion"},
                    {"name": "Option B: Secondary Supplier Onboarding", "expected_profit": 80.0, "risk_score": 45.0, "growth_potential": 65.0, "feasibility": 55.0, "net_score": 65.7, "description": "Dual-sourcing strategy"},
                    {"name": "Option C: Just-In-Time (Maintain 14 days)", "expected_profit": 55.0, "risk_score": 82.0, "growth_potential": 50.0, "feasibility": 100.0, "net_score": 53.7, "description": "Accept stockout vulnerability"}
                ],
                "recommended_option": "Option A: 28-day Safety Stock",
                "confidence_score": 0.92,
                "risk_level": "low",
                "status": "approved"
            }
        ]
        created = []
        for s in seed:
            dec = Decision(org_id=current_user.org_id, **s)
            db.add(dec)
            created.append(dec)
        db.commit()
        for d in created:
            db.refresh(d)
        return created
    return decisions

@router.post("/", response_model=DecisionOut)
def create_decision(
    dec_in: DecisionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dec = Decision(
        org_id=current_user.org_id,
        title=dec_in.title,
        category=dec_in.category,
        description=dec_in.description,
        rationale=dec_in.rationale,
        evidence=dec_in.evidence,
        assumptions=dec_in.assumptions,
        expected_impact=dec_in.expected_impact.dict(),
        options_matrix=[o.dict() for o in dec_in.options_matrix],
        recommended_option=dec_in.recommended_option,
        confidence_score=dec_in.confidence_score,
        risk_level=dec_in.risk_level,
        status="proposed"
    )
    db.add(dec)
    db.commit()
    db.refresh(dec)

    audit_service.log_action(
        db=db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        action="DECISION_PROPOSED",
        entity_type="decision",
        entity_id=dec.id,
        details={"title": dec.title, "recommended_option": dec.recommended_option}
    )

    return dec

@router.post("/{decision_id}/review", response_model=DecisionOut)
def review_decision(
    decision_id: str,
    review_in: DecisionReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    dec = db.query(Decision).filter(
        Decision.id == decision_id,
        Decision.org_id == current_user.org_id
    ).first()
    if not dec:
        raise HTTPException(status_code=404, detail="Decision not found.")

    dec.status = review_in.status
    dec.review_notes = review_in.review_notes
    dec.reviewed_by_id = current_user.id
    dec.reviewed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(dec)

    audit_service.log_action(
        db=db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        action=f"DECISION_{review_in.status.upper()}",
        entity_type="decision",
        entity_id=dec.id,
        details={"status": dec.status, "notes": review_in.review_notes}
    )

    return dec
