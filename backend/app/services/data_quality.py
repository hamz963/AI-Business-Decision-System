import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from app.schemas.dataset import DatasetQualityReport, ColumnMeta, QualityMetric

class DataQualityEngine:
    """
    Evaluates dataset quality against enterprise dimensions:
    Completeness, Uniqueness, Validity, and Statistical Consistency.
    """

    @staticmethod
    def analyze_dataframe(df: pd.DataFrame) -> Tuple[float, Dict[str, Any]]:
        total_rows = len(df)
        total_cols = len(df.columns)
        
        if total_rows == 0:
            return 0.0, {
                "overall_score": 0.0,
                "status": "poor",
                "row_count": 0,
                "column_count": total_cols,
                "columns": [],
                "quality_metrics": [],
                "issues": ["Dataset is empty."],
                "warnings": []
            }

        issues: List[str] = []
        warnings: List[str] = []
        columns_meta: List[Dict[str, Any]] = []

        # 1. Completeness Score
        total_cells = total_rows * total_cols
        total_nulls = int(df.isnull().sum().sum())
        completeness_pct = max(0.0, (1.0 - (total_nulls / total_cells)) * 100.0)
        
        if completeness_pct < 85.0:
            issues.append(f"High volume of missing values: {total_nulls} null entries ({100 - completeness_pct:.1f}% missing).")
        elif completeness_pct < 95.0:
            warnings.append(f"Some missing values detected: {total_nulls} null entries.")

        # 2. Uniqueness Score (Duplicate Rows)
        duplicate_rows = int(df.duplicated().sum())
        uniqueness_pct = max(0.0, (1.0 - (duplicate_rows / total_rows)) * 100.0)
        if duplicate_rows > 0:
            issues.append(f"Found {duplicate_rows} duplicate rows ({duplicate_rows / total_rows * 100:.1f}% of total).")

        # 3. Column Profiling & Validity
        validity_deductions = 0.0
        for col in df.columns:
            series = df[col]
            null_count = int(series.isnull().sum())
            null_pct = (null_count / total_rows) * 100.0
            unique_count = int(series.nunique(dropna=True))

            # Determine inferred type
            if pd.api.types.is_numeric_dtype(series):
                inferred_type = "numeric"
                # Check for negative amounts in columns suggesting monetary or volume
                col_lower = col.lower()
                if any(kw in col_lower for kw in ["revenue", "price", "sales", "inventory", "quantity"]):
                    negatives = (series < 0).sum()
                    if negatives > 0:
                        validity_deductions += 5.0
                        warnings.append(f"Column '{col}' has {negatives} negative values where positive numbers are expected.")
            elif pd.api.types.is_datetime64_any_dtype(series):
                inferred_type = "datetime"
            elif pd.api.types.is_bool_dtype(series):
                inferred_type = "boolean"
            else:
                # Check if it might be date string
                sample = series.dropna().astype(str).head(10)
                is_date = False
                try:
                    pd.to_datetime(sample)
                    is_date = True
                except Exception:
                    pass
                
                if is_date:
                    inferred_type = "datetime"
                elif unique_count < 30 and unique_count < total_rows * 0.2:
                    inferred_type = "categorical"
                else:
                    inferred_type = "text"

            sample_vals = [val for val in series.dropna().head(5).tolist()]
            # Ensure serializable sample values
            serializable_samples = []
            for v in sample_vals:
                if isinstance(v, (pd.Timestamp, np.datetime64)):
                    serializable_samples.append(str(v))
                elif isinstance(v, (np.int64, np.int32, np.float64, np.float32)):
                    serializable_samples.append(float(v) if isinstance(v, (np.float64, np.float32)) else int(v))
                else:
                    serializable_samples.append(str(v))

            columns_meta.append({
                "name": str(col),
                "inferred_type": inferred_type,
                "null_count": null_count,
                "null_percentage": round(null_pct, 2),
                "unique_count": unique_count,
                "sample_values": serializable_samples
            })

        validity_pct = max(0.0, 100.0 - validity_deductions)

        # 4. Composite Quality Score: Weighted average
        # Completeness (40%), Uniqueness (30%), Validity (30%)
        overall_score = round(
            (completeness_pct * 0.40) + (uniqueness_pct * 0.30) + (validity_pct * 0.30),
            1
        )

        if overall_score >= 90.0:
            status = "excellent"
        elif overall_score >= 75.0:
            status = "good"
        elif overall_score >= 60.0:
            status = "fair"
        else:
            status = "poor"

        quality_metrics = [
            {"dimension": "Completeness", "score": round(completeness_pct, 1), "details": f"{total_nulls} missing cells across {total_cells} total values"},
            {"dimension": "Uniqueness", "score": round(uniqueness_pct, 1), "details": f"{duplicate_rows} duplicate rows detected"},
            {"dimension": "Validity", "score": round(validity_pct, 1), "details": "Type constraints and domain sanity checks"}
        ]

        report = {
            "overall_score": overall_score,
            "status": status,
            "row_count": total_rows,
            "column_count": total_cols,
            "columns": columns_meta,
            "quality_metrics": quality_metrics,
            "issues": issues,
            "warnings": warnings
        }

        return overall_score, report

data_quality_engine = DataQualityEngine()
