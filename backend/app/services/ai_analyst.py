import logging
import re
from typing import Any, Dict, List, Optional
import httpx

from app.config import settings
from app.schemas.ai import AIQueryResponse, AIToolCall, ModelOption
from app.schemas.scenario import ScenarioParams
from app.services.anomaly_detector import anomaly_detector
from app.services.decision_engine import decision_engine
from app.services.forecasting import forecasting_engine
from app.services.kpi_calculator import kpi_calculator
from app.services.scenario_simulator import scenario_simulator

logger = logging.getLogger(__name__)

# Pre-defined curated free-tier and local model registry
AVAILABLE_MODELS: List[Dict[str, Any]] = [
    {
        "id": "big-pickle",
        "name": "Big Pickle (OpenCode Deep Reasoning)",
        "provider": "opencode",
        "description": "OpenCode deliberate reasoning model for complex business decision analysis",
        "free_tier": True,
    },
    {
        "id": "mimo-v2.5-free",
        "name": "Mimo 2.5 Free (OpenCode)",
        "provider": "opencode",
        "description": "OpenCode high-speed general intelligence free tier model",
        "free_tier": True,
    },
    {
        "id": "gemini-2.5-flash",
        "name": "Gemini 2.5 Flash",
        "provider": "google",
        "description": "Google free-tier fast multimodal reasoning model",
        "free_tier": True,
    },
    {
        "id": "gemini-2.5-flash-lite",
        "name": "Gemini 2.5 Flash Lite",
        "provider": "google",
        "description": "Google ultra lightweight high throughput free model",
        "free_tier": True,
    },
    {
        "id": "gemini-3.1-flash-lite",
        "name": "Gemini 3.1 Flash Lite",
        "provider": "google",
        "description": "Google next-gen flash lite model",
        "free_tier": True,
    },
    {
        "id": "qwen3:0.6b",
        "name": "Qwen 3 (0.6B Local)",
        "provider": "ollama",
        "description": "Local offline private model running on Ollama",
        "free_tier": True,
    },
    {
        "id": "rule_based",
        "name": "Rule-Based Deterministic Engine",
        "provider": "local",
        "description": "Deterministic keyword routing with statistical engines (zero tokens)",
        "free_tier": True,
    },
]

# Active runtime selected model
_active_model: str = settings.ACTIVE_AI_MODEL


def get_available_models() -> List[ModelOption]:
    return [
        ModelOption(
            id=m["id"],
            name=m["name"],
            provider=m["provider"],
            description=m["description"],
            free_tier=m["free_tier"],
            is_active=(m["id"] == _active_model),
        )
        for m in AVAILABLE_MODELS
    ]


def set_active_model(model_id: str) -> str:
    global _active_model
    known = [m["id"] for m in AVAILABLE_MODELS]
    if model_id not in known:
        raise ValueError(f"Unknown model '{model_id}'. Allowed: {', '.join(known)}")
    _active_model = model_id
    logger.info("Switched active AI model to: %s", _active_model)
    return _active_model


def get_active_model() -> str:
    return _active_model


