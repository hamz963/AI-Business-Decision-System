# AI-BDSS Security & Data Governance

---

## 1. Multi-Tenant Isolation
- Tenant context is bound to every cryptographically signed JWT.
- Every database query and DuckDB table name includes the tenant identifier (`tbl_{org_id}_{dataset_id}`).
- Cross-tenant data access is structurally impossible at the API gateway layer.

## 2. SQL & Analytical Query Safety
- Analytical queries run through `DuckDBEngine.execute_query()`.
- Explicit keyword filtering blocks mutating statements (`DROP`, `DELETE`, `UPDATE`, `INSERT`, `TRUNCATE`, `ALTER`).
- All queries are strictly read-only aggregations.

## 3. Grounding & Anti-Hallucination Controls
- Deterministic calculation logic resides purely in Python service classes.
- The AI orchestrator never synthesizes financial figures from memory; all metrics are injected from executed tool payloads.
- Responses strictly categorize statements into Fact, Inference, Prediction, and Assumption.

## 4. Human-In-The-Loop Sign-Off
- High-impact decisions (pricing changes, budget allocation, catalog discontinuation) require human executive sign-off before status transitions to `approved` or `implemented`.
- All governance decisions record timestamp, user ID, and review rationale into an immutable `audit_logs` table.
