from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.datasets import router as datasets_router
from app.api.v1.kpis import router as kpis_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.forecasting import router as forecasting_router
from app.api.v1.scenarios import router as scenarios_router
from app.api.v1.decisions import router as decisions_router
from app.api.v1.ai_analyst import router as ai_router
from app.api.v1.reports import router as reports_router

api_v1_router = APIRouter()
api_v1_router.include_router(auth_router)
api_v1_router.include_router(datasets_router)
api_v1_router.include_router(kpis_router)
api_v1_router.include_router(dashboard_router)
api_v1_router.include_router(forecasting_router)
api_v1_router.include_router(scenarios_router)
api_v1_router.include_router(decisions_router)
api_v1_router.include_router(ai_router)
api_v1_router.include_router(reports_router)
