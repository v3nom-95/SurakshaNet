from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from fraud_detection_agent.database.db_setup import get_db_connection


TARGET_FEATURE_COLUMNS = [
    "claim_amount_norm",
    "length_of_stay",
    "avg_claim_per_hospital",
    "claim_frequency_per_month",
    "procedure_cost_deviation",
    "patient_repeat_ratio",
]


@dataclass
class FeatureData:
    features: pd.DataFrame
    enriched: pd.DataFrame
    scaler_claim_amount: MinMaxScaler


def load_claims_from_db() -> pd.DataFrame:
    """
    Load raw claims table from SQLite.
    """
    conn = get_db_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM claims", conn)
    finally:
        conn.close()
    return df


def _normalize_claim_amount(df: pd.DataFrame) -> Tuple[pd.DataFrame, MinMaxScaler]:
    df = df.copy()
    scaler = MinMaxScaler()
    df["claim_amount_norm"] = scaler.fit_transform(df[["claim_amount"]])
    return df, scaler


def _add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Ensure datetime for grouping
    df["admission_date"] = pd.to_datetime(df["admission_date"])
    df["month"] = df["admission_date"].dt.to_period("M").astype(str)

    # Average claim per hospital
    hospital_avg = df.groupby("hospital_id")["claim_amount"].mean().rename("avg_claim_per_hospital")
    df = df.merge(hospital_avg, on="hospital_id", how="left")

    # Claim frequency per hospital per month
    freq = (
        df.groupby(["hospital_id", "month"])["claim_id"]
        .count()
        .rename("claim_frequency_per_month")
        .reset_index()
    )
    df = df.merge(freq, on=["hospital_id", "month"], how="left")

    # Procedure cost deviation against district average for that procedure
    proc_district_avg = (
        df.groupby(["district", "procedure_code"])["claim_amount"]
        .mean()
        .rename("district_proc_avg_cost")
        .reset_index()
    )
    df = df.merge(proc_district_avg, on=["district", "procedure_code"], how="left")
    df["procedure_cost_deviation"] = df["claim_amount"] - df["district_proc_avg_cost"]

    # Patient repeat ratio: claims for a patient within hospital-month
    patient_counts = (
        df.groupby(["hospital_id", "month", "patient_id"])["claim_id"]
        .count()
        .rename("patient_claim_count_hosp_month")
        .reset_index()
    )
    df = df.merge(
        patient_counts,
        on=["hospital_id", "month", "patient_id"],
        how="left",
    )

    hosp_month_counts = (
        df.groupby(["hospital_id", "month"])["claim_id"]
        .count()
        .rename("hosp_month_total_claims")
        .reset_index()
    )
    df = df.merge(hosp_month_counts, on=["hospital_id", "month"], how="left")

    df["patient_repeat_ratio"] = (
        df["patient_claim_count_hosp_month"] / df["hosp_month_total_claims"].clip(lower=1)
    )

    return df


def build_features_from_db() -> FeatureData:
    """
    Load claims from DB and construct feature matrix with engineered features.
    """
    df_raw = load_claims_from_db()
    df_raw["claim_amount"] = df_raw["claim_amount"].astype(float)

    df_norm, scaler_claim_amount = _normalize_claim_amount(df_raw)
    df_enriched = _add_derived_features(df_norm)

    # Ensure required columns exist
    missing = [c for c in TARGET_FEATURE_COLUMNS if c not in df_enriched.columns]
    if missing:
        raise ValueError(f"Missing engineered feature columns: {missing}")

    features = df_enriched[TARGET_FEATURE_COLUMNS].fillna(0.0)

    return FeatureData(
        features=features,
        enriched=df_enriched,
        scaler_claim_amount=scaler_claim_amount,
    )

