import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_DIR = BASE_DIR / "database"
DB_PATH = DB_DIR / "claims.db"
CSV_PATH = DATA_DIR / "mock_claims.csv"


def generate_mock_claims(n_rows: int = 3000, random_state: int = 42) -> pd.DataFrame:
    """
    Generate a generalized mock healthcare claims dataset with injected fraud patterns.

    The generator simulates an Indian Ayushman Bharat setting with:
    - Indian states and districts
    - Government, private, teaching, and specialty hospitals
    - A mix of low-, medium-, and high-complexity procedures
    - Varying base costs by procedure complexity and hospital type
    """
    rng = np.random.default_rng(random_state)

    # More hospitals / patients / procedures for better variety
    hospital_ids = [f"HOSP_{i:03d}" for i in range(1, 81)]  # 80 hospitals
    patient_ids = [f"PAT_{i:06d}" for i in range(1, 6001)]  # 6000 patients
    procedure_codes = [f"PROC_{i:03d}" for i in range(1, 81)]  # 80 procedures

    # Representative Indian states and districts (not exhaustive but realistic)
    state_districts = {
        "Delhi": ["New Delhi", "South Delhi", "West Delhi"],
        "Maharashtra": ["Mumbai", "Pune", "Nagpur"],
        "Karnataka": ["Bengaluru Urban", "Mysuru", "Mangaluru"],
        "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai"],
        "Uttar Pradesh": ["Lucknow", "Varanasi", "Kanpur Nagar"],
        "Gujarat": ["Ahmedabad", "Surat", "Vadodara"],
        "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur"],
        "Telangana": ["Hyderabad", "Warangal", "Karimnagar"],
    }
    states = list(state_districts.keys())

    hospital_types = ["Government", "Private", "Teaching", "Trust"]

    # Construct a simple hospital master with fixed state/district/type and human-readable names
    base_names = [
        "Aarogya",
        "Swasthya",
        "Sanjivani",
        "Ashirwad",
        "Navjeevan",
        "Sanjeevan",
        "Ayushmaan",
        "Jan Arogya",
    ]
    suffixes = [
        "Hospital",
        "Multi Speciality Hospital",
        "Super Speciality Hospital",
        "Medical College",
        "Institute of Medical Sciences",
    ]

    hospital_rows = []
    for hid in hospital_ids:
        state = rng.choice(states)
        district = rng.choice(state_districts[state])
        htype = rng.choice(hospital_types, p=[0.35, 0.4, 0.15, 0.1])
        city_label = district.split()[0]
        name = f"{city_label} {rng.choice(base_names)} {rng.choice(suffixes)}"
        hospital_rows.append(
            {
                "hospital_id": hid,
                "hospital_name": name,
                "state": state,
                "district": district,
                "hospital_type": htype,
            }
        )
    hospital_master = pd.DataFrame(hospital_rows).set_index("hospital_id")

    # Map each procedure to a complexity bucket and base cost
    proc_df = pd.DataFrame({"procedure_code": procedure_codes})
    proc_df["complexity"] = pd.cut(
        proc_df.index,
        bins=[-1, 25, 55, 80],
        labels=["Low", "Medium", "High"],
    )
    complexity_base_cost = {"Low": 4000, "Medium": 8000, "High": 15000}

    start_date = datetime(2023, 1, 1)

    rows = []
    for claim_idx in range(1, n_rows + 1):
        hospital_id = rng.choice(hospital_ids)
        patient_id = rng.choice(patient_ids)
        procedure_code = rng.choice(procedure_codes)

        hmeta = hospital_master.loc[hospital_id]
        state = hmeta["state"]
        district = hmeta["district"]
        hospital_type = hmeta["hospital_type"]
        hospital_name = hmeta["hospital_name"]

        proc_info = proc_df.loc[proc_df["procedure_code"] == procedure_code].iloc[0]
        base_cost = float(complexity_base_cost[str(proc_info["complexity"])])

        # Adjust base cost by hospital type
        if hospital_type == "Private":
            base_cost *= 1.3
        elif hospital_type == "Teaching":
            base_cost *= 1.1
        elif hospital_type == "Trust":
            base_cost *= 1.15

        # Admission date within a 1.5-year window
        admission_offset = int(rng.integers(0, 540))
        admission_date = start_date + timedelta(days=admission_offset)

        # Length of stay correlates loosely with complexity
        if proc_info["complexity"] == "Low":
            los = int(max(1, rng.normal(2, 1)))
        elif proc_info["complexity"] == "Medium":
            los = int(max(1, rng.normal(4, 2)))
        else:
            los = int(max(1, rng.normal(7, 3)))
        discharge_date = admission_date + timedelta(days=los)

        # Claim amount around base_cost, scaled by length of stay
        claim_amount = max(
            1000,
            rng.normal(base_cost * (0.6 + 0.1 * los), base_cost * 0.25),
        )

        rows.append(
            {
                "claim_id": f"CLM_{claim_idx:07d}",
                "hospital_id": hospital_id,
                "hospital_name": hospital_name,
                "patient_id": patient_id,
                "procedure_code": procedure_code,
                "claim_amount": round(claim_amount, 2),
                "admission_date": admission_date.date().isoformat(),
                "discharge_date": discharge_date.date().isoformat(),
                "length_of_stay": los,
                "district": district,
                "state": state,
                "hospital_type": hospital_type,
            }
        )

    df = pd.DataFrame(rows)

    # Inject fraud patterns
    df = _inject_fraud_patterns(df, rng)
    return df


