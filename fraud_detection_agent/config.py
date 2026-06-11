"""
Central config for environment-aware settings.
All paths and tunable parameters live here.
"""
import os
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
# On Render a persistent disk is mounted at /data.
# Locally we fall back to the repo's database/ + data/ directories.
_RENDER_DATA_DIR = Path("/data")
_LOCAL_BASE = Path(__file__).resolve().parent

if _RENDER_DATA_DIR.exists():
    DB_DIR = _RENDER_DATA_DIR
    DATA_DIR = _RENDER_DATA_DIR
else:
    DB_DIR = _LOCAL_BASE / "database"
    DATA_DIR = _LOCAL_BASE / "data"

DB_PATH = DB_DIR / "claims.db"
CSV_PATH = DATA_DIR / "mock_claims.csv"

# ── ML tuning ────────────────────────────────────────────────────────────────
CONTAMINATION_RATE: float = float(os.getenv("CONTAMINATION_RATE", "0.10"))
ANOMALY_THRESHOLD: float = float(os.getenv("ANOMALY_THRESHOLD", "0.70"))
DATASET_SIZE: int = int(os.getenv("DATASET_SIZE", "30000"))

# ── CORS ─────────────────────────────────────────────────────────────────────
# Set ALLOWED_ORIGINS to your Render frontend URL in production.
# Multiple origins can be separated by commas.
_origins_env = os.getenv("ALLOWED_ORIGINS", "*")
ALLOWED_ORIGINS: list[str] = (
    ["*"] if _origins_env == "*" else [o.strip() for o in _origins_env.split(",")]
)
