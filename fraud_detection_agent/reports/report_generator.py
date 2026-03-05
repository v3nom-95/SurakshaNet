from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Tuple

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
REPORT_DIR = BASE_DIR / "reports"


def ensure_report_dir() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)


def generate_fraud_report(
    hospital_risk_df: pd.DataFrame,
    claims_df: pd.DataFrame,
    top_n: int = 5,
) -> Tuple[str, str]:
    """
    Generate a structured text fraud report and save it to disk.

    Returns (report_text, report_path).
    """
    ensure_report_dir()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = REPORT_DIR / f"fraud_report_{timestamp}.txt"

    # Top N risky hospitals
    top_risky = hospital_risk_df.sort_values(
        by="avg_risk_score", ascending=False
    ).head(top_n)

    total_claims = len(claims_df)
    suspicious_claims = int((claims_df["anomaly_label"] == 1).sum())
    rule_flagged = int(claims_df["any_rule_flag"].sum())

    lines: list[str] = []
    lines.append("Ayushman Bharat Fraud Detection Report")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Generated at: {datetime.now().isoformat(timespec='seconds')}")
    lines.append("")
    lines.append("Summary")
    lines.append("-" * 60)
    lines.append(f"Total claims analysed       : {total_claims}")
    lines.append(f"Suspicious (ML) claims      : {suspicious_claims}")
    lines.append(f"Rule-flagged claims         : {rule_flagged}")
    lines.append("")

    lines.append(f"Top {top_n} Risky Hospitals (by average risk score)")
    lines.append("-" * 60)
    for _, row in top_risky.iterrows():
        lines.append(
            f"{row['hospital_name']} ({row['hospital_id']}) | State: {row['state']} | District: {row['district']} | Type: {row['hospital_type']} | "
            f"Avg Risk: {row['avg_risk_score']:.2f} | Total Claims: {row['total_claims']} | "
            f"High-risk claims: {int(row['high_risk_claims'])} | Rule flags: {int(row['any_rule_flags'])}"
        )
    lines.append("")

    lines.append("Detected Anomaly Types")
    lines.append("-" * 60)
    lines.append("- Machine-learning-based anomalies (Isolation Forest & Local Outlier Factor).")
    lines.append("- Up-coding: claim amounts significantly higher than district-procedure averages.")
    lines.append("- Ghost billing: patients with unusually high repeat claims in a month.")
    lines.append("- Claim surge: hospitals with abrupt spikes in monthly claim volume.")
    lines.append("")

    lines.append("Suggested Audit Priorities")
    lines.append("-" * 60)
    for _, row in top_risky.iterrows():
        priority = "High" if row["risk_category_overall"] == "High" else "Medium"
        lines.append(
            f"{row['hospital_name']} ({row['hospital_id']}) [{row['state']} - {row['district']}, {row['hospital_type']}]: "
            f"{priority} audit priority."
        )
    lines.append("")

    # Risk score distribution summary
    lines.append("Risk Score Distribution")
    lines.append("-" * 60)
    dist = hospital_risk_df["risk_category_overall"].value_counts().to_dict()
    for cat in ["Low", "Medium", "High"]:
        lines.append(f"{cat:6}: {dist.get(cat, 0)} hospitals")

    report_text = "\n".join(lines)
    report_path.write_text(report_text, encoding="utf-8")
    return report_text, str(report_path)

