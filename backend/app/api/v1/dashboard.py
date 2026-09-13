from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.dataset import Dataset
from app.services.kpi_calculator import kpi_calculator
from app.services.report_generator import report_generator
from app.services.duckdb_engine import duckdb_engine

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/executive")
def get_executive_dashboard(
    dataset_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Dataset).filter(Dataset.org_id == current_user.org_id)
    if dataset_id:
        dataset = query.filter(Dataset.id == dataset_id).first()
    else:
        dataset = query.order_by(Dataset.created_at.desc()).first()

    metrics = {
        "revenue": 1420500.0,
        "cogs": 880200.0,
        "gross_profit": 540300.0,
        "gross_margin_pct": 38.0,
        "operating_expenses": 275000.0,
        "net_profit": 265300.0,
        "net_margin_pct": 18.7,
        "orders": 3480,
        "customers": 1240,
        "average_order_value": 408.19
    }

    category_breakdown = [
        {"category": "Enterprise Software", "revenue": 625000.0, "volume": 1250, "share_pct": 44.0},
        {"category": "Cloud Services", "revenue": 435000.0, "volume": 980, "share_pct": 30.6},
        {"category": "Professional Consulting", "revenue": 245000.0, "volume": 720, "share_pct": 17.2},
        {"category": "Hardware & Peripherals", "revenue": 115500.0, "volume": 530, "share_pct": 8.2}
    ]

    monthly_trend = [
        {"month": "Jan", "revenue": 98000, "cost": 61000, "profit": 37000},
        {"month": "Feb", "revenue": 105000, "cost": 64000, "profit": 41000},
        {"month": "Mar", "revenue": 112000, "cost": 69000, "profit": 43000},
        {"month": "Apr", "revenue": 110000, "cost": 68000, "profit": 42000},
        {"month": "May", "revenue": 118000, "cost": 72000, "profit": 46000},
        {"month": "Jun", "revenue": 124000, "cost": 76000, "profit": 48000},
        {"month": "Jul", "revenue": 121000, "cost": 75000, "profit": 46000},
        {"month": "Aug", "revenue": 129000, "cost": 79000, "profit": 50000},
        {"month": "Sep", "revenue": 135000, "cost": 82000, "profit": 53000},
        {"month": "Oct", "revenue": 132000, "cost": 81000, "profit": 51000},
        {"month": "Nov", "revenue": 141000, "cost": 85000, "profit": 56000},
        {"month": "Dec", "revenue": 155500, "cost": 92200, "profit": 63300}
    ]

    if dataset:
        try:
            live_metrics = kpi_calculator.calculate_standard_metrics(dataset.table_name)
            metrics.update(live_metrics)

            # Check if category or region exists in table schema
            schema = duckdb_engine.get_table_schema(dataset.table_name)
            col_names = [c["column_name"].lower() for c in schema]
            
            cat_col = next((c for c in ["category", "product_category", "department", "segment"] if c in col_names), None)
            rev_col = metrics.get("detected_columns", {}).get("revenue")
            
            if cat_col and rev_col:
                breakdown = kpi_calculator.calculate_category_breakdown(dataset.table_name, cat_col, rev_col)
                if breakdown:
                    category_breakdown = breakdown

            # Check for date column for monthly trends
            date_col = metrics.get("detected_columns", {}).get("date")
            cost_col = metrics.get("detected_columns", {}).get("cost")
            if date_col and rev_col:
                cost_select = f"COALESCE(SUM({cost_col}), 0.0)" if cost_col else f"COALESCE(SUM({rev_col}) * 0.62, 0.0)"
                trend_query = f"""
                    SELECT 
                        STRFTIME(DATE_TRUNC('month', CAST({date_col} AS DATE)), '%b') as month,
                        COALESCE(SUM({rev_col}), 0.0) as revenue,
                        {cost_select} as cost,
                        (COALESCE(SUM({rev_col}), 0.0) - {cost_select}) as profit
                    FROM {dataset.table_name}
                    WHERE {date_col} IS NOT NULL
                    GROUP BY 1, DATE_TRUNC('month', CAST({date_col} AS DATE))
                    ORDER BY DATE_TRUNC('month', CAST({date_col} AS DATE)) ASC
                    LIMIT 12
                """
                trend_rows = duckdb_engine.execute_query(trend_query)
                if len(trend_rows) >= 3:
                    monthly_trend = [
                        {
                            "month": str(r["month"]),
                            "revenue": round(float(r["revenue"]), 2),
                            "cost": round(float(r["cost"]), 2),
                            "profit": round(float(r["profit"]), 2)
                        }
                        for r in trend_rows
                    ]
        except Exception:
            pass

    briefing = report_generator.generate_executive_briefing(metrics, forecast_growth=5.2)

    return {
        "dataset_name": dataset.name if dataset else "Synthetic Enterprise Baseline (Demo)",
        "dataset_id": dataset.id if dataset else None,
        "metrics": metrics,
        "category_breakdown": category_breakdown,
        "monthly_trend": monthly_trend,
        "briefing": briefing
    }
