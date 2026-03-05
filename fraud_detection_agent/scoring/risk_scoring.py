from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


@dataclass
class RiskConfig:
    w_anomaly: float = 0.5
    w_proc_dev: float = 0.3
    w_claim_freq: float = 0.2


def _scale_series(series: pd.Series) -> pd.Series:
    scaler = MinMaxScaler()
    reshaped = series.fillna(0.0).to_numpy(dtype=float).reshape(-1, 1)
    if reshaped.shape[0] <= 1:
        return pd.Series(np.zeros_like(reshaped.squeeze()), index=series.index)
    scaled = scaler.fit_transform(reshaped).squeeze()
    return pd.Series(scaled, index=series.index)


def compute_risk_scores(
    df: pd.DataFrame,
    anomaly_scores: np.ndarray,
    config: RiskConfig | None = None,
) -> pd.DataFrame:
    """
    Compute per-claim risk score and category based on anomaly scores and engineered features.
    """
    if config is None:
        config = RiskConfig()

    df = df.copy()
    df["anomaly_score"] = anomaly_scores

    df["anomaly_score_scaled"] = _scale_series(df["anomaly_score"])
    df["procedure_cost_deviation_scaled"] = _scale_series(df["procedure_cost_deviation"])
    df["claim_frequency_scaled"] = _scale_series(df["claim_frequency_per_month"])

    df["risk_score_raw"] = (
        config.w_anomaly * df["anomaly_score_scaled"]
        + config.w_proc_dev * df["procedure_cost_deviation_scaled"]
        + config.w_claim_freq * df["claim_frequency_scaled"]
    )

    # Non-linear scaling to push clearly anomalous cases higher, closer to real-world audit needs
    df["risk_score"] = (df["risk_score_raw"].clip(0, 1) ** 0.7 * 100).clip(0, 100)

    # Derive per-claim risk bands from the empirical distribution so that
    # Low / Medium / High are always represented in a realistic proportion.
    scores = df["risk_score"].fillna(0.0)
    if len(df) >= 3 and scores.max() > 0:
        q_low = scores.quantile(0.5)   # ~50% Low
        q_med = scores.quantile(0.85)  # ~35% Medium, ~15% High

        def categorize(score: float) -> str:
            if score <= q_low:
                return "Low"
            if score <= q_med:
                return "Medium"
            return "High"

        df["risk_category"] = scores.apply(categorize)
    else:
        df["risk_category"] = "Low"

    return df


def apply_rule_based_flags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply rule-based fraud detection flags:
    - Up-coding: procedure cost > 2x district average
    - Ghost billing: same patient repeated > 3 times/month in same hospital
    - Claim surge: hospital monthly claims spike > ~150% vs hospital's average monthly volume
    """
    df = df.copy()

    # Up-coding
    df["rule_upcoding"] = (
        df["claim_amount"]
        > 2.0 * df["district_proc_avg_cost"].replace(0, np.nan).fillna(df["district_proc_avg_cost"])
    )

    # Ghost billing: patient_claim_count_hosp_month > 3 (tighter, more realistic threshold)
    df["rule_ghost_billing"] = df["patient_claim_count_hosp_month"] > 3

    # Claim surge: hospital monthly claims vs hospital average monthly
    hosp_month = (
        df.groupby(["hospital_id", "month"])["claim_id"]
        .count()
        .rename("claims_in_month")
        .reset_index()
    )
    hosp_avg = (
        hosp_month.groupby("hospital_id")["claims_in_month"]
        .mean()
        .rename("hosp_avg_monthly_claims")
        .reset_index()
    )
    hosp_month = hosp_month.merge(hosp_avg, on="hospital_id", how="left")
    hosp_month["rule_claim_surge"] = (
        hosp_month["claims_in_month"]
        > hosp_month["hosp_avg_monthly_claims"].fillna(0) * 2.5
    )  # > 150% spike => >2.5x

    df = df.merge(
        hosp_month[["hospital_id", "month", "rule_claim_surge"]],
        on=["hospital_id", "month"],
        how="left",
    )

    # Consolidated flag
    df["any_rule_flag"] = (
        df["rule_upcoding"] | df["rule_ghost_billing"] | df["rule_claim_surge"]
    )

    return df


def aggregate_hospital_risk(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate claim-level risk to hospital level for dashboard and reports.
    """
    agg = (
        df.groupby(["hospital_id", "hospital_name", "state", "district", "hospital_type"])
        .agg(
            total_claims=("claim_id", "count"),
            avg_risk_score=("risk_score", "mean"),
            high_risk_claims=("risk_category", lambda s: (s == "High").sum()),
            suspicious_claims=("anomaly_label", lambda s: (s == 1).sum()),
            any_rule_flags=("any_rule_flag", "sum"),
        )
        .reset_index()
    )

    # Incorporate rule flags into the categorization logic
    # Each rule flag adds to the final audit priority score
    agg["audit_priority_score"] = (
        agg["avg_risk_score"] + (agg["any_rule_flags"] / agg["total_claims"]) * 100
    ).clip(0, 100)

    scores = agg["audit_priority_score"].fillna(0.0)
    if len(agg) >= 3 and scores.max() > 0:
        q_low = scores.quantile(0.5)
        q_med = scores.quantile(0.8)  # Lowered to 0.8 to ensure more 'High' visibility

        def categorize_hospital(score: float) -> str:
            if score <= q_low:
                return "Low"
            if score <= q_med:
                return "Medium"
            return "High"

        agg["risk_category_overall"] = scores.apply(categorize_hospital)
    else:
        agg["risk_category_overall"] = "Low"

    return agg

