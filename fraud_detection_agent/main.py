from __future__ import annotations
import os
from dotenv import load_dotenv
load_dotenv()

from datetime import datetime
from typing import Any, Dict, List
import pandas as pd

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler

from fraud_detection_agent.agent.monitor import persist_hospital_snapshot
from fraud_detection_agent.blockchain.algorand_client import AlgorandClient
from fraud_detection_agent.config import ALLOWED_ORIGINS, ANOMALY_THRESHOLD, DATASET_SIZE
from fraud_detection_agent.database.db_setup import init_csv_and_db
from fraud_detection_agent.models.anomaly_model import AnomalyDetector
from fraud_detection_agent.preprocessing.preprocess import build_features_from_db
from fraud_detection_agent.reports.report_generator import generate_fraud_report
from fraud_detection_agent.scoring.risk_scoring import (
    aggregate_hospital_risk,
    apply_rule_based_flags,
    compute_risk_scores,
)

print("-" * 50)
print("AYUSHGUARD SERVER BOOTING...")
print(f"ALGORAND WALLET: {os.getenv('ALGORAND_MNEMONIC')[:10] if os.getenv('ALGORAND_MNEMONIC') else 'NOT SET'}...")
print("-" * 50)

app = FastAPI(title="Ayushman Bharat Fraud Detection Agent - Stage 1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Background scheduler: refresh snapshots every hour ──────────────────────
_scheduler = BackgroundScheduler()

@app.on_event("startup")
def _start_scheduler():
    def _hourly_snapshot():
        try:
            output = run_full_pipeline(persist_snapshot=True, force_refresh=True)
            print(f"[Scheduler] Snapshot refreshed — {len(output['hospital_risk'])} hospitals")
        except Exception as exc:
            print(f"[Scheduler] Snapshot failed: {exc}")

    _scheduler.add_job(_hourly_snapshot, "interval", hours=1, id="hourly_snapshot")
    _scheduler.start()
    print("[Scheduler] Started — hourly snapshots enabled")

@app.on_event("shutdown")
def _stop_scheduler():
    _scheduler.shutdown(wait=False)

# ── Health check ─────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok"}

class HospitalRisk(BaseModel):
    hospital_id: str
    hospital_name: str
    state: str
    district: str
    hospital_type: str
    total_claims: int
    avg_risk_score: float
    high_risk_claims: int
    suspicious_claims: int
    any_rule_flags: int
    risk_category_overall: str

class LoginRequest(BaseModel):
    username: str
    password: str

_pipeline_cache = {}

@app.post("/login")
def login(request: LoginRequest):
    from fraud_detection_agent.database.db_setup import get_db_connection
    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (request.username, request.password)
    ).fetchone()
    conn.close()
    
    if user:
        return {"status": "success", "username": request.username}
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Invalid credentials")

def run_full_pipeline(
    focus_hospital_type: str | None = None,
    persist_snapshot: bool = True,
    force_refresh: bool = False
) -> Dict[str, Any]:
    cache_key = f"{focus_hospital_type}_{persist_snapshot}"
    if not force_refresh and cache_key in _pipeline_cache:
        return _pipeline_cache[cache_key]

    df_raw, _ = init_csv_and_db(n_rows=DATASET_SIZE, reuse_existing=True)
    features_data = build_features_from_db()
    detector = AnomalyDetector()
    anomaly_results = detector.fit_predict(features_data.features)
    df_enriched = features_data.enriched.copy()
    if "state" not in df_enriched.columns:
        df_enriched["state"] = "Unknown"
    
    df_enriched["anomaly_score_model"] = anomaly_results.combined_score
    df_enriched["anomaly_label"] = (anomaly_results.combined_score > ANOMALY_THRESHOLD).astype(int)
    df_scored = compute_risk_scores(df_enriched, anomaly_results.combined_score)
    df_flagged = apply_rule_based_flags(df_scored)
    hospital_risk_df = aggregate_hospital_risk(df_flagged)

    if focus_hospital_type:
        claims_focus = df_flagged[df_flagged["hospital_type"] == focus_hospital_type].copy()
        hosp_focus = hospital_risk_df[
            hospital_risk_df["hospital_type"] == focus_hospital_type
        ].copy()
    else:
        claims_focus = df_flagged
        hosp_focus = hospital_risk_df

    if persist_snapshot:
        try:
            persist_hospital_snapshot(hosp_focus)
        except Exception:
            pass

    output = {
        "claims": claims_focus,
        "hospital_risk": hosp_focus,
        "claims_all": df_flagged,
        "hospital_risk_all": hospital_risk_df,
    }
    
    _pipeline_cache[cache_key] = output
    return output

