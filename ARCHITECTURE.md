# AI-BDSS Architectural Specification

This document details the engineering and architectural standards governing the **AI-Powered Business Decision Support System (AI-BDSS)**.

---

## 1. Grounding & Separation of Concerns

### The Anti-Hallucination Axiom
Large Language Models (LLMs) must **never** be used as numerical calculators or direct database authors. 

```
┌─────────────────────────────────────────────────────────────┐
│                    DETERMINISTIC SPHERE                     │
│  - SQL aggregations in DuckDB / PostgreSQL                  │
│  - P&L formulas (Revenue, COGS, Gross Margin, Net Margin)   │
│  - Time-series statistical models (Holt-Winters, Trend-OLS) │
│  - Econometric price elasticity (ΔQ% = ε · ΔP%)             │
│  - Multi-Criteria Decision Analysis (MCDA scoring)          │
└──────────────────────────────┬──────────────────────────────┘
                               │ Verified Structured Payloads
┌──────────────────────────────▼──────────────────────────────┐
│                    NARRATIVE AI SPHERE                      │
│  - Translates user intent into parameter schemas            │
│  - Invokes deterministic backend tools                      │
│  - Synthesizes findings into structured audit sections:     │
│    FACT • INFERENCE • PREDICTION • ASSUMPTION • REC         │
│  - Verifies cited numbers exist in the grounding payload   │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Ingestion & Data Quality Engine

Data flows from raw tabular files (`.csv`, `.xlsx`, `.json`) into an isolated DuckDB table:

1. **Schema Inference**:
   - Numeric detection (integer, float).
   - DateTime detection (ISO formats, epoch timestamps).
   - Categorical detection (low cardinality ratio).
2. **Quality Scoring (0–100)**:
   - **Completeness (40%)**: Null rate across all cells.
   - **Uniqueness (30%)**: Duplicate records across primary keys.
   - **Validity (30%)**: Domain sanity checks (non-negative prices, valid dates).

---

## 3. Time-Series Forecasting Tournament

Rather than hard-coding deep learning or arbitrary linear models, the forecasting engine runs a **tournament**:

1. **Candidate 1: Holt's Linear Exponential Smoothing**:
   $$L_t = \alpha Y_t + (1 - \alpha)(L_{t-1} + T_{t-1})$$
   $$T_t = \beta(L_t - L_{t-1}) + (1 - \beta)T_{t-1}$$
   $$\hat{Y}_{t+h} = L_t + h T_t$$
2. **Candidate 2: Adaptive Polynomial Trend Regression**:
   $$\hat{Y}_t = \beta_0 + \beta_1 t + \epsilon_t$$
3. **Validation & Selection**:
   - The dataset is split into training and hold-out test periods.
   - Models are scored via Mean Absolute Percentage Error (MAPE) and Root Mean Squared Error (RMSE):
     $$\text{MAPE} = \frac{100\%}{n}\sum_{t=1}^n \left|\frac{Y_t - \hat{Y}_t}{Y_t}\right|$$
   - The winning model generates future horizons with 95% confidence bounds ($Z = 1.96 \cdot \sigma_{\text{residuals}}\sqrt{h}$).

---

## 4. Scenario Simulator (What-If Engine)

The simulation engine implements microeconomic price elasticity:

$$\Delta Q = \epsilon_p \times \Delta P$$
$$\text{Projected Revenue} = P_0 (1 + \Delta P) \times Q_0 (1 + \Delta Q)$$
$$\text{Projected Variable COGS} = \text{COGS}_{\text{var}} \times (1 + \Delta Q)$$
$$\text{Projected OPEX} = \text{OPEX}_{\text{marketing}} (1 + \Delta M) + \text{OPEX}_{\text{labor}} (1 + \Delta L) + \text{OPEX}_{\text{fixed}}$$

---

## 5. Multi-Criteria Decision Intelligence

Decisions evaluate multiple mutually exclusive options against a weighted multi-attribute utility function:

$$\text{Score} = (0.35 \times \text{Profit}) + (0.25 \times (100 - \text{Risk})) + (0.20 \times \text{Growth}) + (0.20 \times \text{Feasibility})$$

- Every option requires:
  - Stated business rationale.
  - Linked KPI evidence.
  - Explicit model assumptions.
  - Expected impact ranges.
- Human-in-the-loop: An executive must approve or reject the recommendation before execution status changes.
