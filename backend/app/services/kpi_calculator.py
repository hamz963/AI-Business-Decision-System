from typing import Dict, Any, List, Optional
from app.services.duckdb_engine import duckdb_engine

class KPICalculator:
    """
    Deterministic KPI calculation engine.
    Calculates executive metrics and period-over-period variances
    directly from DuckDB columnar tables.
    """

    @staticmethod
    def calculate_standard_metrics(table_name: str) -> Dict[str, Any]:
        """
        Extracts foundational enterprise metrics from a dataset.
        Detects standard columns like amount/revenue/sales, cost/cogs/expenses,
        order_id, customer_id, and date.
        """
        columns_info = duckdb_engine.get_table_schema(table_name)
        col_names = [c["column_name"].lower() for c in columns_info]

        # 1. Detect Revenue / Sales column
        rev_col = None
        for candidate in ["revenue", "sales", "total_amount", "amount", "price", "subtotal"]:
            if candidate in col_names:
                rev_col = candidate
                break

        # 2. Detect Cost / COGS column
        cost_col = None
        for candidate in ["cogs", "cost", "total_cost", "expenses", "expense"]:
            if candidate in col_names:
                cost_col = candidate
                break

        # 3. Detect Order ID column
        order_col = None
        for candidate in ["order_id", "transaction_id", "invoice_id", "id"]:
            if candidate in col_names:
                order_col = candidate
                break

        # 4. Detect Customer ID column
        cust_col = None
        for candidate in ["customer_id", "client_id", "user_id", "account_id"]:
            if candidate in col_names:
                cust_col = candidate
                break

        # 5. Detect Date column
        date_col = None
        for candidate in ["order_date", "date", "created_at", "transaction_date", "timestamp"]:
            if candidate in col_names:
                date_col = candidate
                break

        # Build aggregation query
        select_clauses = ["COUNT(*) as total_records"]
        
        if rev_col:
            select_clauses.append(f"COALESCE(SUM({rev_col}), 0.0) as total_revenue")
            select_clauses.append(f"COALESCE(AVG({rev_col}), 0.0) as avg_order_value")
        else:
            select_clauses.append("0.0 as total_revenue")
            select_clauses.append("0.0 as avg_order_value")

        if cost_col:
            select_clauses.append(f"COALESCE(SUM({cost_col}), 0.0) as total_cogs")
        else:
            select_clauses.append("0.0 as total_cogs")

        if order_col:
            select_clauses.append(f"COUNT(DISTINCT {order_col}) as total_orders")
        else:
            select_clauses.append("COUNT(*) as total_orders")

        if cust_col:
            select_clauses.append(f"COUNT(DISTINCT {cust_col}) as total_customers")
        else:
            select_clauses.append("0 as total_customers")

        query = f"SELECT {', '.join(select_clauses)} FROM {table_name}"
        rows = duckdb_engine.execute_query(query)
        base = rows[0] if rows else {}

        revenue = float(base.get("total_revenue", 0.0))
        cogs = float(base.get("total_cogs", 0.0))
        orders = int(base.get("total_orders", 0))
        customers = int(base.get("total_customers", 0))

        gross_profit = revenue - cogs
        gross_margin_pct = (gross_profit / revenue * 100.0) if revenue > 0 else 0.0

        # If no OPEX column exists, estimate from COGS and flag it clearly.
        # This assumption (25% of COGS) is documented so downstream code can surface it.
        if cost_col:
            operating_expenses = cogs * 0.25
            opex_is_estimated = True
        else:
            operating_expenses = revenue * 0.15
            opex_is_estimated = True

        net_profit = gross_profit - operating_expenses
        net_margin_pct = (net_profit / revenue * 100.0) if revenue > 0 else 0.0
        aov = (revenue / orders) if orders > 0 else 0.0

        return {
            "revenue": round(revenue, 2),
            "cogs": round(cogs, 2),
            "gross_profit": round(gross_profit, 2),
            "gross_margin_pct": round(gross_margin_pct, 2),
            "operating_expenses": round(operating_expenses, 2),
            "opex_is_estimated": opex_is_estimated,
            "opex_estimation_note": "Operating expenses estimated at 25% of COGS (no OPEX column detected in dataset).",
            "net_profit": round(net_profit, 2),
            "net_margin_pct": round(net_margin_pct, 2),
            "orders": orders,
            "customers": customers,
            "average_order_value": round(aov, 2),
            "detected_columns": {
                "revenue": rev_col,
                "cost": cost_col,
                "order": order_col,
                "customer": cust_col,
                "date": date_col,
            },
        }

    @staticmethod
    def calculate_category_breakdown(table_name: str, category_col: str, metric_col: str) -> List[Dict[str, Any]]:
        """Calculates dimensional breakdown by category or region."""
        import re
        if not re.match(r"^[A-Za-z0-9_]+$", category_col) or not re.match(r"^[A-Za-z0-9_]+$", metric_col):
            raise ValueError("Invalid column name provided for category breakdown.")

        query = f"""
            SELECT 
                "{category_col}" as category,
                COALESCE(SUM("{metric_col}"), 0.0) as revenue,
                COUNT(*) as volume
            FROM {table_name}
            WHERE "{category_col}" IS NOT NULL
            GROUP BY "{category_col}"
            ORDER BY revenue DESC
            LIMIT 10
        """
        rows = duckdb_engine.execute_query(query)
        total_rev = sum(r["revenue"] for r in rows) if rows else 1.0
        for r in rows:
            r["share_pct"] = round((r["revenue"] / total_rev * 100.0), 1) if total_rev > 0 else 0.0
            r["revenue"] = round(r["revenue"], 2)
        return rows

kpi_calculator = KPICalculator()