@app.get("/get-high-risk-hospitals", response_model=List[HospitalRisk])
def get_high_risk_hospitals(limit: int = 10, hospital_type: str = None):
    pipeline_output = run_full_pipeline(focus_hospital_type=hospital_type)
    hospital_df = pipeline_output["hospital_risk"]
    top = hospital_df.sort_values(by="avg_risk_score", ascending=False).head(limit)
    return [
        HospitalRisk(
            hospital_id=row["hospital_id"],
            hospital_name=str(row.get("hospital_name", row["hospital_id"])),
            state=str(row.get("state", "Unknown")),
            district=row["district"],
            hospital_type=row["hospital_type"],
            total_claims=int(row["total_claims"]),
            avg_risk_score=float(row["avg_risk_score"]),
            high_risk_claims=int(row["high_risk_claims"]),
            suspicious_claims=int(row["suspicious_claims"]),
            any_rule_flags=int(row["any_rule_flags"]),
            risk_category_overall=str(row["risk_category_overall"]),
        )
        for _, row in top.iterrows()
    ]

@app.get("/get-claim-anomalies")
def get_claim_anomalies(limit: int = 50, hospital_type: str = None, state: str = "All", district: str = "All"):
    pipeline_output = run_full_pipeline(focus_hospital_type=hospital_type)
    claims_df = pipeline_output["claims"]
    if state != "All":
        claims_df = claims_df[claims_df["state"] == state]
    if district != "All":
        claims_df = claims_df[claims_df["district"] == district]
    suspicious = claims_df[
        (claims_df["anomaly_label"] == 1) | (claims_df["any_rule_flag"])
    ].copy()
    suspicious = suspicious.sort_values(by="risk_score", ascending=False).head(limit)
    return suspicious.to_dict(orient="records")

@app.get("/generate-report")
def generate_report(hospital_type: str = None, state: str = "All", district: str = "All"):
    print(f"--- GENERATE REPORT CALLED ({state}, {district}) ---")
    pipeline_output = run_full_pipeline(focus_hospital_type=hospital_type)
    claims_df = pipeline_output["claims"]
    hospitals_df = pipeline_output["hospital_risk"]
    
    if state != "All":
        claims_df = claims_df[claims_df["state"] == state]
        hospitals_df = hospitals_df[hospitals_df["state"] == state]
    if district != "All":
        claims_df = claims_df[claims_df["district"] == district]
        hospitals_df = hospitals_df[hospitals_df["district"] == district]

    report_text, report_path = generate_fraud_report(hospitals_df, claims_df)
    
    print("ACTION: Generating Quantum Seal...")
    try:
        from fraud_detection_agent.blockchain.quantum_client import get_quantum_client
        quantum_seal = get_quantum_client().create_quantum_seal(report_text)
    except Exception as e:
        print(f"Failed to generate quantum seal: {e}")
        quantum_seal = None

    print("ACTION: Contacting Algorand Blockchain...")
    blockchain_client = AlgorandClient()
    
    metadata = {
        "timestamp": datetime.now().isoformat(),
        "total_claims": len(claims_df),
        "suspicious_count": int(((claims_df["anomaly_label"] == 1) | (claims_df["any_rule_flag"])).sum()),
    }
    if quantum_seal:
        metadata["quantum_seal_token"] = quantum_seal.get("quantum_entropy_token", "")
        
    tx_id = blockchain_client.store_report_on_chain(
        report_text,
        metadata
    )
    print(f"ACTION: Blockchain Storage Complete. TXID: {tx_id}")

    return {
        "report_text": report_text,
        "report_path": report_path,
        "blockchain_tx_id": tx_id,
        "wallet_address": blockchain_client.sender_address,
        "quantum_seal": quantum_seal
    }

@app.get("/get-summary")
def get_summary(hospital_type: str = None, state: str = "All", district: str = "All"):
    pipeline_output = run_full_pipeline(focus_hospital_type=hospital_type)
    claims_df = pipeline_output["claims"]
    hosp_df = pipeline_output["hospital_risk"]
    if state != "All":
        claims_df = claims_df[claims_df["state"] == state]
        hosp_df = hosp_df[hosp_df["state"] == state]
    if district != "All":
        claims_df = claims_df[claims_df["district"] == district]
        hosp_df = hosp_df[hosp_df["district"] == district]
    total_claims = len(claims_df)
    low = int((hosp_df["risk_category_overall"] == "Low").sum())
    med = int((hosp_df["risk_category_overall"] == "Medium").sum())
    high = int((hosp_df["risk_category_overall"] == "High").sum())
    
    suspicious_claims_mask = (claims_df["anomaly_label"] == 1) | (claims_df["any_rule_flag"])
    suspicious_claims = int(suspicious_claims_mask.sum())
    total_fraud_amount = float(claims_df[suspicious_claims_mask]["claim_amount"].sum())
    total_hospitals = len(hosp_df)
    monthly = (claims_df.assign(is_suspicious=(claims_df["anomaly_label"] == 1) | (claims_df["any_rule_flag"])).groupby("month")["is_suspicious"].sum().reset_index().to_dict(orient="records"))
    
    # Advanced stats for more charts
    hosp_type_risk = (hosp_df.groupby("hospital_type")["avg_risk_score"].mean().reset_index().to_dict(orient="records"))
    
    anomaly_types = {
        "Up-coding": int(claims_df["rule_upcoding"].sum()),
        "Ghost Billing": int(claims_df["rule_ghost_billing"].sum()),
        "Claim Surge": int(claims_df["rule_claim_surge"].sum()),
        "ML Anomalies": int(claims_df["anomaly_label"].sum())
    }
    
    return {
        "stats": {
            "total_claims": total_claims, 
            "suspicious_claims": suspicious_claims, 
            "total_hospitals": total_hospitals,
            "total_fraud_amount": total_fraud_amount
        },
        "monthly_trends": monthly,
        "risk_distribution": [{"category": "Low", "count": low}, {"category": "Medium", "count": med}, {"category": "High", "count": high}],
        "hosp_type_risk": hosp_type_risk,
        "anomaly_type_counts": [{"type": k, "count": v} for k, v in anomaly_types.items()]
    }