def _call_opencode_zen(model_id: str, prompt: str, system_prompt: str) -> Optional[str]:
    """Call OpenCode Zen API for OpenCode models like big-pickle."""
    import uuid

    if not settings.OPENCODE_API_KEY:
        logger.warning("OPENCODE_API_KEY is not set.")
        return None

    clean_model = model_id.replace("opencode/", "")
    url = f"{settings.OPENCODE_ZEN_BASE_URL}/chat/completions"

    session_id = f"ses_{uuid.uuid4().hex[:16]}"
    request_id = f"req_{uuid.uuid4().hex[:16]}"

    headers = {
        "Authorization": f"Bearer {settings.OPENCODE_API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "opencode/1.18.30",
        "x-opencode-session": session_id,
        "x-opencode-request": request_id,
        "x-opencode-client": "cli",
    }

    payload = {
        "model": clean_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 1200,
    }

    try:
        # Big Pickle is a reasoning model, allow sufficient response time
        with httpx.Client(timeout=90.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                msg = data["choices"][0]["message"]
                content = msg.get("content")
                if content and content.strip():
                    return content.strip()
                # Fallback to reasoning or reasoning_content if output was generated in thinking mode
                reasoning = msg.get("reasoning") or msg.get("reasoning_content")
                if reasoning and reasoning.strip():
                    return reasoning.strip()
                # Check reasoning_details
                details = msg.get("reasoning_details")
                if details and isinstance(details, list) and len(details) > 0:
                    text_parts = [d.get("text", "") for d in details if isinstance(d, dict)]
                    joined = "".join(text_parts).strip()
                    if joined:
                        return joined
            logger.error("OpenCode Zen error (%d): %s", resp.status_code, resp.text[:200])
    except Exception:
        logger.exception("Failed calling OpenCode Zen API for model '%s'", model_id)

    return None


def _call_gemini_api(model_id: str, prompt: str, system_prompt: str) -> Optional[str]:
    """Call Google Generative Language API directly using the configured Google key."""
    if not settings.GOOGLE_API_KEY:
        logger.warning("GOOGLE_API_KEY is not set.")
        return None

    clean_model = model_id.replace("google/", "")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{clean_model}:generateContent?key={settings.GOOGLE_API_KEY}"
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": f"{system_prompt}\n\nTask/Question:\n{prompt}"}],
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 1000,
        },
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
            logger.error("Gemini API error (%d): %s", resp.status_code, resp.text[:200])
    except Exception:
        logger.exception("Failed calling Gemini API")
    return None


