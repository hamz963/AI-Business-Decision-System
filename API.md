# AI-BDSS REST API Specification

All endpoints are versioned under `/api/v1` and return JSON.

---

## Authentication & Multi-Tenancy

### `POST /api/v1/auth/register`
Creates an organization and administrator account.
- **Request Body**:
  ```json
  {
    "email": "executive@acme.com",
    "password": "SecurePassword123!",
    "full_name": "Jane Doe",
    "org_name": "Acme Global"
  }
  ```
- **Response**: Returns JWT bearer access token and user metadata.

### `POST /api/v1/auth/login`
Authenticates existing tenant users.
- **Response**:
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "user": { "id": "uuid", "email": "...", "role": "admin" }
  }
  ```

---

## Datasets & Data Quality

### `GET /api/v1/datasets/`
Lists all uploaded datasets for the authenticated organization.

### `POST /api/v1/datasets/upload`
Uploads a `.csv`, `.xlsx`, or `.json` file.
- **Content-Type**: `multipart/form-data`
- **Output**: Returns schema metadata, inferred column types, row counts, and composite `quality_score` (0–100).

### `GET /api/v1/datasets/{dataset_id}/preview`
Returns first $N$ rows directly from the columnar DuckDB table.

---

## Executive Cockpit

### `GET /api/v1/dashboard/executive`
Computes top-level revenue, COGS, gross margin %, operating expenses, net profit, monthly trajectories, and the latest AI Executive Briefing.

---

## Scenarios & What-If Studio

### `POST /api/v1/scenarios/simulate`
Simulates econometric price elasticity and cost shocks.
- **Request Body**:
  ```json
  {
    "parameters": {
      "price_change_pct": 5.0,
      "marketing_spend_pct": 10.0,
      "operating_cost_pct": -3.0,
      "assumed_elasticity": -1.2
    }
  }
  ```
- **Response**: Baseline vs. projected P&L, delta metrics, risk score (0–100), and prescriptive recommendation.

---

## Decision Intelligence

### `GET /api/v1/decisions/`
Lists strategic proposals, MCDA alternatives, and human-in-the-loop review statuses.

### `POST /api/v1/decisions/{id}/review`
Submits human approval or rejection:
- **Request Body**:
  ```json
  {
    "status": "approved",
    "review_notes": "Authorized for Q1 price adjustment on non-contract catalog."
  }
  ```

---

## Grounded AI Business Analyst

### `POST /api/v1/ai/query`
Conversational business query endpoint.
- **Request Body**:
  ```json
  {
    "query": "What happens if we increase prices by 8%?"
  }
  ```
- **Response**:
  ```json
  {
    "query": "What happens if we increase prices by 8%?",
    "intent": "SCENARIO_SIMULATION",
    "answer": "If prices are adjusted by +8.0%...",
    "facts": ["Baseline Revenue: $1,420,500.00", "..."],
    "inferences": ["Estimated volume reaction: ..."],
    "predictions": ["Projected Net Profit: $298,400.00 (+12.4%)"],
    "assumptions": ["Price elasticity coefficient set to -1.2"],
    "recommendations": ["Proceed with staged rollout..."],
    "evidence": [{"metric": "Projected Net Profit Delta", "value": "+$33,100.00"}],
    "confidence": "High"
  }
  ```