@app.get("/get-all-hospitals")
def get_all_hospitals(hospital_type: str = None, state: str = "All", district: str = "All"):
    pipeline_output = run_full_pipeline(focus_hospital_type=hospital_type)
    hosp_df = pipeline_output["hospital_risk"]
    if state != "All":
        hosp_df = hosp_df[hosp_df["state"] == state]
    if district != "All":
        hosp_df = hosp_df[hosp_df["district"] == district]
    return hosp_df.to_dict(orient="records")

@app.get("/get-monitoring-trends")
def get_monitoring_trends(hospital_type: str = None):
    from fraud_detection_agent.agent.monitor import load_snapshots
    snap = load_snapshots(hospital_type_focus=hospital_type, limit=5000)
    if snap.empty: return []
    snap["snapshot_ts"] = pd.to_datetime(snap["snapshot_ts"])
    trend = (snap.groupby(pd.Grouper(key="snapshot_ts", freq="H"))["avg_risk_score"].mean().reset_index().sort_values("snapshot_ts"))
    trend["snapshot_ts"] = trend["snapshot_ts"].dt.strftime("%Y-%m-%d %H:%M")
    return trend.to_dict(orient="records")

@app.get("/get-claims-search")
def get_claims_search(query: str = "", limit: int = 100, state: str = "All", district: str = "All"):
    pipeline_output = run_full_pipeline()
    claims_df = pipeline_output["claims_all"]
    
    if state != "All":
        claims_df = claims_df[claims_df["state"] == state]
    if district != "All":
        claims_df = claims_df[claims_df["district"] == district]
        
    if query:
        query = query.lower()
        # Search in claim_id or patient_id
        claims_df = claims_df[
            claims_df["claim_id"].str.lower().str.contains(query, na=False) | 
            claims_df["patient_id"].str.lower().str.contains(query, na=False)
        ]
        
    result = claims_df.sort_values(by="risk_score", ascending=False).head(limit)
    return result.to_dict(orient="records")


# ═══════════════════════════════════════════════════════════════════════════════
#  WEB3 AGENT ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

class AgentQueryRequest(BaseModel):
    query: str

class AgentQueryResponse(BaseModel):
    status: str
    query: str
    answer: str
    steps: int = 0
    error: str | None = None


@app.post("/agent/query", response_model=AgentQueryResponse)
async def agent_query(request: AgentQueryRequest):
    """
    Natural-language interface to the SurakshaNet Web3 fraud detection agent.

    The agent can:
    - Run the fraud pipeline and analyse results
    - Identify top risky hospitals and suspicious claims
    - Explain why a specific claim is flagged
    - Generate and anchor audit reports to Algorand blockchain
    - Query previously anchored blockchain transactions

    Example queries:
    - "Run the fraud pipeline and tell me the top 5 risky hospitals in Maharashtra"
    - "Explain why claim CLM_0000042 is suspicious"
    - "Generate a full audit report for Delhi and anchor it to the blockchain"
    - "How many suspicious claims are there in Hyderabad?"

    Requires GEMINI_API_KEY in environment variables.
    """
    if not os.getenv("GROQ_API_KEY"):
        from fastapi import HTTPException
        raise HTTPException(
            status_code=503,
            detail="GROQ_API_KEY not configured. Get a free key at https://console.groq.com/"
        )
    from fraud_detection_agent.agent.web3_agent import run_agent_query
    result = await run_agent_query(request.query)
    return AgentQueryResponse(
        status=result.get("status", "error"),
        query=result.get("query", request.query),
        answer=result.get("answer", ""),
        steps=result.get("steps", 0),
        error=result.get("error"),
    )


@app.get("/agent/status")
def agent_status():
    """Check if the Web3 agent is available (GROQ_API_KEY configured)."""
    has_key = bool(os.getenv("GROQ_API_KEY"))
    has_algo = bool(os.getenv("ALGORAND_MNEMONIC"))
    return {
        "agent_available": has_key,
        "blockchain_available": has_algo,
        "llm_model": "llama-3.3-70b-versatile via Groq (free tier)",
        "blockchain": "Algorand TestNet (algokit-utils)",
        "capabilities": [
            "fraud_pipeline",
            "hospital_risk_analysis",
            "claim_investigation",
            "audit_report_generation",
            "blockchain_anchoring",
        ],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fraud_detection_agent.main:app", host="0.0.0.0", port=8000, reload=True)
