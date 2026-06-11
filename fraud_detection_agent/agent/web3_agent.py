"""
SurakshaNet Web3 Fraud Detection Agent
=======================================
A LangChain ReAct agent powered by Google Gemini Flash (free tier) that can:

  1. run_fraud_pipeline    – execute the full ML anomaly + risk scoring pipeline
  2. get_top_risky_hospitals – query top N hospitals by risk score
  3. get_suspicious_claims   – fetch flagged claims (filtered by state/district)
  4. explain_claim           – LLM explanation of why a claim looks suspicious
  5. generate_audit_report   – produce a structured text report
  6. anchor_to_algorand      – hash + anchor the report on Algorand TestNet
  7. query_blockchain_tx     – look up a previously anchored transaction

All blockchain work uses algokit-utils (official Algorand Python SDK v2 wrapper).
LLM: google-generativeai (Gemini 1.5 Flash) — free tier, no credit card needed.

Setup (one-time):
    pip install langchain langchain-google-genai algokit-utils google-generativeai
    # Get a free Gemini API key at https://aistudio.google.com/
    # Add GEMINI_API_KEY=... to your .env
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime
from typing import Any, Optional

from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.tools import tool
from langchain_groq import ChatGroq

# ── Internal imports ──────────────────────────────────────────────────────────
from fraud_detection_agent.blockchain.algorand_client import AlgorandClient
from fraud_detection_agent.database.db_setup import init_csv_and_db
from fraud_detection_agent.models.anomaly_model import AnomalyDetector
from fraud_detection_agent.preprocessing.preprocess import build_features_from_db
from fraud_detection_agent.reports.report_generator import generate_fraud_report
from fraud_detection_agent.scoring.risk_scoring import (
    aggregate_hospital_risk,
    apply_rule_based_flags,
    compute_risk_scores,
)
from fraud_detection_agent.config import ANOMALY_THRESHOLD, DATASET_SIZE

# ── Pipeline cache (shared with main.py) ─────────────────────────────────────
_pipeline_cache: dict[str, Any] = {}


def _run_pipeline(force_refresh: bool = False) -> dict[str, Any]:
    """Run (or return cached) full fraud detection pipeline."""
    cache_key = "default"
    if not force_refresh and cache_key in _pipeline_cache:
        return _pipeline_cache[cache_key]

    print("[Agent] Running fraud detection pipeline...")
    init_csv_and_db(n_rows=DATASET_SIZE, reuse_existing=True)
    features_data = build_features_from_db()
    detector = AnomalyDetector()
    anomaly_results = detector.fit_predict(features_data.features)

    df = features_data.enriched.copy()
    if "state" not in df.columns:
        df["state"] = "Unknown"

    df["anomaly_score_model"] = anomaly_results.combined_score
    df["anomaly_label"] = (anomaly_results.combined_score > ANOMALY_THRESHOLD).astype(int)
    df_scored = compute_risk_scores(df, anomaly_results.combined_score)
    df_flagged = apply_rule_based_flags(df_scored)
    hospital_df = aggregate_hospital_risk(df_flagged)

    result = {"claims": df_flagged, "hospital_risk": hospital_df}
    _pipeline_cache[cache_key] = result
    print(f"[Agent] Pipeline complete — {len(df_flagged)} claims, {len(hospital_df)} hospitals")
    return result


# ═══════════════════════════════════════════════════════════════════════════════
#  TOOLS — these are what the LangChain agent can call
# ═══════════════════════════════════════════════════════════════════════════════

@tool
def run_fraud_pipeline(force_refresh: str = "false") -> str:
    """
    Run the full fraud detection ML pipeline across all claims in the database.
    Returns a summary of total claims processed, suspicious claims found, and
    hospital risk distribution. Use force_refresh='true' to bypass cache.
    """
    refresh = force_refresh.lower() == "true"
    output = _run_pipeline(force_refresh=refresh)
    claims_df = output["claims"]
    hosp_df = output["hospital_risk"]

    suspicious = int(((claims_df["anomaly_label"] == 1) | (claims_df["any_rule_flag"])).sum())
    dist = hosp_df["risk_category_overall"].value_counts().to_dict()

    return json.dumps({
        "status": "complete",
        "total_claims": len(claims_df),
        "suspicious_claims": suspicious,
        "total_hospitals": len(hosp_df),
        "risk_distribution": dist,
        "fraud_amount_inr": round(float(
            claims_df[
                (claims_df["anomaly_label"] == 1) | (claims_df["any_rule_flag"])
            ]["claim_amount"].sum()
        ), 2),
    }, indent=2)


@tool
def get_top_risky_hospitals(input: str = "5") -> str:
    """
    Retrieve the top N hospitals ranked by average fraud risk score.
    Input can be just a number like "5", or JSON like {"limit": "5", "state": "Maharashtra"}.
    Optionally filter by state name (e.g. 'Maharashtra', 'Delhi').
    """
    # Parse flexible input
    limit = 5
    state = "All"
    if input.strip().startswith("{"):
        try:
            params = json.loads(input)
            limit = int(params.get("limit", 5))
            state = params.get("state", "All")
        except Exception:
            pass
    else:
        try:
            limit = int(input.strip())
        except Exception:
            pass

    output = _run_pipeline()
    hosp_df = output["hospital_risk"].copy()

    if state != "All":
        hosp_df = hosp_df[hosp_df["state"] == state]

    top = hosp_df.sort_values("avg_risk_score", ascending=False).head(limit)

    results = []
    for _, row in top.iterrows():
        results.append({
            "hospital_id": row["hospital_id"],
            "hospital_name": str(row.get("hospital_name", row["hospital_id"])),
            "state": str(row.get("state", "Unknown")),
            "district": str(row.get("district", "Unknown")),
            "hospital_type": str(row["hospital_type"]),
            "avg_risk_score": round(float(row["avg_risk_score"]), 2),
            "risk_category": str(row["risk_category_overall"]),
            "high_risk_claims": int(row["high_risk_claims"]),
            "suspicious_claims": int(row["suspicious_claims"]),
            "rule_flags": int(row["any_rule_flags"]),
        })
    return json.dumps(results, indent=2)


@tool
def get_suspicious_claims(input: str = "10") -> str:
    """
    Retrieve the most suspicious claims sorted by risk score.
    Input can be a number like "10", or JSON like {"limit": "10", "state": "Delhi", "district": "All"}.
    Optionally filter by state and/or district.
    """
    limit = 10
    state = "All"
    district = "All"
    if input.strip().startswith("{"):
        try:
            params = json.loads(input)
            limit = int(params.get("limit", 10))
            state = params.get("state", "All")
            district = params.get("district", "All")
        except Exception:
            pass
    else:
        try:
            limit = int(input.strip())
        except Exception:
            pass

    output = _run_pipeline()
    claims_df = output["claims"].copy()

    if state != "All":
        claims_df = claims_df[claims_df["state"] == state]
    if district != "All":
        claims_df = claims_df[claims_df["district"] == district]

    suspicious = claims_df[
        (claims_df["anomaly_label"] == 1) | (claims_df["any_rule_flag"])
    ].sort_values("risk_score", ascending=False).head(limit)

    results = []
    for _, row in suspicious.iterrows():
        results.append({
            "claim_id": str(row["claim_id"]),
            "hospital_id": str(row["hospital_id"]),
            "patient_id": str(row["patient_id"]),
            "claim_amount_inr": round(float(row["claim_amount"]), 2),
            "risk_score": round(float(row["risk_score"]), 2),
            "risk_category": str(row["risk_category"]),
            "anomaly_flag": bool(row["anomaly_label"] == 1),
            "rule_upcoding": bool(row.get("rule_upcoding", False)),
            "rule_ghost_billing": bool(row.get("rule_ghost_billing", False)),
            "rule_claim_surge": bool(row.get("rule_claim_surge", False)),
            "length_of_stay": int(row.get("length_of_stay", 0)),
        })
    return json.dumps(results, indent=2)


@tool
def explain_claim(claim_id: str) -> str:
    """
    Generate a plain-English explanation of why a specific claim (by claim_id)
    is considered suspicious. Returns detailed reasoning based on the claim's features.
    This tool uses the LLM's reasoning — call it after fetching claim data.
    """
    output = _run_pipeline()
    claims_df = output["claims"]
    match = claims_df[claims_df["claim_id"] == claim_id]

    if match.empty:
        return f"Claim {claim_id} not found in the current dataset."

    row = match.iloc[0]
    flags = []
    if row.get("rule_upcoding"):
        flags.append(f"up-coding (claim ₹{row['claim_amount']:,.0f} vs district avg ₹{row.get('district_proc_avg_cost', 0):,.0f})")
    if row.get("rule_ghost_billing"):
        flags.append(f"ghost billing (patient filed {row.get('patient_claim_count_hosp_month', '?')} claims this month at same hospital)")
    if row.get("rule_claim_surge"):
        flags.append("claim surge (hospital monthly volume spike > 150%)")
    if row.get("anomaly_label") == 1:
        flags.append(f"ML anomaly (combined anomaly score: {row.get('anomaly_score_model', 0):.3f})")

    summary = {
        "claim_id": claim_id,
        "hospital": str(row.get("hospital_name", row["hospital_id"])),
        "patient_id": str(row["patient_id"]),
        "amount_inr": round(float(row["claim_amount"]), 2),
        "risk_score": round(float(row["risk_score"]), 2),
        "length_of_stay_days": int(row.get("length_of_stay", 0)),
        "procedure_code": str(row.get("procedure_code", "?")),
        "flags_detected": flags if flags else ["No specific rule flags — ML anomaly only"],
        "state": str(row.get("state", "Unknown")),
        "district": str(row.get("district", "Unknown")),
    }
    return json.dumps(summary, indent=2)


@tool
def generate_audit_report(input: str = "All") -> str:
    """
    Generate a full fraud audit report.
    Input can be a state name like "Maharashtra", "All", or JSON like {"state": "Delhi", "district": "All"}.
    Use 'All' for no filtering.
    """
    state = "All"
    district = "All"
    if input.strip().startswith("{"):
        try:
            params = json.loads(input)
            state = params.get("state", "All")
            district = params.get("district", "All")
        except Exception:
            pass
    else:
        val = input.strip()
        if val and val != "All":
            state = val

    output = _run_pipeline()
    claims_df = output["claims"].copy()
    hosp_df = output["hospital_risk"].copy()

    if state != "All":
        claims_df = claims_df[claims_df["state"] == state]
        hosp_df = hosp_df[hosp_df["state"] == state]
    if district != "All":
        claims_df = claims_df[claims_df["district"] == district]
        hosp_df = hosp_df[hosp_df["district"] == district]

    report_text, report_path = generate_fraud_report(hosp_df, claims_df)
    return json.dumps({
        "status": "generated",
        "report_path": report_path,
        "report_preview": report_text[:800] + "..." if len(report_text) > 800 else report_text,
        "total_claims_in_scope": len(claims_df),
        "filter_state": state,
        "filter_district": district,
    }, indent=2)


@tool
def anchor_to_algorand(report_text: str) -> str:
    """
    Anchor a fraud report to the Algorand TestNet blockchain.
    Takes the report text, computes a SHA-256 hash, and stores it as an
    immutable transaction note. Returns the transaction ID and wallet address.
    Always use this after generating an audit report for tamper-proof compliance.
    """
    client = AlgorandClient()
    report_hash = hashlib.sha256(report_text.encode()).hexdigest()

    metadata = {
        "timestamp": datetime.now().isoformat(),
        "report_hash": report_hash,
        "app": "SurakshaNet",
        "anchored_by": "SurakshaNet Web3 Agent",
        "total_chars": len(report_text),
    }

    tx_id = client.store_report_on_chain(report_text, metadata)

    if tx_id:
        return json.dumps({
            "status": "anchored",
            "blockchain": "Algorand TestNet",
            "transaction_id": tx_id,
            "wallet_address": client.sender_address,
            "report_hash_sha256": report_hash,
            "explorer_url": f"https://testnet.explorer.perawallet.app/tx/{tx_id}",
        }, indent=2)
    else:
        return json.dumps({
            "status": "failed",
            "reason": "No valid Algorand mnemonic configured. Set ALGORAND_MNEMONIC in .env",
            "report_hash_sha256": report_hash,
        }, indent=2)


@tool
def query_blockchain_tx(tx_id: str) -> str:
    """
    Look up details of a previously anchored transaction on Algorand TestNet.
    Pass the transaction ID returned by anchor_to_algorand.
    Returns confirmation round, timestamp, and note content.
    """
    try:
        from algosdk.v2client import algod
        algod_client = algod.AlgodClient("", "https://testnet-api.algonode.cloud")
        info = algod_client.pending_transaction_info(tx_id)

        note_raw = info.get("txn", {}).get("txn", {}).get("note", "")
        if note_raw:
            import base64
            note_decoded = base64.b64decode(note_raw).decode("utf-8", errors="replace")
            try:
                note_parsed = json.loads(note_decoded)
            except Exception:
                note_parsed = note_decoded
        else:
            note_parsed = None

        return json.dumps({
            "tx_id": tx_id,
            "confirmed_round": info.get("confirmed-round"),
            "note": note_parsed,
            "explorer_url": f"https://testnet.explorer.perawallet.app/tx/{tx_id}",
        }, indent=2)
    except Exception as exc:
        return json.dumps({
            "tx_id": tx_id,
            "error": str(exc),
            "note": "Transaction may still be pending or ID is invalid.",
        }, indent=2)


# ═══════════════════════════════════════════════════════════════════════════════
#  AGENT SETUP
# ═══════════════════════════════════════════════════════════════════════════════

TOOLS = [
    run_fraud_pipeline,
    get_top_risky_hospitals,
    get_suspicious_claims,
    explain_claim,
    generate_audit_report,
    anchor_to_algorand,
    query_blockchain_tx,
]

_AGENT_SYSTEM_PROMPT = """You are SurakshaNet, an advanced Web3 AI fraud detection agent for \
India's Ayushman Bharat healthcare insurance scheme.

