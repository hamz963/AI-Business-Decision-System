import os
import uuid
import pandas as pd
from typing import Tuple, Dict, Any
from app.services.duckdb_engine import duckdb_engine
from app.services.data_quality import data_quality_engine

class DataIngestionService:
    """
    Ingests tabular business data from CSV, Excel, or JSON.
    Runs schema profiling, computes quality metrics, and registers into DuckDB.
    """

    @staticmethod
    def ingest_file(file_path: str, org_id: str, original_filename: str) -> Tuple[str, int, int, float, Dict[str, Any], Dict[str, Any]]:
        ext = os.path.splitext(original_filename)[1].lower()
        
        # Load into pandas dataframe
        if ext == ".csv":
            # Attempt UTF-8 with latin1 fallback
            try:
                df = pd.read_csv(file_path, encoding="utf-8")
            except UnicodeDecodeError:
                df = pd.read_csv(file_path, encoding="latin1")
        elif ext in [".xlsx", ".xls"]:
            df = pd.read_excel(file_path)
        elif ext == ".json":
            df = pd.read_json(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}. Only CSV, Excel, and JSON are supported.")

        # Clean column names (strip whitespace, lowercase, replace spaces/dashes with underscores)
        df.columns = [str(c).strip().lower().replace(" ", "_").replace("-", "_") for c in df.columns]

        row_count = len(df)
        col_count = len(df.columns)

        # Run Data Quality and profiling
        quality_score, quality_report = data_quality_engine.analyze_dataframe(df)

        # Generate a safe unique DuckDB table name
        safe_org = org_id.replace("-", "_")[:8]
        safe_id = str(uuid.uuid4()).replace("-", "_")[:8]
        table_name = f"tbl_{safe_org}_{safe_id}"

        # Register inside DuckDB columnar store
        duckdb_engine.register_dataframe(table_name, df)

        schema_info = {
            "columns": quality_report["columns"],
            "row_count": row_count,
            "column_count": col_count
        }

        return table_name, row_count, col_count, quality_score, schema_info, quality_report

data_ingestion_service = DataIngestionService()
