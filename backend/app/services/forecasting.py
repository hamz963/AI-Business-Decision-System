import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from app.services.duckdb_engine import duckdb_engine
from app.schemas.analytics import ForecastPoint, ForecastResult

class ForecastingEngine:
    """
    Time-series forecasting engine.
    Applies backtesting validation across multiple statistical models,
    selects the model with lowest MAPE/RMSE, and projects future periods
    with confidence intervals.
    """

    @staticmethod
    def forecast_metric(
        table_name: str,
        date_col: str,
        metric_col: str,
        periods_ahead: int = 6,
        freq: str = "month"
    ) -> ForecastResult:
        """
        Executes time-series aggregation and model evaluation.
        """
        # 1. Aggregate time-series using DuckDB date truncation
        sql = f"""
            SELECT 
                DATE_TRUNC('{freq}', CAST({date_col} AS DATE)) as period_date,
                COALESCE(SUM({metric_col}), 0.0) as total_val
            FROM {table_name}
            WHERE {date_col} IS NOT NULL
            GROUP BY 1
            ORDER BY 1 ASC
        """
        rows = duckdb_engine.execute_query(sql)
        if len(rows) < 4:
            raise ValueError("Insufficient time-series history (minimum 4 periods required for forecasting).")

        df = pd.DataFrame(rows)
        df["period_date"] = pd.to_datetime(df["period_date"])
        df["total_val"] = df["total_val"].astype(float)
        
        y = df["total_val"].values
        dates = df["period_date"].dt.strftime("%Y-%m-%d").tolist()
        n = len(y)

        # 2. Train / Test Split for validation (last 20% or minimum 2 periods)
        test_size = max(2, int(n * 0.25))
        train_y = y[:-test_size]
        test_y = y[-test_size:]

        # Candidate Model 1: Double Exponential Smoothing (Holt's Linear Trend)
        def holt_forecast(series: np.ndarray, horizon: int, alpha: float = 0.4, beta: float = 0.2):
            level = series[0]
            trend = series[1] - series[0] if len(series) > 1 else 0.0
            for val in series[1:]:
                last_level = level
                level = alpha * val + (1 - alpha) * (level + trend)
                trend = beta * (level - last_level) + (1 - beta) * trend
            
            predictions = [level + (h * trend) for h in range(1, horizon + 1)]
            return np.array(predictions)

        # Candidate Model 2: Polynomial Trend with Momentum (Degree 1 or 2)
        def linear_trend_forecast(series: np.ndarray, horizon: int):
            x = np.arange(len(series))
            slope, intercept = np.polyfit(x, series, 1)
            future_x = np.arange(len(series), len(series) + horizon)
            return intercept + slope * future_x

        # Evaluate on test set
        pred_holt_test = holt_forecast(train_y, test_size)
        pred_linear_test = linear_trend_forecast(train_y, test_size)

        def calc_mape(actual, pred):
            denom = np.where(actual == 0, 1.0, actual)
            return float(np.mean(np.abs((actual - pred) / denom)) * 100.0)

        def calc_rmse(actual, pred):
            return float(np.sqrt(np.mean((actual - pred) ** 2)))

        mape_holt = calc_mape(test_y, pred_holt_test)
        rmse_holt = calc_rmse(test_y, pred_holt_test)

        mape_linear = calc_mape(test_y, pred_linear_test)
        rmse_linear = calc_rmse(test_y, pred_linear_test)

        # Select winning model
        if mape_holt <= mape_linear:
            chosen_model_name = "Holt Exponential Smoothing"
            best_mape = mape_holt
            best_rmse = rmse_holt
            future_preds = holt_forecast(y, periods_ahead)
        else:
            chosen_model_name = "Adaptive Linear Trend"
            best_mape = mape_linear
            best_rmse = rmse_linear
            future_preds = linear_trend_forecast(y, periods_ahead)

        # Calculate prediction intervals based on validation residual standard deviation
        residuals = y[-test_size:] - (pred_holt_test if chosen_model_name.startswith("Holt") else pred_linear_test)
        std_err = float(np.std(residuals)) if len(residuals) > 1 else float(np.std(y) * 0.1)
        z_95 = 1.96

        # Build history points
        history_points: List[ForecastPoint] = []
        for d, val in zip(dates, y):
            history_points.append(ForecastPoint(
                date=d,
                actual=round(float(val), 2),
                predicted=round(float(val), 2),
                lower_bound=round(float(val), 2),
                upper_bound=round(float(val), 2)
            ))

        # Generate future dates
        last_date = pd.to_datetime(dates[-1])
        future_points: List[ForecastPoint] = []
        for step, val in enumerate(future_preds, 1):
            if freq == "month":
                next_date = (last_date + pd.DateOffset(months=step)).strftime("%Y-%m-%d")
            else:
                next_date = (last_date + pd.DateOffset(days=step * 7)).strftime("%Y-%m-%d")

            pred_val = max(0.0, float(val))
            # Uncertainty expands with time horizon
            uncertainty = std_err * np.sqrt(step)
            lower = max(0.0, pred_val - (z_95 * uncertainty))
            upper = pred_val + (z_95 * uncertainty)

            future_points.append(ForecastPoint(
                date=next_date,
                actual=None,
                predicted=round(pred_val, 2),
                lower_bound=round(lower, 2),
                upper_bound=round(upper, 2)
            ))

        # Calculate projected growth
        baseline_avg = float(np.mean(y[-3:])) if len(y) >= 3 else float(y[-1])
        projected_avg = float(np.mean(future_preds))
        growth_pct = ((projected_avg - baseline_avg) / baseline_avg * 100.0) if baseline_avg > 0 else 0.0

        assumptions = [
            f"Selected {chosen_model_name} via backtesting (MAPE: {best_mape:.1f}%, RMSE: {best_rmse:.1f}).",
            "Assumes current operational velocity and macroeconomic stability remain within historical bounds.",
            "Prediction bounds reflect 95% confidence interval scaling with time horizon."
        ]

        return ForecastResult(
            metric=metric_col,
            model_name=chosen_model_name,
            validation_mape=round(best_mape, 2),
            validation_rmse=round(best_rmse, 2),
            history=history_points,
            forecast=future_points,
            summary_growth_pct=round(growth_pct, 1),
            assumptions=assumptions
        )

forecasting_engine = ForecastingEngine()
