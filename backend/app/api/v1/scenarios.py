from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.dataset import Dataset
from app.models.scenario import Scenario
from app.schemas.scenario import ScenarioRunRequest, ScenarioResultOut
from app.services.scenario_simulator import scenario_simulator
from app.services.kpi_calculator import kpi_calculator
from app.services.audit_service import audit_service

router = APIRouter(prefix="/scenarios", tags=["Scenarios & What-If"])

@router.post("/simulate", response_model=ScenarioResultOut)
def run_simulation(
    req: ScenarioRunRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    baseline_rev = 1420000.0
    baseline_cogs = 880000.0
    baseline_opex = 275000.0

    if req.dataset_id:
        ds = db.query(Dataset).filter(
            Dataset.id == req.dataset_id,
            Dataset.org_id == current_user.org_id
        ).first()
        if ds:
            try:
                metrics = kpi_calculator.calculate_standard_metrics(ds.table_name)
                baseline_rev = metrics.get("revenue", baseline_rev)
                baseline_cogs = metrics.get("cogs", baseline_cogs)
                baseline_opex = metrics.get("operating_expenses", baseline_opex)
            except Exception:
                pass

    res = scenario_simulator.simulate(
        baseline_revenue=baseline_rev,
        baseline_cogs=baseline_cogs,
        baseline_opex=baseline_opex,
        params=req.parameters
    )
    res.name = req.name or "What-If Simulation"
    return res

@router.post("/save", response_model=ScenarioResultOut)
def save_scenario(
    req: ScenarioRunRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    sim_res = run_simulation(req, db, current_user)

    scenario = Scenario(
        org_id=current_user.org_id,
        created_by_id=current_user.id,
        name=req.name or "Saved What-If Scenario",
        description=req.description,
        dataset_id=req.dataset_id,
        parameters=req.parameters.dict(),
        results=sim_res.dict(),
        risk_score=sim_res.risk_score,
        risk_assessment=sim_res.risk_assessment
    )
    db.add(scenario)
    db.commit()
    db.refresh(scenario)

    audit_service.log_action(
        db=db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        action="SCENARIO_SAVED",
        entity_type="scenario",
        entity_id=scenario.id,
        details={"name": scenario.name, "risk_score": sim_res.risk_score}
    )

    sim_res.id = scenario.id
    return sim_res

@router.get("/", response_model=List[ScenarioResultOut])
def list_saved_scenarios(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    scenarios = db.query(Scenario).filter(
        Scenario.org_id == current_user.org_id
    ).order_by(Scenario.created_at.desc()).all()

    out = []
    for s in scenarios:
        res_data = s.results
        res_data["id"] = s.id
        out.append(ScenarioResultOut(**res_data))
    return out
