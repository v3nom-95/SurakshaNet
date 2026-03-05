Ayushman Bharat Fraud Detection Agent - Stage 1 (AyushGuard)
==========================================================

This project implements an advanced end-to-end fraud detection agent for Ayushman Bharat claims.

It includes:
- Mock claims data generation and SQLite storage
- Preprocessing and feature engineering
- Unsupervised anomaly detection (Isolation Forest + Local Outlier Factor)
- Risk scoring and rule-based fraud pattern detection
- FastAPI backend with optimized caching
- Next.js 15+ Advanced Dashboard with Recharts and Lucide icons

Project layout
--------------

`fraud_detection_agent/`
- `database/db_setup.py` – mock data generator and SQLite ingestion
- `preprocessing/preprocess.py` – feature engineering
- `models/anomaly_model.py` – anomaly detectors
- `scoring/risk_scoring.py` – risk scoring and rule-based checks
- `reports/report_generator.py` – AI fraud report generator
- `main.py` – FastAPI application and pipeline orchestration

`frontend/`
- Next.js application with glassmorphism UI and advanced analytics dashboard.

Setup
-----

### 1. Backend Setup
1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the FastAPI server:
   ```bash
   python -m fraud_detection_agent.main
   ```
   The API will be available at `http://localhost:8000`.

### 2. Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
   The dashboard will be available at `http://localhost:3000`.

Features
--------
- **ML Anomaly Detection**: Uses Isolation Forest and LOF to detect outliers in claim amounts and frequencies.
- **Rule-Based Flags**: Detects up-coding, ghost billing, and claim surges using custom heuristics.
- **Glassmorphism UI**: High-end modern dashboard with real-time monitoring indicators.
- **Automated Reporting**: Generates human-readable audit priorities for risky hospitals.