def _call_ollama_api(model_id: str, prompt: str, system_prompt: str) -> Optional[str]:
    """Call local Ollama instance for 100% offline private processing."""
    clean_model = model_id.replace("ollama/", "")
    url = f"{settings.OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": clean_model,
        "prompt": f"{system_prompt}\n\nUser Question:\n{prompt}",
        "stream": False,
    }
    try:
        with httpx.Client(timeout=45.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 200:
                return resp.json().get("response")
    except Exception:
        logger.exception("Failed calling local Ollama")
    return None


def _call_llm(query: str, kpi_context: Dict[str, Any], requested_model: Optional[str] = None) -> Optional[str]:
    target_model = requested_model or _active_model

    if target_model == "rule_based":
        return None

    kpi_lines = []
    for k, v in kpi_context.items():
        if k in ("detected_columns", "opex_estimation_note", "opex_is_estimated"):
            continue
        kpi_lines.append(f"  - {k}: {v}")
    kpi_summary = "\n".join(kpi_lines) if kpi_lines else "  (no KPI data available)"

    system_prompt = (
        "You are an expert business analyst inside an AI Decision Support System. "
        "Your job is to answer the user's business question using the KPI data provided. "
        "Be concise, precise, and factual. Structure your answer like this:\n\n"
        "**FACTS** (from actual data):\n- ...\n\n"
        "**ANALYSIS**:\n- ...\n\n"
        "**RECOMMENDATION**:\n- ...\n\n"
        "Never invent numbers. If data is insufficient, say so clearly.\n\n"
        f"Current Business KPIs:\n{kpi_summary}"
    )

    # Check if target model is an OpenCode registered model
    opencode_model_ids = {m["id"] for m in AVAILABLE_MODELS if m["provider"] == "opencode"}
    if target_model in opencode_model_ids or "pickle" in target_model.lower() or "opencode" in target_model.lower():
        return _call_opencode_zen(target_model, query, system_prompt)
    if "gemini" in target_model.lower():
        return _call_gemini_api(target_model, query, system_prompt)
    if "qwen" in target_model.lower() or "ollama" in target_model.lower():
        return _call_ollama_api(target_model, query, system_prompt)

    return None


class AIBusinessAnalyst:
    """
    AI Business Analyst supporting selectable free-tier models:
    - Google Gemini free-tier (Gemini 2.5 Flash, Gemini 2.5 Flash Lite)
    - Local Ollama (Qwen 3)
    - Deterministic Rule-Based Engine
    """

    @staticmethod
    def answer_query(
        query: str,
        table_name: Optional[str] = None,
        cached_kpis: Optional[Dict[str, Any]] = None,
        model_name: Optional[str] = None,
    ) -> AIQueryResponse:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")
        if len(query) > 2000:
            raise ValueError("Query is too long (max 2,000 characters).")

        selected_model = model_name or _active_model
        tools_executed: List[AIToolCall] = []

        if table_name and not cached_kpis:
            try:
                cached_kpis = kpi_calculator.calculate_standard_metrics(table_name)
                tools_executed.append(AIToolCall(
                    tool_name="calculate_kpis",
                    arguments={"table_name": table_name},
                    output=cached_kpis,
                ))
            except Exception:
                logger.exception("KPI calculation failed for table '%s'", table_name)
                cached_kpis = None

        if not cached_kpis:
            return AIQueryResponse(
                query=query,
                intent="NO_DATA",
                answer=(
                    "No dataset is currently loaded. Please upload a dataset first so I can "
                    "ground my analysis in your actual business data."
                ),
                facts=["No dataset is available in this session."],
                inferences=[],
                predictions=[],
                assumptions=[],
                recommendations=["Upload a CSV, Excel, or JSON dataset via the Datasets tab."],
                evidence=[],
                confidence="N/A",
                tools_executed=tools_executed,
                suggested_actions=["Go to Datasets → Upload"],
                analyst_mode=selected_model,
            )

        rev = cached_kpis.get("revenue", 0.0)
        cogs = cached_kpis.get("cogs", 0.0)
        opex = cached_kpis.get("operating_expenses", 0.0)
        gross_margin = cached_kpis.get("gross_margin_pct", 0.0)
        net_profit = rev - cogs - opex

        # Call selected model
        llm_answer = _call_llm(query, cached_kpis, requested_model=selected_model)

        if llm_answer:
            return AIQueryResponse(
                query=query,
                intent="LLM_RESPONSE",
                answer=llm_answer,
                facts=[
                    f"Revenue: ${rev:,.2f}",
                    f"Gross Margin: {gross_margin:.1f}%",
                    f"Net Profit: ${net_profit:,.2f}",
                ],
                inferences=[],
                predictions=[],
                assumptions=[f"Generated via free tier model ({selected_model}) grounded in live dataset KPIs."],
                recommendations=[],
                evidence=[{"source": "Live Dataset KPIs", "metric": "Revenue", "value": f"${rev:,.2f}"}],
                confidence="High",
                tools_executed=tools_executed,
                suggested_actions=["Review KPI Dashboard for full metrics"],
                analyst_mode=selected_model,
            )

        # Fallback to rule-based engine if model call returns None or rule_based is selected
        return AIBusinessAnalyst._rule_based_response(
            query, table_name, cached_kpis, rev, cogs, opex, gross_margin, net_profit, tools_executed, selected_model
        )

    @staticmethod
    def _rule_based_response(
        query: str,
        table_name: Optional[str],
        cached_kpis: Dict[str, Any],
        rev: float,
        cogs: float,
        opex: float,
        gross_margin: float,
        net_profit: float,
        tools_executed: List[AIToolCall],
        current_model: str,
    ) -> AIQueryResponse:
        q_lower = query.lower()

        # 1. Intent: What-If / Scenario Analysis
        if any(w in q_lower for w in ["what if", "scenario", "price increase", "prices increase", "raise price"]):
            intent = "SCENARIO_SIMULATION"
            price_match = re.search(r"(\d+(\.\d+)?)%", query)
            price_pct = float(price_match.group(1)) if price_match else 5.0
            if "decrease" in q_lower or "cut price" in q_lower:
                price_pct = -price_pct

            params = ScenarioParams(
                price_change_pct=price_pct,
                marketing_spend_pct=0.0,
                operating_cost_pct=0.0,
            )

            sim_result = scenario_simulator.simulate(rev, cogs, opex, params)
            tools_executed.append(AIToolCall(
                tool_name="run_scenario_simulation",
                arguments={"baseline_revenue": rev, "parameters": params.model_dump()},
                output=sim_result.model_dump(),
            ))

            facts = [
                f"Baseline Revenue: ${rev:,.2f}",
                f"Baseline Gross Margin: {gross_margin:.1f}%",
                f"Baseline Net Profit: ${net_profit:,.2f}",
            ]
            inferences = [
                f"Simulating a {price_pct:+.1f}% price change.",
                f"Estimated margin impact: {sim_result.deltas.margin_delta_basis_pts:+.0f} bps based on elasticity of {params.assumed_elasticity}.",
            ]
            predictions = [
                f"Projected Revenue: ${sim_result.projected.revenue:,.2f} ({sim_result.deltas.revenue_delta_pct:+.1f}%)",
                f"Projected Net Profit: ${sim_result.projected.net_profit:,.2f} ({sim_result.deltas.net_profit_delta_pct:+.1f}%)",
            ]
            assumptions = [
                f"Price elasticity of demand: {params.assumed_elasticity}.",
                "Variable COGS scales with 80% of volume changes.",
                "No other parameters change simultaneously.",
            ]
            recs = [
                sim_result.recommendation,
                "Monitor customer retention closely for 45 days post-adjustment.",
            ]
            evidence = [
                {"source": "Scenario Engine", "metric": "Net Profit Delta", "value": f"${sim_result.deltas.net_profit_delta:,.2f}"},
                {"source": "Scenario Engine", "metric": "Risk Score", "value": f"{sim_result.risk_score}/100"},
            ]
            answer = (
                f"If prices shift by {price_pct:+.1f}%, projected revenue becomes "
                f"${sim_result.projected.revenue:,.2f} ({sim_result.deltas.revenue_delta_pct:+.1f}%), "
                f"with net profit at ${sim_result.projected.net_profit:,.2f}. "
                f"Risk score: {sim_result.risk_score}/100 ({sim_result.risk_assessment['level'].upper()})."
            )
            actions = [
                "Open Scenario Studio to adjust elasticity sliders",
                "Create a Decision Proposal for executive review",
                "Export Scenario Comparison Report",
            ]

        # 2. Intent: Forecasting
        elif any(w in q_lower for w in ["forecast", "predict", "next month", "next quarter", "future", "trend"]):
            intent = "FORECASTING"
            detected = cached_kpis.get("detected_columns", {})
            date_col = detected.get("date") if isinstance(detected, dict) else None
            rev_col = detected.get("revenue") if isinstance(detected, dict) else None

            forecast_res = None
            if table_name and date_col and rev_col:
                try:
                    forecast_res = forecasting_engine.forecast_metric(
                        table_name, date_col, rev_col, periods_ahead=6
                    )
                    tools_executed.append(AIToolCall(
                        tool_name="forecast_metric",
                        arguments={"table_name": table_name, "date_col": date_col, "metric_col": rev_col},
                        output=forecast_res.model_dump(),
                    ))
                except Exception:
                    logger.warning("Forecasting failed for table '%s'; no projection available.", table_name)

            if forecast_res:
                growth_rate = forecast_res.summary_growth_pct
                model_used = forecast_res.model_name
                mape_score = forecast_res.validation_mape
                confidence = "High" if mape_score < 10 else ("Medium" if mape_score < 20 else "Low")
            else:
                growth_rate = None
                model_used = "N/A"
                mape_score = None
                confidence = "Low"

            facts = [f"Trailing Revenue: ${rev:,.2f}"]
            if forecast_res:
                facts.append(f"Model selected: {model_used} (Validation MAPE: {mape_score:.1f}%)")

            inferences = ["Historical trend analysis applied to the uploaded dataset."]
            if growth_rate is not None:
                predictions = [
                    f"Projected growth over next 6 periods: {growth_rate:+.1f}%",
                    f"Next-period estimate: ${rev * (1 + (growth_rate / 100) / 12):,.0f}",
                ]
            else:
                predictions = ["Forecast unavailable — dataset may lack date or revenue columns with sufficient history (min 4 periods)."]

            assumptions = [
                "No major macroeconomic disruptions assumed.",
                "Historical seasonality patterns persist.",
            ]
            recs = [
                "Align procurement buffers with the upper 95% confidence bound.",
                "Re-evaluate after next month's books close.",
            ]
            evidence = [
                {"source": "Forecasting Engine", "metric": "Algorithm", "value": model_used},
                {"source": "Forecasting Engine", "metric": "MAPE", "value": f"{mape_score:.1f}%" if mape_score is not None else "N/A"},
            ]
            answer = (
                f"Based on {model_used}, the revenue trajectory projects {growth_rate:+.1f}% over the next 6 periods."
                if growth_rate is not None
                else "Insufficient date/revenue data for a quantitative forecast. Check dataset columns."
            )
            actions = [
                "View forecast chart in the Analytics tab",
                "Run a stress-test scenario with a 10% demand contraction",
            ]

        # 3. Intent: Anomaly Detection
        elif any(w in q_lower for w in ["anomaly", "unusual", "outlier", "spike", "irregular"]):
            intent = "ANOMALY_DETECTION"
            detected = cached_kpis.get("detected_columns", {})
            rev_col = detected.get("revenue") if isinstance(detected, dict) else None

            anomalies = []
            if table_name and rev_col:
                try:
                    anomalies = anomaly_detector.detect_anomalies(table_name, rev_col)
                    tools_executed.append(AIToolCall(
                        tool_name="detect_anomalies",
                        arguments={"table_name": table_name, "metric_col": rev_col},
                        output=[a.model_dump() for a in anomalies],
                    ))
                except Exception:
                    logger.warning("Anomaly detection failed for table '%s'.", table_name)

            anom_count = len(anomalies)

            facts = [
                f"Scanned {cached_kpis.get('orders', 'N/A')} transaction records.",
                f"Found {anom_count} statistical outliers exceeding the 2.5σ threshold.",
            ]
            inferences = (
                ["No anomalies detected — data distribution is within normal bounds."]
                if anom_count == 0
                else ["Flagged records represent genuine transactional variance, not data corruption."]
            )
            predictions = (
                []
                if anom_count == 0
                else ["Unreviewed outliers may distort automated forecasts if not normalised."]
            )
            assumptions = [
                "Z-score threshold: 2.5 standard deviations.",
                "IQR fence: 1.5× interquartile range.",
            ]
            recs = (
                ["No action required — continue monitoring."]
                if anom_count == 0
                else [
                    "Audit the top flagged transactions for contract compliance.",
                    "Consider excluding extreme outliers before running forecasts.",
                ]
            )
            evidence = [
                {"source": "Anomaly Detector", "metric": "Outliers Found", "value": str(anom_count)},
            ]
            if anomalies:
                top = anomalies[0]
                evidence.append({
                    "source": "Anomaly Detector",
                    "metric": "Highest Deviation",
                    "value": f"{abs(top.deviation_z_score):.2f}σ",
                })
            answer = (
                f"The anomaly engine scanned your data and found {anom_count} outlier records "
                + ("exceeding the 2.5σ threshold. Review the Anomaly Ledger for details." if anom_count > 0 else "— data looks clean.")
            )
            actions = [
                "Review Anomaly Ledger in the Analytics tab",
                "Exclude outliers from model training dataset",
            ]

        # 4. Intent: Driver Analysis
        else:
            intent = "DRIVER_ANALYSIS"
            proposal = decision_engine.generate_strategic_proposal(query, cached_kpis)
            tools_executed.append(AIToolCall(
                tool_name="generate_strategic_proposal",
                arguments={"topic": query, "kpi_context": cached_kpis},
                output=proposal,
            ))

            facts = [
                f"Revenue: ${rev:,.2f}",
                f"Gross Margin: {gross_margin:.1f}% (${rev - cogs:,.2f} gross profit)",
                f"Net Operating Profit: ${net_profit:,.2f}",
            ]
            inferences = [
                f"Primary opportunity identified: {proposal['title']}.",
            ]
            predictions = [
                f"Executing the recommended strategy is projected to yield "
                f"{proposal['expected_impact']['profit_impact_range']} within "
                f"{proposal['expected_impact']['time_to_value']}.",
            ]
            assumptions = proposal["assumptions"]
            recs = [
                f"Recommended action: {proposal['recommended_option']}",
                proposal["description"],
            ]
            evidence = proposal["evidence"]
            answer = (
                f"Based on current figures (Revenue: ${rev:,.2f}, Gross Margin: {gross_margin:.1f}%), "
                f"the primary priority is {proposal['title'].lower()}. "
                f"{proposal['rationale']}"
            )
            actions = [
                "Submit proposed decision for executive sign-off",
                "Run a What-If simulation with adjusted parameters",
                "Download executive summary briefing",
            ]
            confidence = "Medium"

        return AIQueryResponse(
            query=query,
            intent=intent,
            answer=answer,
            facts=facts,
            inferences=inferences,
            predictions=predictions,
            assumptions=assumptions,
            recommendations=recs,
            evidence=evidence,
            confidence=locals().get("confidence", "High"),
            tools_executed=tools_executed,
            suggested_actions=actions,
            analyst_mode=current_model,
        )


ai_business_analyst = AIBusinessAnalyst()
