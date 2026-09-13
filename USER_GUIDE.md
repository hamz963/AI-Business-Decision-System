# AI-BDSS User & Strategic Operations Guide

Welcome to the **AI-Powered Business Decision Support System (AI-BDSS)**. This guide outlines end-to-end workflows for executives, business analysts, and operators.

---

## 1. Executive Briefing & Cockpit
Upon logging into the platform:
- Inspect the **AI Executive Intelligence Briefing** at the top of the screen.
- The briefing summarizes the period's recognized revenue, gross margin, operating profit, and primary root-cause drivers.
- Click **Simulate Impact** on any recommended initiative to immediately launch a What-If model in the Scenario Studio.

---

## 2. Ingesting Data & Auditing Quality
1. Navigate to **Data & Quality Engine** from the sidebar.
2. Drag and drop your `.csv` or `.xlsx` sales or ledger file.
3. The platform automatically detects column data types, computes null rates, checks for duplicate transactions, and outputs a **Data Quality Score (0–100)**.
4. If your quality index is **VERIFIED (Score &gt; 90)**, the data is automatically registered in DuckDB for sub-second columnar queries.
5. Inspect the first 25 records in the in-memory tabular explorer.

---

## 3. Running What-If Econometric Simulations
1. Navigate to **Scenario Simulator**.
2. Use the interactive sliders to adjust:
   - **Selling Price Adjustment (-30% to +50%)**
   - **Marketing Budget Scaling (-50% to +100%)**
   - **Operational Cost Shift (-25% to +35%)**
   - **Demand Elasticity Coefficient (-0.5 to -2.5)**
3. Review the live **Projected Revenue**, **Projected Net Profit**, and **Risk Score**.
4. Inspect the **P&L Variance Breakdown Table** to see exactly how variable COGS and overheads react to volume shifts.
5. Click **Save Scenario** to persist the simulation into the governance audit trail.

---

## 4. Grounded AI Analyst
1. Navigate to **Grounded AI Analyst**.
2. Type any business question or click one of the quick prompt chips:
   - *"Why did gross margin contract in recent periods?"*
   - *"What happens if prices increase by 8%?"*
   - *"Forecast revenue trajectory for next 6 months"*
   - *"Identify unusual transaction anomalies in the ledger"*
3. Every response is structured into:
   - **FACT**: Exact figures verified from historical ledgers.
   - **INFERENCE**: Statistical root-cause deductions.
   - **PREDICTION**: Model-generated outputs with confidence bounds.
   - **ASSUMPTION**: Stated parameter boundaries.
   - **RECOMMENDATION**: Concrete actions with expected dollar impact.

---

## 5. Strategic Decision Governance
1. Navigate to **Decision Intelligence**.
2. Review active strategic proposals evaluated across **Expected Profit**, **Risk**, **Growth**, and **Feasibility**.
3. Under **Executive Sign-Off & Governance Audit**, enter optional review notes.
4. Click **Approve Proposal**, **Reject**, or **Mark Executed** to record your decision in the compliance log.