def _inject_fraud_patterns(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """
    Inject specific fraud patterns:
    - 300% billing spike for a subset of claims
    - Duplicate claims
    - Excessive high-cost procedures
    """
    df = df.copy()

    # 300%+ billing spike on ~8% of claims
    spike_idx = df.sample(frac=0.08, random_state=1).index
    df.loc[spike_idx, "claim_amount"] *= rng.uniform(3.0, 4.0)

    # Duplicate/near-duplicate claims (~5%)
    dup_sample = df.sample(frac=0.05, random_state=2)
    dup_rows = dup_sample.copy()
    dup_rows["claim_id"] = [f"DUP_{cid}" for cid in dup_rows["claim_id"]]
    df = pd.concat([df, dup_rows], ignore_index=True)

    # Excessive high-cost procedures: pick more procedure codes and strongly inflate them
    unique_procs = df["procedure_code"].unique()
    size = min(10, len(unique_procs))
    high_cost_procs = rng.choice(unique_procs, size=size, replace=False)
    high_cost_mask = df["procedure_code"].isin(high_cost_procs)
    df.loc[high_cost_mask, "claim_amount"] *= rng.uniform(2.0, 3.0)

    df["claim_amount"] = df["claim_amount"].round(2)
    return df


def ensure_directories() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DB_DIR.mkdir(parents=True, exist_ok=True)


def init_csv_and_db(
    n_rows: int = 3000,
    reuse_existing: bool = True,
) -> Tuple[pd.DataFrame, str]:
    """
    Ensure SQLite DB exists and has data. Returns the loaded DataFrame and DB path.
    """
    ensure_directories()
    
    db_exists = DB_PATH.exists()
    has_data = False
    
    if db_exists:
        try:
            conn = sqlite3.connect(DB_PATH)
            count = conn.execute("SELECT count(*) FROM claims").fetchone()[0]
            conn.close()
            if count > 0:
                has_data = True
        except Exception:
            has_data = False

    if not has_data or not reuse_existing:
        print(f"Generating new dataset ({n_rows} rows)...")
        df = generate_mock_claims(n_rows=n_rows)
        # Store in SQLite
        conn = sqlite3.connect(DB_PATH)
        df.to_sql("claims", conn, if_exists="replace", index=False)
        conn.close()
        # Also save CSV for backup/manual inspection if needed, but don't depend on it
        try:
            df.to_csv(CSV_PATH, index=False)
        except Exception:
            pass
    else:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM claims", conn)
        conn.close()

    return df, str(DB_PATH)


def init_auth_db() -> None:
    """
    Initialize the users table and seed the admin user.
    """
    ensure_directories()
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    # Seed admin user if it doesn't exist
    conn.execute("""
        INSERT OR IGNORE INTO users (username, password)
        VALUES ('ab1', '1234')
    """)
    conn.commit()
    conn.close()


def get_db_connection() -> sqlite3.Connection:
    """
    Return a new SQLite connection. Caller is responsible for closing it.
    """
    ensure_directories()
    init_auth_db()
    # If DB doesn't exist or is empty, initialize it
    db_exists = DB_PATH.exists()
    if not db_exists:
        init_csv_and_db()
    else:
        conn = sqlite3.connect(DB_PATH)
        try:
            count = conn.execute("SELECT count(*) FROM claims").fetchone()[0]
            if count == 0:
                conn.close()
                init_csv_and_db()
            else:
                conn.close()
        except Exception:
            conn.close()
            init_csv_and_db()
            
    return sqlite3.connect(DB_PATH)

