from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Optional

import pandas as pd

from fraud_detection_agent.database.db_setup import DB_PATH, ensure_directories


SNAPSHOT_TABLE = "risk_snapshots"


def _get_conn() -> sqlite3.Connection:
    ensure_directories()
    return sqlite3.connect(DB_PATH)


def ensure_snapshot_table() -> None:
    """
    Create snapshot table if missing.
    """
    conn = _get_conn()
    try:
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {SNAPSHOT_TABLE} (
                snapshot_ts TEXT NOT NULL,
                hospital_id TEXT NOT NULL,
                hospital_name TEXT,
                hospital_type TEXT,
                state TEXT,
                district TEXT,
                total_claims INTEGER,
                avg_risk_score REAL,
                risk_category_overall TEXT,
                high_risk_claims INTEGER,
                suspicious_claims INTEGER,
                any_rule_flags INTEGER
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def persist_hospital_snapshot(
    hospital_risk_df: pd.DataFrame,
    snapshot_ts: Optional[str] = None,
) -> str:
    """
    Persist a hospital-level risk snapshot into SQLite for time-series monitoring.
    """
    ensure_snapshot_table()
    ts = snapshot_ts or datetime.now().isoformat(timespec="seconds")

    cols = [
        "hospital_id",
        "hospital_name",
        "hospital_type",
        "state",
        "district",
        "total_claims",
        "avg_risk_score",
        "risk_category_overall",
        "high_risk_claims",
        "suspicious_claims",
        "any_rule_flags",
    ]
    df = hospital_risk_df.copy()
    for c in cols:
        if c not in df.columns:
            df[c] = None

    df = df[cols]
    df.insert(0, "snapshot_ts", ts)

    conn = _get_conn()
    try:
        df.to_sql(SNAPSHOT_TABLE, conn, if_exists="append", index=False)
    finally:
        conn.close()
    return ts


def load_snapshots(
    hospital_type_focus: str = "Private",
    limit: int = 5000,
) -> pd.DataFrame:
    """
    Load recent risk snapshots, filtered to a hospital type (default: Private).
    """
    ensure_snapshot_table()
    conn = _get_conn()
    try:
        query = f"""
        SELECT *
        FROM {SNAPSHOT_TABLE}
        WHERE hospital_type = ?
        ORDER BY snapshot_ts DESC
        LIMIT ?
        """
        df = pd.read_sql_query(query, conn, params=[hospital_type_focus, limit])
    finally:
        conn.close()
    return df