Your job is to detect, analyse, and report fraudulent hospital claims using machine learning, \
rule-based heuristics, and immutable blockchain anchoring on Algorand.

You have access to these tools:
{tools}

Tool names: {tool_names}

ALWAYS follow this reasoning format exactly:

Question: the input question or task
Thought: think step by step about what to do
Action: one of [{tool_names}]
Action Input: the input to the tool (use simple strings or JSON)
Observation: the result of the tool
... (repeat Thought/Action/Observation as needed)
Thought: I now know the final answer
Final Answer: a clear, concise response to the original question

Rules:
- Run the pipeline first if you need fresh data
- When asked to investigate fraud, always check both hospitals AND claims
- Always anchor audit reports to Algorand blockchain for compliance
- Present numbers in Indian Rupees (₹) where relevant
- Be specific and actionable — name the hospitals, cite the amounts

Begin!

Question: {input}
Thought: {agent_scratchpad}"""


def build_agent() -> AgentExecutor:
    """
    Build and return the SurakshaNet Web3 agent.
    Requires GROQ_API_KEY in environment (free at https://console.groq.com/).
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GROQ_API_KEY not set. Get a free key at https://console.groq.com/ "
            "and add it to your .env file."
        )

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",  # free tier — 14,400 req/day, no credit card
        groq_api_key=api_key,
        temperature=0.1,
        max_tokens=2048,
    )

    prompt = PromptTemplate.from_template(_AGENT_SYSTEM_PROMPT)
    agent = create_react_agent(llm=llm, tools=TOOLS, prompt=prompt)

    return AgentExecutor(
        agent=agent,
        tools=TOOLS,
        verbose=True,
        max_iterations=8,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  FASTAPI INTEGRATION — agent endpoint
# ═══════════════════════════════════════════════════════════════════════════════

_agent_executor: Optional[AgentExecutor] = None


def get_agent() -> AgentExecutor:
    """Singleton: build agent once, reuse across requests."""
    global _agent_executor
    if _agent_executor is None:
        _agent_executor = build_agent()
    return _agent_executor


async def run_agent_query(query: str) -> dict[str, Any]:
    """
    Run a natural-language query through the Web3 agent.
    Suitable for calling from a FastAPI endpoint.
    """
    agent = get_agent()
    try:
        result = agent.invoke({"input": query})
        # result is always a dict from AgentExecutor, but guard defensively
        if isinstance(result, dict):
            output = result.get("output", "")
            steps = len(result.get("intermediate_steps", []))
        elif isinstance(result, list):
            # Shouldn't happen, but handle gracefully
            output = str(result[-1]) if result else ""
            steps = 0
        else:
            output = str(result)
            steps = 0

        return {
            "status": "success",
            "query": query,
            "answer": output,
            "steps": steps,
        }
    except Exception as exc:
        return {
            "status": "error",
            "query": query,
            "answer": "",
            "error": str(exc),
        }
