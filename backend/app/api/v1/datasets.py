import os
import time
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from app.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.dataset import Dataset
from app.schemas.dataset import DatasetOut, DatasetPreview
from app.services.data_ingestion import data_ingestion_service
from app.services.duckdb_engine import duckdb_engine
from app.services.audit_service import audit_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/datasets", tags=["Datasets"])

# Extensions we accept for ingestion
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".json"}


@router.get("/", response_model=List[DatasetOut])
def list_datasets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Dataset)
        .filter(Dataset.org_id == current_user.org_id)
        .order_by(Dataset.created_at.desc())
        .all()
    )


@router.post("/upload", response_model=DatasetOut)
async def upload_dataset(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Extension validation
    _, ext = os.path.splitext(file.filename or "")
    if ext.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    # Read into memory so we can enforce the size cap before touching the filesystem
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_BYTES:
        max_mb = settings.MAX_UPLOAD_BYTES // (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the {max_mb} MB upload limit.",
        )

    # Timestamp in filename to avoid collisions when two users upload the same filename
    epoch_ms = int(time.time() * 1000)
    safe_filename = f"{current_user.org_id}_{epoch_ms}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

    with open(file_path, "wb") as buf:
        buf.write(content)

    try:
        table_name, row_count, col_count, quality_score, schema_info, quality_report = (
            data_ingestion_service.ingest_file(
                file_path=file_path,
                org_id=current_user.org_id,
                original_filename=file.filename,
            )
        )
    except Exception as exc:
        if os.path.exists(file_path):
            os.remove(file_path)
        logger.exception("Ingestion failed for '%s'", file.filename)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to ingest dataset: {exc}",
        )

    dataset = Dataset(
        org_id=current_user.org_id,
        name=name or file.filename,
        description=description,
        source_type=ext.lstrip("."),
        file_path=file_path,
        table_name=table_name,
        row_count=row_count,
        column_count=col_count,
        schema_info=schema_info,
        quality_score=quality_score,
        quality_report=quality_report,
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    audit_service.log_action(
        db=db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        action="DATASET_UPLOAD",
        entity_type="dataset",
        entity_id=dataset.id,
        details={"name": dataset.name, "rows": row_count, "quality_score": quality_score},
    )

    return dataset


@router.get("/{dataset_id}", response_model=DatasetOut)
def get_dataset(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.org_id == current_user.org_id,
    ).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    return dataset


@router.get("/{dataset_id}/preview", response_model=DatasetPreview)
def preview_dataset(
    dataset_id: str,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not 1 <= limit <= 500:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 500.")

    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.org_id == current_user.org_id,
    ).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    # table_name is stored by us, not user-supplied; limit is parameterized
    rows = duckdb_engine.execute_query(
        f"SELECT * FROM {dataset.table_name} LIMIT ?", [limit]
    )
    cols = list(rows[0].keys()) if rows else []

    return DatasetPreview(
        dataset=DatasetOut.from_orm(dataset),
        columns=cols,
        rows=rows,
    )


@router.delete("/{dataset_id}", status_code=204)
def delete_dataset(
    dataset_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.org_id == current_user.org_id,
    ).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    # Use execute_ddl() — it acquires the shared DuckDB lock and returns properly
    try:
        duckdb_engine.execute_ddl(f"DROP TABLE IF EXISTS {dataset.table_name}")
    except Exception:
        logger.warning(
            "Could not drop DuckDB table '%s'; continuing with metadata deletion.",
            dataset.table_name,
        )

    if dataset.file_path and os.path.exists(dataset.file_path):
        try:
            os.remove(dataset.file_path)
        except OSError:
            logger.warning("Could not remove file '%s'.", dataset.file_path)

    db.delete(dataset)
    db.commit()
