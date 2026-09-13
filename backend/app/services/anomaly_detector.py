import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from app.services.duckdb_engine import duckdb_engine
from app.schemas.analytics import AnomalyItem

class AnomalyDetector:
    """
    Detects business anomalies using statistical thresholding (Z-Score & IQR)
    and classifies severity into LOW, MEDIUM, HIGH, and CRITICAL.
    """

    @staticmethod
    def detect_anomalies(
        table_name: str,
        metric_col: str,
        entity_col: Optional[str] = None,
        date_col: Optional[str] = None,
        z_threshold: float = 2.5
    ) -> List[AnomalyItem]:
        cols = [metric_col]
        if entity_col:
            cols.append(entity_col)
        if date_col:
            cols.append(date_col)

        query = f"SELECT {', '.join(cols)} FROM {table_name} WHERE {metric_col} IS NOT NULL"
        rows = duckdb_engine.execute_query(query)
        if len(rows) < 10:
            return []

        df = pd.DataFrame(rows)
        series = df[metric_col].astype(float)
        
        mean_val = float(series.mean())
        std_val = float(series.std())
        if std_val == 0:
            return []

        # IQR computation for robust verification
        q25 = float(series.quantile(0.25))
        q75 = float(series.quantile(0.75))
        iqr = q75 - q25
        lower_iqr = q25 - (1.5 * iqr)
        upper_iqr = q75 + (1.5 * iqr)

        anomalies: List[AnomalyItem] = []
        for idx, row in df.iterrows():
            val = float(row[metric_col])
            z_score = (val - mean_val) / std_val

            # Trigger condition: exceeds z_threshold OR falls outside IQR bounds
            if abs(z_score) >= z_threshold or val < lower_iqr or val > upper_iqr:
                abs_z = abs(z_score)
                if abs_z >= 4.0:
                    severity = "critical"
                elif abs_z >= 3.0:
                    severity = "high"
                elif abs_z >= 2.0:
                    severity = "medium"
                else:
                    severity = "low"

                entity_name = str(row[entity_col]) if entity_col and entity_col in row else f"Record #{idx+1}"
                date_str = str(row[date_col]) if date_col and date_col in row else "N/A"
                
                direction = "higher" if z_score > 0 else "lower"
                details = f"Value of ${val:,.2f} is {abs_z:.2f} standard deviations {direction} than expected average (${mean_val:,.2f})."

                anomalies.append(AnomalyItem(
                    id=f"anom_{idx}",
                    date=date_str,
                    entity=entity_name,
                    field=metric_col,
                    observed_value=round(val, 2),
                    expected_value=round(mean_val, 2),
                    deviation_z_score=round(float(z_score), 2),
                    severity=severity,
                    details=details
                ))

        # Sort by deviation severity descending, limit to top 25
        anomalies.sort(key=lambda a: abs(a.deviation_z_score), reverse=True)
        return anomalies[:25]

anomaly_detector = AnomalyDetector()
